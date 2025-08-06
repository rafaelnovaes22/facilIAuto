import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Conversation(Base):
    """
    Modelo para armazenar conversas completas do chatbot

    Cada conversa representa uma sessão de interação do usuário
    com o chatbot sobre um veículo específico.
    """

    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Identificadores
    carro_id = Column(Integer, nullable=False, index=True)
    user_session_id = Column(
        String, nullable=True, index=True
    )  # Para identificar usuário

    # Dados do veículo (snapshot para preservar contexto)
    carro_data = Column(JSON, nullable=False)

    # Metadados da conversa
    started_at = Column(DateTime, default=func.now(), nullable=False)
    last_activity = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    ended_at = Column(DateTime, nullable=True)

    # Estado da conversa
    is_active = Column(Boolean, default=True, nullable=False)
    total_messages = Column(Integer, default=0, nullable=False)

    # Preferências do usuário identificadas durante a conversa
    user_preferences = Column(JSON, default=dict, nullable=False)

    # Agente mais utilizado na conversa
    primary_agent = Column(String, nullable=True)

    # Relacionamentos
    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
    context_data = relationship(
        "ConversationContext",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "carro_id": self.carro_id,
            "user_session_id": self.user_session_id,
            "carro_data": self.carro_data,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_activity": self.last_activity.isoformat()
            if self.last_activity
            else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "is_active": self.is_active,
            "total_messages": self.total_messages,
            "user_preferences": self.user_preferences,
            "primary_agent": self.primary_agent,
        }


class ConversationMessage(Base):
    """
    Modelo para armazenar mensagens individuais de uma conversa

    Cada mensagem representa uma interação específica (pergunta do usuário
    ou resposta do agente) dentro de uma conversa.
    """

    __tablename__ = "conversation_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(
        String, ForeignKey("conversations.id"), nullable=False, index=True
    )

    # Tipo e conteúdo da mensagem
    message_type = Column(String, nullable=False)  # 'user' ou 'assistant'
    content = Column(Text, nullable=False)

    # Metadados do processamento (para mensagens do assistente)
    agent_used = Column(String, nullable=True)  # Qual agente processou
    confidence_score = Column(Float, nullable=True)  # Confiança do roteamento
    processing_time_ms = Column(Integer, nullable=True)  # Tempo de processamento

    # Dados utilizados e sugestões geradas
    data_sources = Column(
        JSON, default=list, nullable=False
    )  # Fontes de dados utilizadas
    followup_suggestions = Column(
        JSON, default=list, nullable=False
    )  # Sugestões de follow-up

    # Feedback do usuário (opcional)
    user_rating = Column(Integer, nullable=True)  # 1-5 estrelas
    user_feedback = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relacionamentos
    conversation = relationship("Conversation", back_populates="messages")

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "message_type": self.message_type,
            "content": self.content,
            "agent_used": self.agent_used,
            "confidence_score": self.confidence_score,
            "processing_time_ms": self.processing_time_ms,
            "data_sources": self.data_sources,
            "followup_suggestions": self.followup_suggestions,
            "user_rating": self.user_rating,
            "user_feedback": self.user_feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ConversationContext(Base):
    """
    Modelo para armazenar contexto adicional da conversa

    Armazena informações extraídas durante a conversa que podem
    ser úteis para personalização de respostas futuras.
    """

    __tablename__ = "conversation_context"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(
        String, ForeignKey("conversations.id"), nullable=False, index=True
    )

    # Tipo de contexto
    context_type = Column(
        String, nullable=False, index=True
    )  # 'preference', 'intent', 'demographic', etc.
    context_key = Column(String, nullable=False)  # Chave específica
    context_value = Column(JSON, nullable=False)  # Valor do contexto

    # Confiança na inferência do contexto
    confidence = Column(Float, default=1.0, nullable=False)

    # Quando foi identificado
    identified_at = Column(DateTime, default=func.now(), nullable=False)

    # Fonte da inferência
    source_message_id = Column(
        String, ForeignKey("conversation_messages.id"), nullable=True
    )

    # Relacionamentos
    conversation = relationship("Conversation", back_populates="context_data")

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "context_type": self.context_type,
            "context_key": self.context_key,
            "context_value": self.context_value,
            "confidence": self.confidence,
            "identified_at": self.identified_at.isoformat()
            if self.identified_at
            else None,
            "source_message_id": self.source_message_id,
        }


class UserSession(Base):
    """
    Modelo para agrupar conversas por sessão de usuário

    Permite rastrear um usuário através de múltiplas conversas
    e construir um perfil de preferências ao longo do tempo.
    """

    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Identificadores do usuário (podem ser anônimos)
    browser_fingerprint = Column(String, nullable=True, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Dados coletados sobre o usuário
    inferred_preferences = Column(JSON, default=dict, nullable=False)
    favorite_brands = Column(JSON, default=list, nullable=False)
    price_range_interest = Column(JSON, default=dict, nullable=False)

    # Estatísticas
    total_conversations = Column(Integer, default=0, nullable=False)
    total_messages = Column(Integer, default=0, nullable=False)

    # Timestamps
    first_seen = Column(DateTime, default=func.now(), nullable=False)
    last_seen = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "browser_fingerprint": self.browser_fingerprint,
            "inferred_preferences": self.inferred_preferences,
            "favorite_brands": self.favorite_brands,
            "price_range_interest": self.price_range_interest,
            "total_conversations": self.total_conversations,
            "total_messages": self.total_messages,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


# Índices para performance
from sqlalchemy import Index

# Índices compostos para queries frequentes
Index("idx_conv_carro_active", Conversation.carro_id, Conversation.is_active)
Index(
    "idx_msg_conv_type",
    ConversationMessage.conversation_id,
    ConversationMessage.message_type,
)
Index(
    "idx_ctx_conv_type",
    ConversationContext.conversation_id,
    ConversationContext.context_type,
)
Index(
    "idx_conv_user_activity", Conversation.user_session_id, Conversation.last_activity
)
