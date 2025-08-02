from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from app.langgraph_chatbot_state import ChatbotState, AgentType, criar_estado_inicial
from app.langgraph_chatbot_nodes import (
    router_node,
    tecnico_agent_node,
    financeiro_agent_node,
    comparacao_agent_node,
    manutencao_agent_node,
    avaliacao_agent_node,
    finalizer_node
)
from app.memory_manager import get_memory_manager
import time
import logging

logger = logging.getLogger(__name__)

class FacilIAutoChatbotGraph:
    """
    LangGraph principal para o sistema de chatbot do FacilIAuto
    
    Define o fluxo de conversação usando agentes especializados:
    1. Router analisa a pergunta
    2. Roteia para o agente apropriado
    3. Agente processa e responde
    4. Finalizer formata resposta final
    """
    
    def __init__(self):
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """Constrói o grafo de estados do LangGraph com memória persistente"""
        
        # Criar grafo com o estado customizado
        workflow = StateGraph(ChatbotState)
        
        # Adicionar nós especializados + nó de memória
        workflow.add_node("memory_loader", self._memory_loader_node)
        workflow.add_node("router", router_node)
        workflow.add_node("tecnico_agent", tecnico_agent_node)
        workflow.add_node("financeiro_agent", financeiro_agent_node)
        workflow.add_node("comparacao_agent", comparacao_agent_node)
        workflow.add_node("manutencao_agent", manutencao_agent_node)
        workflow.add_node("avaliacao_agent", avaliacao_agent_node)
        workflow.add_node("finalizer", finalizer_node)
        workflow.add_node("memory_persister", self._memory_persister_node)
        
        # Definir ponto de entrada: primeiro carrega memória
        workflow.set_entry_point("memory_loader")
        
        # Memory loader vai para router
        workflow.add_edge("memory_loader", "router")
        
        # Definir roteamento condicional baseado no agente selecionado
        workflow.add_conditional_edges(
            "router",
            self._decide_next_agent,
            {
                "tecnico": "tecnico_agent",
                "financeiro": "financeiro_agent", 
                "comparacao": "comparacao_agent",
                "manutencao": "manutencao_agent",
                "avaliacao": "avaliacao_agent",
                "finalizer": "finalizer"
            }
        )
        
        # Todos os agentes especializados vão para o finalizer
        workflow.add_edge("tecnico_agent", "finalizer")
        workflow.add_edge("financeiro_agent", "finalizer")
        workflow.add_edge("comparacao_agent", "finalizer")
        workflow.add_edge("manutencao_agent", "finalizer")
        workflow.add_edge("avaliacao_agent", "finalizer")
        
        # Finalizer vai para memory persister
        workflow.add_edge("finalizer", "memory_persister")
        
        # Memory persister vai para END
        workflow.add_edge("memory_persister", END)
        
        return workflow
    
    def _decide_next_agent(self, state: ChatbotState) -> Literal["tecnico", "financeiro", "comparacao", "manutencao", "avaliacao", "finalizer"]:
        """
        Função de decisão que determina qual agente usar baseado no estado
        """
        agente_selecionado = state.get("agente_selecionado")
        
        if agente_selecionado == AgentType.TECNICO:
            return "tecnico"
        elif agente_selecionado == AgentType.FINANCEIRO:
            return "financeiro"
        elif agente_selecionado == AgentType.COMPARACAO:
            return "comparacao"
        elif agente_selecionado == AgentType.MANUTENCAO:
            return "manutencao"
        elif agente_selecionado == AgentType.AVALIACAO:
            return "avaliacao"
        else:
            # Fallback para finalizer (resposta genérica)
            return "finalizer"
    
    def _memory_loader_node(self, state: ChatbotState) -> ChatbotState:
        """
        Nó que carrega contexto de memória persistente antes do processamento
        """
        try:
            memory_manager = get_memory_manager()
            
            # Verificar se a conversa já existe no banco
            if state["conversation_id"]:
                conversation, messages = memory_manager.get_conversation_history(
                    state["conversation_id"], limit=20
                )
                
                if conversation:
                    state["conversation_exists_in_db"] = True
                    # Carregar preferências da conversa existente
                    state["preferencias_usuario"].update(conversation.user_preferences)
                    
                    # Adicionar mensagens históricas ao contexto
                    historical_messages = []
                    for msg in messages[-5:]:  # Últimas 5 mensagens para contexto
                        historical_messages.append({
                            "type": msg.message_type,
                            "content": msg.content[:200],  # Resumido
                            "agent": msg.agent_used
                        })
                    
                    state["historical_context"]["recent_messages"] = historical_messages
                else:
                    # Conversa nova - criar no banco
                    new_conv_id = memory_manager.create_conversation(
                        carro_id=state["carro_id"],
                        carro_data=state["carro_data"],
                        user_session_id=state["user_session_id"]
                    )
                    state["conversation_id"] = new_conv_id
                    state["is_new_conversation"] = True
            
            # Enriquecer estado com contexto do usuário se disponível
            if state["user_session_id"]:
                state = memory_manager.enhance_state_with_memory(
                    state, state["user_session_id"]
                )
            
            # Buscar conversas similares para contexto adicional
            similar_convs = memory_manager.get_similar_conversations(
                state["carro_id"], limit=3
            )
            state["similar_conversations_count"] = len(similar_convs)
            
            logger.debug(f"🧠 Memória carregada: {len(similar_convs)} conversas similares")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar memória: {e}")
            # Continuar sem memória em caso de erro
            state["conversation_exists_in_db"] = False
            state["historical_context"] = {}
        
        return state
    
    def _memory_persister_node(self, state: ChatbotState) -> ChatbotState:
        """
        Nó que persiste o resultado da conversa na memória
        """
        try:
            memory_manager = get_memory_manager()
            
            # Calcular tempo de processamento
            if state["processing_start_time"]:
                processing_time_ms = int((time.time() - state["processing_start_time"]) * 1000)
                state["processing_time_ms"] = processing_time_ms
            
            # Persistir resultado da conversa
            memory_manager.persist_conversation_result(
                conversation_id=state["conversation_id"],
                user_message=state["pergunta_atual"],
                assistant_response=state["resposta_final"],
                agent_used=state["agente_selecionado"].value if state["agente_selecionado"] else "unknown",
                confidence_score=state["confianca_agente"],
                processing_time_ms=state.get("processing_time_ms", 0),
                data_sources=state["dados_utilizados"],
                followup_suggestions=state["sugestoes_followup"]
            )
            
            logger.debug(f"💾 Conversa persistida: {state['conversation_id']}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao persistir memória: {e}")
            # Não falhar o processamento por erro de persistência
        
        return state
    
    def processar_pergunta(
        self, 
        carro_id: int, 
        carro_data: Dict[str, Any], 
        pergunta: str,
        conversation_id: str = None,
        user_session_id: str = None
    ) -> Dict[str, Any]:
        """
        Método principal para processar uma pergunta do usuário com memória persistente
        
        Args:
            carro_id: ID do carro sendo consultado
            carro_data: Dados completos do carro
            pergunta: Pergunta do usuário
            conversation_id: ID da conversa (opcional)
            user_session_id: ID da sessão do usuário (para tracking)
        
        Returns:
            Resultado do processamento com resposta e metadados
        """
        try:
            # Criar estado inicial com suporte a memória
            initial_state = criar_estado_inicial(
                carro_id=carro_id,
                carro_data=carro_data,
                pergunta=pergunta,
                conversation_id=conversation_id,
                user_session_id=user_session_id
            )
            
            # Executar o grafo
            result = self.compiled_graph.invoke(initial_state)
            
            # Extrair resposta e metadados
            return {
                "resposta": result["resposta_final"],
                "agente": result["agente_selecionado"].value if result["agente_selecionado"] else "geral",
                "conversation_id": result["conversation_id"],
                "confianca": result["confianca_agente"],
                "sugestoes_followup": result["sugestoes_followup"],
                "dados_utilizados": result["dados_utilizados"],
                "error": result.get("error_message"),
                "needs_human_fallback": result.get("needs_human_fallback", False)
            }
            
        except Exception as e:
            # Fallback em caso de erro
            return {
                "resposta": f"Desculpe, ocorreu um erro ao processar sua pergunta. Por favor, tente novamente ou reformule sua pergunta. (Erro: {str(e)})",
                "agente": "error",
                "conversation_id": conversation_id or "error",
                "confianca": 0.0,
                "sugestoes_followup": [
                    "Tente reformular sua pergunta",
                    "Pergunte sobre especificações técnicas",
                    "Consulte sobre financiamento"
                ],
                "dados_utilizados": [],
                "error": str(e),
                "needs_human_fallback": True
            }
    
    def obter_agentes_disponiveis(self) -> Dict[str, Any]:
        """
        Retorna informações sobre todos os agentes disponíveis
        """
        return {
            "tecnico": {
                "nome": "Especialista Técnico",
                "emoji": "🔧",
                "especialidades": [
                    "Especificações do motor e potência",
                    "Consumo de combustível e autonomia", 
                    "Sistemas de transmissão e câmbio",
                    "Dimensões e capacidades",
                    "Sistemas de segurança e proteção"
                ],
                "exemplos": [
                    "Qual a potência do motor?",
                    "Como é o consumo de combustível?",
                    "Quais os itens de segurança?"
                ]
            },
            "financeiro": {
                "nome": "Consultor Financeiro",
                "emoji": "💰",
                "especialidades": [
                    "Simulações de financiamento completas",
                    "Documentação necessária para aprovação",
                    "Consórcio e leasing operacional",
                    "Orientações de crédito e score",
                    "Comparação de modalidades de pagamento"
                ],
                "exemplos": [
                    "Como financiar este carro?",
                    "Que documentos preciso?",
                    "Como funciona o consórcio?"
                ]
            },
            "comparacao": {
                "nome": "Analista Comparativo", 
                "emoji": "⚖️",
                "especialidades": [
                    "Comparação detalhada com concorrentes",
                    "Análise de custo-benefício",
                    "Posicionamento no mercado atual",
                    "Identificação de alternativas similares",
                    "Avaliação de pontos fortes e fracos"
                ],
                "exemplos": [
                    "Compare com outros carros",
                    "Vale mais a pena que o concorrente?",
                    "Quais as melhores alternativas?"
                ]
            },
            "manutencao": {
                "nome": "Especialista em Manutenção",
                "emoji": "🔧",
                "especialidades": [
                    "Estimativa de custos de manutenção",
                    "Calendário de revisões e cuidados",
                    "Análise de confiabilidade da marca",
                    "Identificação de problemas conhecidos",
                    "Dicas de conservação e cuidados"
                ],
                "exemplos": [
                    "Quanto vou gastar com manutenção?",
                    "A marca é confiável?",
                    "Quando fazer a primeira revisão?"
                ]
            },
            "avaliacao": {
                "nome": "Avaliador de Mercado",
                "emoji": "📊", 
                "especialidades": [
                    "Análise de valor de mercado atual",
                    "Perspectivas de valorização/depreciação",
                    "Comparação com tabela FIPE",
                    "Potencial de revenda futuro",
                    "Análise de investimento automotivo"
                ],
                "exemplos": [
                    "O preço está justo?",
                    "Como vai valorizar no futuro?",
                    "Vale como investimento?"
                ]
            }
        }
    
    def obter_estatisticas_grafo(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre o grafo LangGraph
        """
        try:
            # Obter informações sobre o grafo compilado
            nodes = list(self.compiled_graph.graph.nodes())
            edges = list(self.compiled_graph.graph.edges())
            
            return {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "entry_point": "router",
                "available_agents": len([n for n in nodes if "_agent" in n]),
                "graph_structure": {
                    "nodes": nodes,
                    "flow": "router → [agent] → finalizer → END"
                },
                "status": "compiled and ready",
                "langgraph_version": "active"
            }
        except Exception as e:
            return {
                "error": f"Erro ao obter estatísticas: {str(e)}",
                "status": "error"
            }
    
    def executar_debug(
        self, 
        carro_id: int, 
        carro_data: Dict[str, Any], 
        pergunta: str
    ) -> Dict[str, Any]:
        """
        Executa o grafo em modo debug para análise de fluxo
        """
        try:
            # Criar estado inicial
            initial_state = criar_estado_inicial(
                carro_id=carro_id,
                carro_data=carro_data,
                pergunta=pergunta
            )
            
            # Executar com streaming para capturar cada etapa
            debug_info = {
                "initial_state": {
                    "pergunta": pergunta,
                    "carro": f"{carro_data.get('marca')} {carro_data.get('modelo')}"
                },
                "execution_flow": [],
                "final_result": None
            }
            
            # Executar grafo
            result = self.compiled_graph.invoke(initial_state)
            
            debug_info["execution_flow"] = [
                f"1. Router analisou: '{pergunta}'",
                f"2. Selecionou agente: {result.get('agente_selecionado', 'N/A')}",
                f"3. Confiança: {result.get('confianca_agente', 0.0):.2f}",
                f"4. Processamento concluído"
            ]
            
            debug_info["final_result"] = {
                "agente_usado": result.get("agente_selecionado"),
                "resposta_gerada": len(result.get("resposta_final", "")) > 0,
                "sugestoes_count": len(result.get("sugestoes_followup", [])),
                "dados_utilizados": result.get("dados_utilizados", [])
            }
            
            return debug_info
            
        except Exception as e:
            return {
                "error": f"Erro no debug: {str(e)}",
                "traceback": str(e)
            }


# Instância global do grafo (Singleton pattern para performance)
_chatbot_graph_instance = None

def get_chatbot_graph() -> FacilIAutoChatbotGraph:
    """
    Retorna instância singleton do grafo do chatbot
    
    Isso evita recompilar o grafo a cada requisição,
    melhorando significativamente a performance.
    """
    global _chatbot_graph_instance
    
    if _chatbot_graph_instance is None:
        _chatbot_graph_instance = FacilIAutoChatbotGraph()
    
    return _chatbot_graph_instance

def reset_chatbot_graph():
    """
    Reseta a instância do grafo (útil para testes)
    """
    global _chatbot_graph_instance
    _chatbot_graph_instance = None