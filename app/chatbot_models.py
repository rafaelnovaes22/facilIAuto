from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TipoAgente(str, Enum):
    """Tipos de agentes especializados disponíveis"""

    TECNICO = "tecnico"
    FINANCEIRO = "financeiro"
    COMPARACAO = "comparacao"
    MANUTENCAO = "manutencao"
    AVALIACAO = "avaliacao"
    GERAL = "geral"


class PerguntaChatbot(BaseModel):
    """Modelo para perguntas enviadas ao chatbot"""

    carro_id: int
    pergunta: str
    conversation_id: Optional[str] = None
    user_session_id: Optional[str] = None  # Para tracking de usuário
    contexto_adicional: Optional[Dict[str, Any]] = None


class RespostaChatbot(BaseModel):
    """Modelo para respostas do chatbot"""

    resposta: str
    agente: TipoAgente
    conversation_id: str
    confianca: float = 0.8
    sugestoes_followup: List[str] = []
    dados_utilizados: List[str] = []


class ConversationContext(BaseModel):
    """Contexto da conversa para manter histórico"""

    conversation_id: str
    carro_id: int
    carro_data: Dict[str, Any]
    historico_mensagens: List[Dict[str, str]] = []
    agente_ativo: Optional[TipoAgente] = None
    preferencias_usuario: Dict[str, Any] = {}
