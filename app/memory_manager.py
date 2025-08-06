import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, create_engine, desc, or_
from sqlalchemy.orm import Session

from app.langgraph_chatbot_state import AgentType, ChatbotState
from app.memory_models import (
    Base,
    Conversation,
    ConversationContext,
    ConversationMessage,
    UserSession,
)

logger = logging.getLogger(__name__)


class ConversationMemoryManager:
    """
    Gerenciador de memória persistente para conversas do chatbot

    Responsável por:
    - Criar e gerenciar conversas
    - Persistir mensagens e contexto
    - Recuperar histórico relevante
    - Extrair preferências do usuário
    - Otimizar respostas baseadas no histórico
    """

    def __init__(
        self, database_url: str = "postgresql://user:pass@localhost/faciliauto"
    ):
        """
        Inicializa o gerenciador de memória

        Args:
            database_url: URL do banco de dados PostgreSQL
        """
        try:
            self.engine = create_engine(database_url, echo=False)
            Base.metadata.create_all(self.engine)
            logger.info("💾 Memory Manager inicializado com PostgreSQL")
        except Exception as e:
            # Fallback para SQLite em desenvolvimento
            logger.warning(f"⚠️ Falha ao conectar PostgreSQL: {e}")
            logger.info("🔄 Usando SQLite como fallback...")
            self.engine = create_engine("sqlite:///faciliauto_memory.db", echo=False)
            Base.metadata.create_all(self.engine)
            logger.info("💾 Memory Manager inicializado com SQLite")

    def _get_session(self) -> Session:
        """Cria uma nova sessão do banco de dados"""
        from sqlalchemy.orm import sessionmaker

        SessionLocal = sessionmaker(bind=self.engine)
        return SessionLocal()

    def create_conversation(
        self,
        carro_id: int,
        carro_data: Dict[str, Any],
        user_session_id: Optional[str] = None,
    ) -> str:
        """
        Cria uma nova conversa

        Args:
            carro_id: ID do carro sendo consultado
            carro_data: Dados completos do carro
            user_session_id: ID da sessão do usuário (opcional)

        Returns:
            ID da conversa criada
        """
        session = self._get_session()
        try:
            conversation = Conversation(
                carro_id=carro_id,
                carro_data=carro_data,
                user_session_id=user_session_id,
            )

            session.add(conversation)
            session.commit()

            logger.info(
                f"📝 Nova conversa criada: {conversation.id} para carro {carro_id}"
            )
            return conversation.id

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erro ao criar conversa: {e}")
            raise
        finally:
            session.close()

    def add_message(
        self,
        conversation_id: str,
        message_type: str,  # 'user' ou 'assistant'
        content: str,
        agent_used: Optional[str] = None,
        confidence_score: Optional[float] = None,
        processing_time_ms: Optional[int] = None,
        data_sources: Optional[List[str]] = None,
        followup_suggestions: Optional[List[str]] = None,
    ) -> str:
        """
        Adiciona uma mensagem à conversa

        Args:
            conversation_id: ID da conversa
            message_type: Tipo da mensagem ('user' ou 'assistant')
            content: Conteúdo da mensagem
            agent_used: Agente que processou (para mensagens do assistente)
            confidence_score: Confiança do roteamento
            processing_time_ms: Tempo de processamento
            data_sources: Fontes de dados utilizadas
            followup_suggestions: Sugestões de follow-up

        Returns:
            ID da mensagem criada
        """
        session = self._get_session()
        try:
            message = ConversationMessage(
                conversation_id=conversation_id,
                message_type=message_type,
                content=content,
                agent_used=agent_used,
                confidence_score=confidence_score,
                processing_time_ms=processing_time_ms,
                data_sources=data_sources or [],
                followup_suggestions=followup_suggestions or [],
            )

            session.add(message)

            # Atualizar contadores da conversa
            conversation = (
                session.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )

            if conversation:
                conversation.total_messages += 1
                conversation.last_activity = datetime.now()

                # Atualizar agente primário se for mensagem do assistente
                if message_type == "assistant" and agent_used:
                    self._update_primary_agent(session, conversation, agent_used)

            session.commit()

            logger.debug(f"💬 Mensagem adicionada: {message.id} [{message_type}]")
            return message.id

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erro ao adicionar mensagem: {e}")
            raise
        finally:
            session.close()

    def _update_primary_agent(
        self, session: Session, conversation: Conversation, agent_used: str
    ):
        """Atualiza o agente primário da conversa baseado no uso"""
        # Contar mensagens por agente nesta conversa usando func.count
        from sqlalchemy import func

        agent_counts = (
            session.query(
                ConversationMessage.agent_used,
                func.count(ConversationMessage.id).label("count"),
            )
            .filter(
                ConversationMessage.conversation_id == conversation.id,
                ConversationMessage.agent_used.isnot(None),
            )
            .group_by(ConversationMessage.agent_used)
            .all()
        )

        if agent_counts:
            # Agente mais usado se torna o primário
            primary_agent = max(agent_counts, key=lambda x: x[1])[0]
            conversation.primary_agent = primary_agent

    def add_context(
        self,
        conversation_id: str,
        context_type: str,
        context_key: str,
        context_value: Any,
        confidence: float = 1.0,
        source_message_id: Optional[str] = None,
    ) -> str:
        """
        Adiciona contexto extraído da conversa

        Args:
            conversation_id: ID da conversa
            context_type: Tipo de contexto ('preference', 'intent', etc.)
            context_key: Chave específica do contexto
            context_value: Valor do contexto
            confidence: Confiança na inferência (0.0-1.0)
            source_message_id: ID da mensagem que originou o contexto

        Returns:
            ID do contexto criado
        """
        session = self._get_session()
        try:
            context = ConversationContext(
                conversation_id=conversation_id,
                context_type=context_type,
                context_key=context_key,
                context_value=context_value,
                confidence=confidence,
                source_message_id=source_message_id,
            )

            session.add(context)
            session.commit()

            logger.debug(f"🧠 Contexto adicionado: {context_type}.{context_key}")
            return context.id

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erro ao adicionar contexto: {e}")
            raise
        finally:
            session.close()

    def get_conversation_history(
        self, conversation_id: str, limit: int = 50
    ) -> Tuple[Optional[Conversation], List[ConversationMessage]]:
        """
        Recupera histórico de uma conversa específica

        Args:
            conversation_id: ID da conversa
            limit: Limite de mensagens a retornar

        Returns:
            Tuple com (conversa, lista de mensagens)
        """
        session = self._get_session()
        try:
            conversation = (
                session.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )

            if not conversation:
                return None, []

            messages = (
                session.query(ConversationMessage)
                .filter(ConversationMessage.conversation_id == conversation_id)
                .order_by(ConversationMessage.created_at)
                .limit(limit)
                .all()
            )

            return conversation, messages

        finally:
            session.close()

    def get_user_context(
        self, user_session_id: str, carro_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Recupera contexto acumulado do usuário

        Args:
            user_session_id: ID da sessão do usuário
            carro_id: ID do carro (para contexto específico)

        Returns:
            Dicionário com contexto do usuário
        """
        session = self._get_session()
        try:
            # Buscar conversas recentes do usuário
            query = session.query(Conversation).filter(
                Conversation.user_session_id == user_session_id,
                Conversation.last_activity >= datetime.now() - timedelta(days=30),
            )

            if carro_id:
                query = query.filter(Conversation.carro_id == carro_id)

            conversations = (
                query.order_by(desc(Conversation.last_activity)).limit(10).all()
            )

            # Agregar contexto
            user_context = {
                "recent_conversations": len(conversations),
                "preferred_agents": {},
                "common_interests": [],
                "price_preferences": {},
                "brand_preferences": [],
                "interaction_patterns": {},
            }

            for conv in conversations:
                # Agentes preferidos
                if conv.primary_agent:
                    user_context["preferred_agents"][conv.primary_agent] = (
                        user_context["preferred_agents"].get(conv.primary_agent, 0) + 1
                    )

                # Preferências do carro
                carro_data = conv.carro_data
                if carro_data:
                    marca = carro_data.get("marca")
                    if marca:
                        user_context["brand_preferences"].append(marca)

                    preco = carro_data.get("preco")
                    if preco:
                        price_range = self._get_price_range(preco)
                        user_context["price_preferences"][price_range] = (
                            user_context["price_preferences"].get(price_range, 0) + 1
                        )

            # Limpar duplicatas e ordenar por frequência
            user_context["brand_preferences"] = list(
                set(user_context["brand_preferences"])
            )

            return user_context

        finally:
            session.close()

    def _get_price_range(self, preco: float) -> str:
        """Categoriza preço em faixas"""
        if preco < 50000:
            return "economico"
        elif preco < 100000:
            return "medio"
        elif preco < 200000:
            return "premium"
        else:
            return "luxury"

    def get_similar_conversations(
        self, carro_id: int, limit: int = 5
    ) -> List[Tuple[Conversation, List[ConversationMessage]]]:
        """
        Busca conversas similares sobre o mesmo carro

        Args:
            carro_id: ID do carro
            limit: Limite de conversas a retornar

        Returns:
            Lista de tuplas (conversa, mensagens)
        """
        session = self._get_session()
        try:
            conversations = (
                session.query(Conversation)
                .filter(
                    Conversation.carro_id == carro_id,
                    Conversation.total_messages >= 3,  # Conversas com interação mínima
                )
                .order_by(desc(Conversation.last_activity))
                .limit(limit)
                .all()
            )

            result = []
            for conv in conversations:
                messages = (
                    session.query(ConversationMessage)
                    .filter(ConversationMessage.conversation_id == conv.id)
                    .order_by(ConversationMessage.created_at)
                    .all()
                )

                result.append((conv, messages))

            return result

        finally:
            session.close()

    def enhance_state_with_memory(
        self, state: ChatbotState, user_session_id: Optional[str] = None
    ) -> ChatbotState:
        """
        Enriquece o estado do LangGraph com informações da memória

        Args:
            state: Estado atual do chatbot
            user_session_id: ID da sessão do usuário

        Returns:
            Estado enriquecido com contexto da memória
        """
        try:
            # Recuperar contexto do usuário se disponível
            if user_session_id:
                user_context = self.get_user_context(user_session_id, state["carro_id"])
                state["preferencias_usuario"].update(user_context)

            # Buscar conversas similares para contexto adicional
            similar_convs = self.get_similar_conversations(state["carro_id"], limit=3)

            if similar_convs:
                # Extrair padrões de perguntas frequentes
                frequent_questions = []
                common_agents = {}

                for conv, messages in similar_convs:
                    for msg in messages:
                        if msg.message_type == "user":
                            frequent_questions.append(msg.content)
                        elif msg.agent_used:
                            common_agents[msg.agent_used] = (
                                common_agents.get(msg.agent_used, 0) + 1
                            )

                # Adicionar insights ao estado
                state["dados_utilizados"].extend(
                    ["historico_conversas", "padroes_usuario", "contexto_similar"]
                )

                # Se há padrão claro de agente preferido, ajustar confiança
                if common_agents:
                    most_used_agent = max(common_agents.items(), key=lambda x: x[1])
                    if most_used_agent[1] >= 3:  # Usado pelo menos 3 vezes
                        # Se o agente atual é o mais usado, aumentar confiança
                        if (
                            state["agente_selecionado"]
                            and state["agente_selecionado"].value == most_used_agent[0]
                        ):
                            state["confianca_agente"] = min(
                                state["confianca_agente"] + 0.1, 1.0
                            )

            return state

        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer estado com memória: {e}")
            return state

    def persist_conversation_result(
        self,
        conversation_id: str,
        user_message: str,
        assistant_response: str,
        agent_used: str,
        confidence_score: float,
        processing_time_ms: int,
        data_sources: List[str],
        followup_suggestions: List[str],
    ):
        """
        Persiste o resultado completo de uma interação

        Args:
            conversation_id: ID da conversa
            user_message: Mensagem do usuário
            assistant_response: Resposta do assistente
            agent_used: Agente que processou
            confidence_score: Confiança do roteamento
            processing_time_ms: Tempo de processamento
            data_sources: Fontes de dados utilizadas
            followup_suggestions: Sugestões de follow-up
        """
        try:
            # Adicionar mensagem do usuário
            self.add_message(
                conversation_id=conversation_id,
                message_type="user",
                content=user_message,
            )

            # Adicionar resposta do assistente
            self.add_message(
                conversation_id=conversation_id,
                message_type="assistant",
                content=assistant_response,
                agent_used=agent_used,
                confidence_score=confidence_score,
                processing_time_ms=processing_time_ms,
                data_sources=data_sources,
                followup_suggestions=followup_suggestions,
            )

            # Extrair e persistir contexto se possível
            self._extract_and_persist_context(conversation_id, user_message, agent_used)

        except Exception as e:
            logger.error(f"❌ Erro ao persistir resultado da conversa: {e}")

    def _extract_and_persist_context(
        self, conversation_id: str, user_message: str, agent_used: str
    ):
        """
        Extrai contexto da mensagem do usuário e persiste
        """
        try:
            message_lower = user_message.lower()

            # Detectar preferências de marca
            brands = [
                "toyota",
                "honda",
                "volkswagen",
                "hyundai",
                "chevrolet",
                "ford",
                "nissan",
            ]
            for brand in brands:
                if brand in message_lower:
                    self.add_context(
                        conversation_id=conversation_id,
                        context_type="preference",
                        context_key="mentioned_brand",
                        context_value=brand.title(),
                        confidence=0.8,
                    )

            # Detectar intenção de compra urgente
            urgency_words = ["urgente", "rápido", "hoje", "amanhã", "imediato"]
            if any(word in message_lower for word in urgency_words):
                self.add_context(
                    conversation_id=conversation_id,
                    context_type="intent",
                    context_key="urgency_level",
                    context_value="high",
                    confidence=0.7,
                )

            # Detectar interesse em características específicas
            features = {
                "economia": ["econômico", "barato", "economia", "consumo"],
                "performance": ["potente", "rápido", "performance", "veloz"],
                "conforto": ["conforto", "confortável", "luxo", "comodidade"],
                "familia": ["família", "crianças", "espaçoso", "lugares"],
            }

            for feature, keywords in features.items():
                if any(keyword in message_lower for keyword in keywords):
                    self.add_context(
                        conversation_id=conversation_id,
                        context_type="preference",
                        context_key="feature_interest",
                        context_value=feature,
                        confidence=0.6,
                    )

        except Exception as e:
            logger.error(f"❌ Erro ao extrair contexto: {e}")

    def get_conversation_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Retorna analytics das conversas dos últimos N dias

        Args:
            days: Número de dias para análise

        Returns:
            Dicionário com métricas analíticas
        """
        session = self._get_session()
        try:
            since_date = datetime.now() - timedelta(days=days)

            # Contadores básicos
            total_conversations = (
                session.query(Conversation)
                .filter(Conversation.started_at >= since_date)
                .count()
            )

            total_messages = (
                session.query(ConversationMessage)
                .filter(ConversationMessage.created_at >= since_date)
                .count()
            )

            # Agentes mais utilizados
            from sqlalchemy import func

            agent_usage = (
                session.query(
                    ConversationMessage.agent_used,
                    func.count(ConversationMessage.id).label("count"),
                )
                .filter(
                    ConversationMessage.created_at >= since_date,
                    ConversationMessage.agent_used.isnot(None),
                )
                .group_by(ConversationMessage.agent_used)
                .all()
            )

            # Carros mais consultados
            car_popularity = (
                session.query(
                    Conversation.carro_id, func.count(Conversation.id).label("count")
                )
                .filter(Conversation.started_at >= since_date)
                .group_by(Conversation.carro_id)
                .order_by(desc("count"))
                .limit(10)
                .all()
            )

            return {
                "period_days": days,
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "avg_messages_per_conversation": round(
                    total_messages / max(total_conversations, 1), 2
                ),
                "agent_usage": dict(agent_usage),
                "popular_cars": [
                    {"carro_id": car_id, "conversations": count}
                    for car_id, count in car_popularity
                ],
                "generated_at": datetime.now().isoformat(),
            }

        finally:
            session.close()


# Instância global do gerenciador (singleton)
_memory_manager_instance = None


def get_memory_manager() -> ConversationMemoryManager:
    """
    Retorna instância singleton do gerenciador de memória
    """
    global _memory_manager_instance

    if _memory_manager_instance is None:
        _memory_manager_instance = ConversationMemoryManager()

    return _memory_manager_instance
