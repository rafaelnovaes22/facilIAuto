import uuid
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class AgentType(str, Enum):
    """Tipos de agentes especializados"""

    ROUTER = "router"
    TECNICO = "tecnico"
    FINANCEIRO = "financeiro"
    COMPARACAO = "comparacao"
    MANUTENCAO = "manutencao"
    AVALIACAO = "avaliacao"
    USO_PRINCIPAL = "uso_principal"
    FINALIZER = "finalizer"


class ChatbotState(TypedDict):
    """Estado central do LangGraph para o chatbot com memória persistente"""

    # Identificadores
    conversation_id: str
    carro_id: int
    user_session_id: Optional[str]  # Para tracking de usuário

    # Dados do veículo
    carro_data: Dict[str, Any]

    # Conversa
    messages: Annotated[List[BaseMessage], "Lista de mensagens da conversa"]
    pergunta_atual: str
    resposta_final: str

    # Roteamento e agentes
    agente_selecionado: Optional[AgentType]
    confianca_agente: float
    historico_agentes: List[str]

    # Contexto e preferências (enriquecidas com memória)
    preferencias_usuario: Dict[str, Any]
    dados_utilizados: List[str]
    sugestoes_followup: List[str]

    # Memória persistente
    is_new_conversation: bool
    conversation_exists_in_db: bool
    historical_context: Dict[str, Any]
    similar_conversations_count: int

    # Performance tracking
    processing_start_time: float
    processing_time_ms: Optional[int]

    # Metadados
    timestamp: str
    error_message: Optional[str]
    needs_human_fallback: bool


def criar_estado_inicial(
    carro_id: int,
    carro_data: Dict[str, Any],
    pergunta: str,
    conversation_id: Optional[str] = None,
    user_session_id: Optional[str] = None,
) -> ChatbotState:
    """Cria estado inicial para uma nova conversa ou pergunta com memória persistente"""

    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    import time

    return ChatbotState(
        conversation_id=conversation_id,
        carro_id=carro_id,
        user_session_id=user_session_id,
        carro_data=carro_data,
        messages=[HumanMessage(content=pergunta)],
        pergunta_atual=pergunta,
        resposta_final="",
        agente_selecionado=None,
        confianca_agente=0.0,
        historico_agentes=[],
        preferencias_usuario={},
        dados_utilizados=[],
        sugestoes_followup=[],
        # Campos de memória persistente
        is_new_conversation=conversation_id is None,
        conversation_exists_in_db=False,
        historical_context={},
        similar_conversations_count=0,
        # Performance tracking
        processing_start_time=time.time(),
        processing_time_ms=None,
        # Metadados
        timestamp=str(uuid.uuid4()),  # Em prod usar datetime
        error_message=None,
        needs_human_fallback=False,
    )


def adicionar_mensagem_usuario(state: ChatbotState, pergunta: str) -> ChatbotState:
    """Adiciona nova mensagem do usuário ao estado"""
    state["messages"].append(HumanMessage(content=pergunta))
    state["pergunta_atual"] = pergunta
    state["resposta_final"] = ""
    state["agente_selecionado"] = None
    state["confianca_agente"] = 0.0
    state["error_message"] = None
    return state


def adicionar_resposta_agente(
    state: ChatbotState,
    resposta: str,
    agente: AgentType,
    confianca: float,
    dados_utilizados: List[str] = None,
    sugestoes: List[str] = None,
) -> ChatbotState:
    """Adiciona resposta do agente ao estado"""
    state["messages"].append(AIMessage(content=resposta))
    state["resposta_final"] = resposta
    state["agente_selecionado"] = agente
    state["confianca_agente"] = confianca
    state["historico_agentes"].append(agente.value)
    state["dados_utilizados"] = dados_utilizados or []
    state["sugestoes_followup"] = sugestoes or []
    return state
