"""
Conversation Engine using LangGraph.

Orchestrates conversational flow with state management, checkpoints,
and conditional routing based on user intent.
"""

from typing import TypedDict, Annotated, Literal
import operator
from datetime import datetime
import logging

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ..models.session import SessionData, SessionState
from ..services.nlp_service import NLPService, NLPResult, Intent
from ..services.guardrails import GuardrailsService

logger = logging.getLogger(__name__)


class ConversationState(TypedDict):
    """
    Estado do grafo conversacional (LangGraph).
    
    Mantém o estado da conversa através dos nós do grafo,
    incluindo mensagens, sessão, resultado NLP e resposta.
    """
    
    # Lista de mensagens (acumulativa)
    messages: Annotated[list, operator.add]
    
    # Sessão atual
    session: SessionData
    
    # Resultado do processamento NLP
    nlp_result: NLPResult
    
    # Resposta gerada
    response: str
    
    # Próxima ação (para controle de fluxo)
    next_action: str
    
    # Flag para indicar se precisa de handoff
    needs_handoff: bool
    
    # Contador de falhas consecutivas
    consecutive_failures: int


class ConversationEngine:
    """
    Engine conversacional usando LangGraph.
    
    Orquestra o fluxo de conversa através de um grafo de estados,
    com nós para cada tipo de interação e edges condicionais baseados
    na intenção identificada pelo NLP.
    """
    
    def __init__(self, nlp_service: NLPService, guardrails_service: GuardrailsService):
        """
        Inicializa o Conversation Engine.
        
        Args:
            nlp_service: Serviço de processamento de linguagem natural
            guardrails_service: Serviço de guardrails para validação de respostas
        """
        self.nlp = nlp_service
        self.guardrails = guardrails_service
        
        # Criar checkpoint saver para recuperação de contexto
        self.checkpointer = MemorySaver()
        
        # Construir grafo de estados
        self.graph = self._build_graph()
        
        logger.info("Conversation Engine initialized with LangGraph")
    
    def _build_graph(self) -> StateGraph:
        """
        Constrói o grafo de estados conversacionais.
        
        Define nós para cada tipo de interação e edges condicionais
        baseados na intenção identificada.
        
        Returns:
            StateGraph compilado com checkpoints
        """
        # Criar grafo
        workflow = StateGraph(ConversationState)
        
        # Adicionar nós
        workflow.add_node("process_nlp", self._process_nlp)
        workflow.add_node("handle_greeting", self._handle_greeting)
        workflow.add_node("collect_profile", self._collect_profile)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("show_car_details", self._show_car_details)
        workflow.add_node("compare_cars", self._compare_cars)
        workflow.add_node("human_handoff", self._human_handoff)
        workflow.add_node("apply_guardrails", self._apply_guardrails)
        
        # Definir ponto de entrada
        workflow.set_entry_point("process_nlp")
        
        # Adicionar edges condicionais baseados em intenção
        workflow.add_conditional_edges(
            "process_nlp",
            self._route_by_intent,
            {
                "greeting": "handle_greeting",
                "collect_profile": "collect_profile",
                "generate_recommendations": "generate_recommendations",
                "show_car_details": "show_car_details",
                "compare_cars": "compare_cars",
                "human_handoff": "human_handoff",
            }
        )
        
        # Todos os nós de resposta passam por guardrails antes de finalizar
        response_nodes = [
            "handle_greeting",
            "collect_profile",
            "generate_recommendations",
            "show_car_details",
            "compare_cars",
            "human_handoff"
        ]
        
        for node in response_nodes:
            workflow.add_edge(node, "apply_guardrails")
        
        # Guardrails finaliza o fluxo
        workflow.add_edge("apply_guardrails", END)
        
        # Compilar com checkpointer para recuperação
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _route_by_intent(self, state: ConversationState) -> str:
        """
        Roteia para o handler apropriado baseado na intenção.
        
        Args:
            state: Estado atual da conversa
            
        Returns:
            Nome do próximo nó a executar
        """
        intent = state["nlp_result"].intent
        session_state = state["session"].state
        
        # Se precisa de handoff, sempre vai para human_handoff
        if state.get("needs_handoff", False):
            return "human_handoff"
        
        # Mapeamento de intenções para nós
        intent_routing = {
            Intent.GREETING: "greeting",
            Intent.HUMAN_HANDOFF: "human_handoff",
            Intent.CAR_DETAILS: "show_car_details",
            Intent.COMPARE_CARS: "compare_cars",
        }
        
        # Se tem roteamento direto, usar
        if intent in intent_routing:
            return intent_routing[intent]
        
        # Caso contrário, rotear baseado no estado da sessão
        if session_state == SessionState.GREETING:
            return "greeting"
        elif session_state == SessionState.COLLECTING_PROFILE:
            return "collect_profile"
        elif session_state in [
            SessionState.GENERATING_RECOMMENDATIONS,
            SessionState.SHOWING_RECOMMENDATIONS
        ]:
            # Se tem intenção de recomendação, gerar
            if intent in [Intent.CAR_RECOMMENDATION, Intent.BUDGET_INQUIRY]:
                return "generate_recommendations"
            # Senão, continuar coletando perfil
            return "collect_profile"
        elif session_state == SessionState.CAR_DETAILS:
            return "show_car_details"
        elif session_state == SessionState.COMPARING_CARS:
            return "compare_cars"
        
        # Default: coletar perfil
        return "collect_profile"
    
    async def _process_nlp(self, state: ConversationState) -> ConversationState:
        """
        Processa NLP da mensagem (já feito antes, apenas valida).
        
        Args:
            state: Estado atual
            
        Returns:
            Estado atualizado
        """
        # NLP já foi processado antes de entrar no grafo
        # Este nó apenas valida e passa adiante
        logger.debug(
            f"Processing NLP: intent={state['nlp_result'].intent.value}, "
            f"confidence={state['nlp_result'].confidence:.2f}"
        )
        return state
    
    async def _handle_greeting(self, state: ConversationState) -> ConversationState:
        """
        Handler para saudações iniciais.
        
        Args:
            state: Estado atual
            
        Returns:
            Estado com resposta de boas-vindas
        """
        session = state["session"]
        
        # Verificar se é primeira interação
        if session.turn_id == 0:
            # Primeira vez - solicitar consentimento LGPD
            state["response"] = (
                "Olá! 👋 Bem-vindo ao *FacilIAuto*!\n\n"
                "Sou seu assistente virtual e vou te ajudar a encontrar o carro ideal "
                "para você.\n\n"
                "Antes de começarmos, preciso do seu consentimento para processar seus dados "
                "conforme a LGPD. Seus dados serão usados apenas para recomendações de veículos "
                "e não serão compartilhados sem sua autorização.\n\n"
                "Você concorda? (Sim/Não)"
            )
        elif not session.consent_given:
            # Aguardando consentimento
            user_message = state["messages"][-1]["content"].lower()
            
            if any(word in user_message for word in ["sim", "aceito", "concordo", "ok"]):
                session.give_consent()
                state["response"] = (
                    "Perfeito! ✅ Obrigado pelo consentimento.\n\n"
                    "Agora vamos começar! Para te ajudar melhor, "
                    "me conta: *qual é o seu orçamento aproximado* para o carro?"
                )
                session.state = SessionState.COLLECTING_PROFILE
            else:
                state["response"] = (
                    "Entendo. Infelizmente, preciso do seu consentimento para continuar. "
                    "Se mudar de ideia, é só me chamar! 😊"
                )
        else:
            # Já tem consentimento - saudação normal
            state["response"] = (
                "Olá novamente! 👋\n\n"
                "Como posso te ajudar hoje?"
            )
        
        state["session"] = session
        return state

    
    async def _collect_profile(self, state: ConversationState) -> ConversationState:
        """
        Coleta informações do perfil do usuário.
        
        Extrai entidades da mensagem e faz perguntas de esclarecimento
        até ter informações suficientes para gerar recomendações.
        
        Args:
            state: Estado atual
            
        Returns:
            Estado com próxima pergunta ou transição para recomendações
        """
        session = state["session"]
        profile = session.user_profile
        nlp_result = state["nlp_result"]
        
        # Extrair entidades da mensagem
        for entity in nlp_result.entities:
            if entity.type == "budget":
                # Atualizar orçamento
                try:
                    budget_value = float(entity.value)
                    if not profile.orcamento_min:
                        profile.orcamento_min = budget_value * 0.8
                        profile.orcamento_max = budget_value * 1.2
                        logger.info(f"Budget set: {budget_value}")
                except ValueError:
                    logger.warning(f"Invalid budget value: {entity.value}")
            
            elif entity.type == "location":
                # Atualizar localização
                location = entity.value.lower()
                # Mapear para cidade/estado (simplificado)
                if not profile.city:
                    profile.city = location
                    logger.info(f"Location set: {location}")
            
            elif entity.type == "preference":
                # Adicionar preferência
                pref = entity.value.lower()
                if pref not in profile.prioridades:
                    profile.prioridades[pref] = len(profile.prioridades) + 1
                    logger.info(f"Preference added: {pref}")
            
            elif entity.type == "brand":
                # Adicionar marca preferida
                brand = entity.value.lower()
                if brand not in profile.marcas_preferidas:
                    profile.marcas_preferidas.append(brand)
                    logger.info(f"Brand preference added: {brand}")
            
            elif entity.type == "category":
                # Adicionar tipo preferido
                category = entity.value.lower()
                if category not in profile.tipos_preferidos:
                    profile.tipos_preferidos.append(category)
                    logger.info(f"Category preference added: {category}")
        
        # Detectar uso principal da mensagem
        if not profile.uso_principal:
            message = state["messages"][-1]["content"].lower()
            uso_keywords = {
                "trabalho": ["trabalho", "trabalhar", "emprego", "escritório"],
                "família": ["família", "familia", "filhos", "crianças", "criancas"],
                "lazer": ["lazer", "passeio", "viagem", "viajar", "turismo"],
                "cidade": ["cidade", "urbano", "trânsito", "transito"],
                "estrada": ["estrada", "rodovia", "viagem longa"],
            }
            
            for uso, keywords in uso_keywords.items():
                if any(kw in message for kw in keywords):
                    profile.uso_principal = uso
                    logger.info(f"Usage detected: {uso}")
                    break
        
        # Determinar próxima pergunta baseado na completude
        completeness = profile.completeness
        
        if not profile.orcamento_min:
            state["response"] = (
                "Para começar, preciso saber: *qual é o seu orçamento aproximado* "
                "para o carro?\n\n"
                "Pode ser uma faixa de valores, por exemplo: 'entre 50 e 70 mil'"
            )
        elif not profile.uso_principal:
            state["response"] = (
                "Entendi! 💰\n\n"
                "Agora me conta: *como você pretende usar o carro?*\n\n"
                "Por exemplo:\n"
                "• Trabalho diário\n"
                "• Uso com a família\n"
                "• Lazer e viagens\n"
                "• Cidade ou estrada"
            )
        elif not profile.city:
            state["response"] = (
                "Ótimo! 🚗\n\n"
                "*Em qual cidade você está procurando?*\n\n"
                "Isso me ajuda a encontrar as melhores ofertas perto de você."
            )
        elif len(profile.prioridades) < 3:
            state["response"] = (
                "Perfeito! 📍\n\n"
                "Para finalizar, me diga: *quais são suas 3 principais prioridades?*\n\n"
                "Escolha entre:\n"
                "1️⃣ Economia de combustível\n"
                "2️⃣ Espaço interno\n"
                "3️⃣ Performance e potência\n"
                "4️⃣ Conforto\n"
                "5️⃣ Segurança\n"
                "6️⃣ Tecnologia\n\n"
                "Pode me dizer os números ou escrever as prioridades."
            )
        else:
            # Perfil completo! Gerar recomendações
            state["response"] = (
                "Excelente! ✅ Já tenho todas as informações necessárias.\n\n"
                f"📊 *Seu perfil:*\n"
                f"💰 Orçamento: R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}\n"
                f"🎯 Uso: {profile.uso_principal}\n"
                f"📍 Localização: {profile.city}\n"
                f"⭐ Prioridades: {', '.join(profile.prioridades.keys())}\n\n"
                "Deixa eu buscar os *melhores carros* para você... 🔍"
            )
            session.state = SessionState.GENERATING_RECOMMENDATIONS
            state["next_action"] = "generate_recommendations"
        
        session.user_profile = profile
        state["session"] = session
        
        logger.info(f"Profile completeness: {completeness:.2%}")
        return state
    
    async def _generate_recommendations(self, state: ConversationState) -> ConversationState:
        """
        Gera recomendações de veículos usando o backend.
        
        Args:
            state: Estado atual
            
        Returns:
            Estado com recomendações formatadas
        """
        session = state["session"]
        profile = session.user_profile
        
        # TODO: Integrar com BackendClient (Task 7)
        # Por enquanto, retornar mensagem placeholder
        state["response"] = (
            "🎯 *Encontrei ótimas opções para você!*\n\n"
            "_[Integração com backend será implementada na Task 7]_\n\n"
            "As recomendações serão baseadas no seu perfil:\n"
            f"• Orçamento: R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}\n"
            f"• Uso: {profile.uso_principal}\n"
            f"• Prioridades: {', '.join(profile.prioridades.keys())}\n\n"
            "Digite o número do carro para ver mais detalhes ou 'mais opções' "
            "para ver outros carros."
        )
        
        session.state = SessionState.SHOWING_RECOMMENDATIONS
        state["session"] = session
        
        logger.info("Recommendations generated (placeholder)")
        return state
    
    async def _show_car_details(self, state: ConversationState) -> ConversationState:
        """
        Mostra detalhes de um carro específico.
        
        Args:
            state: Estado atual
            
        Returns:
            Estado com detalhes do carro
        """
        session = state["session"]
        
        # TODO: Implementar busca de detalhes do carro (Task 7)
        state["response"] = (
            "🚗 *Detalhes do Carro*\n\n"
            "_[Detalhes serão implementados na Task 7]_\n\n"
            "Aqui você verá:\n"
            "• Especificações técnicas completas\n"
            "• Itens de série\n"
            "• Fotos adicionais\n"
            "• Localização da concessionária\n"
            "• Opções de financiamento\n\n"
            "Gostaria de:\n"
            "• Ver outros carros\n"
            "• Comparar com outro modelo\n"
            "• Agendar test-drive\n"
            "• Falar com vendedor"
        )
        
        session.state = SessionState.CAR_DETAILS
        state["session"] = session
        
        return state
    
    async def _compare_cars(self, state: ConversationState) -> ConversationState:
        """
        Compara múltiplos carros lado a lado.
        
        Args:
            state: Estado atual
            
        Returns:
            Estado com comparação de carros
        """
        session = state["session"]
        
        # TODO: Implementar comparação de carros (Task 7)
        state["response"] = (
            "⚖️ *Comparação de Carros*\n\n"
            "_[Comparação será implementada na Task 7]_\n\n"
            "Aqui você verá uma tabela comparativa com:\n"
            "• Preço\n"
            "• Consumo\n"
            "• Potência\n"
            "• Espaço interno\n"
            "• Itens de segurança\n"
            "• Tecnologia embarcada\n\n"
            "Qual carro te interessou mais?"
        )
        
        session.state = SessionState.COMPARING_CARS
        state["session"] = session
        
        return state
    
    async def _human_handoff(self, state: ConversationState) -> ConversationState:
        """
        Transfere para atendimento humano.
        
        Args:
            state: Estado atual
            
        Returns:
            Estado com mensagem de transferência
        """
        session = state["session"]
        
        state["response"] = (
            "👤 *Transferindo para atendimento humano*\n\n"
            "Entendi que você gostaria de falar com um de nossos especialistas.\n\n"
            "Um atendente entrará em contato com você em breve!\n\n"
            "Enquanto isso, posso te ajudar com mais alguma coisa?"
        )
        
        session.state = SessionState.HUMAN_HANDOFF
        state["session"] = session
        
        # TODO: Notificar equipe de atendimento via Celery (Task 9)
        logger.info(f"Human handoff requested for session {session.session_id}")
        
        return state
    
    async def _apply_guardrails(self, state: ConversationState) -> ConversationState:
        """
        Aplica guardrails para evitar respostas duplicadas.
        
        Verifica se a resposta já foi enviada recentemente e,
        se necessário, reformula para evitar repetição.
        
        Args:
            state: Estado atual
            
        Returns:
            Estado com resposta validada
        """
        response = state["response"]
        session = state["session"]
        
        # Verificar se resposta está vazia
        if not response or response.strip() == "":
            state["response"] = (
                "Desculpe, não entendi muito bem. 🤔\n\n"
                "Pode reformular sua pergunta?"
            )
            state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
            
            # Se falhou 3 vezes, oferecer handoff
            if state["consecutive_failures"] >= 3:
                state["needs_handoff"] = True
                state["response"] += (
                    "\n\nParece que estou tendo dificuldade em te ajudar. "
                    "Gostaria de falar com um atendente humano?"
                )
        else:
            # Reset contador de falhas
            state["consecutive_failures"] = 0
            
            # Aplicar guardrails completos
            validated_response, metadata = self.guardrails.validate_response(
                response,
                session
            )
            
            state["response"] = validated_response
            
            # Log metadata
            if metadata.get("is_duplicate"):
                logger.warning("Duplicate response detected and reformulated")
            if metadata.get("style_violations"):
                logger.warning(f"Style violations: {metadata['style_violations']}")
        
        logger.debug(
            f"Guardrails applied, response length: {len(state['response'])}, "
            f"original: {metadata.get('original_length', 0) if response else 0}"
        )
        return state

    
    async def process_message(
        self,
        session: SessionData,
        message: str,
        nlp_result: NLPResult
    ) -> tuple[str, SessionData]:
        """
        Processa mensagem do usuário e gera resposta.
        
        Este é o método principal que orquestra todo o fluxo conversacional
        através do grafo LangGraph.
        
        Args:
            session: Sessão atual do usuário
            message: Mensagem do usuário
            nlp_result: Resultado do processamento NLP
            
        Returns:
            Tupla (resposta, sessão_atualizada)
        """
        try:
            # Criar estado inicial
            initial_state: ConversationState = {
                "messages": [{"role": "user", "content": message}],
                "session": session,
                "nlp_result": nlp_result,
                "response": "",
                "next_action": "",
                "needs_handoff": False,
                "consecutive_failures": 0,
            }
            
            # Configuração do checkpoint (para recuperação)
            config = {
                "configurable": {
                    "thread_id": session.session_id,
                    "checkpoint_ns": "conversation"
                }
            }
            
            # Executar grafo
            logger.info(
                f"Processing message for session {session.session_id}, "
                f"intent: {nlp_result.intent.value}"
            )
            
            final_state = await self.graph.ainvoke(initial_state, config)
            
            # Extrair resposta e sessão atualizada
            response = final_state["response"]
            updated_session = final_state["session"]
            
            # Adicionar mensagens à memória da sessão
            updated_session.add_message("user", message)
            updated_session.add_message("assistant", response)
            
            logger.info(
                f"Message processed successfully, "
                f"new state: {updated_session.state.value}"
            )
            
            return response, updated_session
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            
            # Resposta de fallback
            fallback_response = (
                "Desculpe, tive um problema ao processar sua mensagem. 😔\n\n"
                "Pode tentar novamente ou falar com um atendente humano?"
            )
            
            return fallback_response, session
    
    async def get_checkpoint(self, session_id: str) -> dict:
        """
        Recupera checkpoint da conversa para continuação.
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Checkpoint salvo ou dict vazio
        """
        try:
            config = {
                "configurable": {
                    "thread_id": session_id,
                    "checkpoint_ns": "conversation"
                }
            }
            
            # Obter checkpoint do saver
            checkpoint = self.checkpointer.get(config)
            
            if checkpoint:
                logger.info(f"Checkpoint recovered for session {session_id}")
                return checkpoint
            else:
                logger.debug(f"No checkpoint found for session {session_id}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting checkpoint: {e}")
            return {}
    
    def get_graph_visualization(self) -> str:
        """
        Retorna representação visual do grafo (para debug/docs).
        
        Returns:
            String com estrutura do grafo
        """
        try:
            # LangGraph pode gerar visualização em Mermaid
            return str(self.graph.get_graph())
        except Exception as e:
            logger.error(f"Error generating graph visualization: {e}")
            return "Graph visualization not available"


# Função auxiliar para criar instância do engine
def create_conversation_engine(
    nlp_service: NLPService,
    guardrails_service: GuardrailsService
) -> ConversationEngine:
    """
    Factory function para criar ConversationEngine.
    
    Args:
        nlp_service: Serviço NLP configurado
        guardrails_service: Serviço de guardrails configurado
        
    Returns:
        ConversationEngine inicializado
    """
    return ConversationEngine(nlp_service, guardrails_service)
