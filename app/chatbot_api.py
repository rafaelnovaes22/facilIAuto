import logging

from fastapi import APIRouter, HTTPException

from app.chatbot_models import PerguntaChatbot, RespostaChatbot, TipoAgente
from app.langgraph_chatbot_graph import get_chatbot_graph

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chatbot/perguntar", response_model=RespostaChatbot)
async def processar_pergunta_chatbot(pergunta: PerguntaChatbot):
    """
    Endpoint principal para processar perguntas do chatbot usando LangGraph

    Recebe uma pergunta do usuário e processa através do grafo de agentes IA
    especializado, retornando resposta contextualizada e inteligente.
    """
    try:
        logger.info(
            f"[LangGraph] Processando pergunta para carro {pergunta.carro_id}: {pergunta.pergunta}"
        )

        # Validar se o carro existe
        from app.database import get_carro_by_id

        carro = get_carro_by_id(pergunta.carro_id)
        if not carro:
            raise HTTPException(
                status_code=404,
                detail=f"Carro com ID {pergunta.carro_id} não encontrado",
            )

        # Obter instância do grafo LangGraph
        chatbot_graph = get_chatbot_graph()

        # Processar pergunta através do LangGraph com memória persistente
        resultado = chatbot_graph.processar_pergunta(
            carro_id=pergunta.carro_id,
            carro_data=carro,
            pergunta=pergunta.pergunta,
            conversation_id=pergunta.conversation_id,
            user_session_id=pergunta.user_session_id,
        )

        # Converter para formato de resposta esperado
        agente_tipo = (
            TipoAgente(resultado["agente"])
            if resultado["agente"] in [e.value for e in TipoAgente]
            else TipoAgente.GERAL
        )

        resposta = RespostaChatbot(
            resposta=resultado["resposta"],
            agente=agente_tipo,
            conversation_id=resultado["conversation_id"],
            confianca=resultado["confianca"],
            sugestoes_followup=resultado["sugestoes_followup"],
            dados_utilizados=resultado["dados_utilizados"],
        )

        logger.info(
            f"[LangGraph] Resposta gerada pelo agente {resposta.agente} com confiança {resposta.confianca}"
        )

        return resposta

    except ValueError as e:
        logger.error(f"[LangGraph] Erro de validação: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"[LangGraph] Erro interno ao processar pergunta: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Erro interno do servidor. Tente novamente."
        )


@router.get("/chatbot/agentes")
async def listar_agentes():
    """
    Lista todos os agentes disponíveis no LangGraph e suas especialidades

    Retorna informações detalhadas sobre cada agente especializado,
    incluindo suas capacidades e exemplos de uso.
    """
    try:
        # Obter informações dos agentes do LangGraph
        chatbot_graph = get_chatbot_graph()
        agentes_info = chatbot_graph.obter_agentes_disponiveis()

        return {
            "total_agentes": len(agentes_info),
            "agentes": agentes_info,
            "langgraph_info": {
                "framework": "LangGraph",
                "tipo_processamento": "Grafo de Estados com Agentes Especializados",
                "roteamento": "Automático baseado em análise de contexto",
            },
            "como_usar": "Faça perguntas naturais! O LangGraph analisa automaticamente e direciona para o especialista ideal 🚀",
        }

    except Exception as e:
        logger.error(f"[LangGraph] Erro ao listar agentes: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/chatbot/langgraph/estatisticas")
async def obter_estatisticas_langgraph():
    """
    Obtém estatísticas detalhadas do LangGraph

    Retorna informações sobre a estrutura do grafo,
    nós disponíveis e performance geral.
    """
    try:
        chatbot_graph = get_chatbot_graph()
        estatisticas = chatbot_graph.obter_estatisticas_grafo()

        return {
            "langgraph_stats": estatisticas,
            "framework_info": {
                "nome": "LangGraph",
                "versao": "0.1.0+",
                "tipo": "State Graph with Conditional Edges",
                "performance": "Otimizado com singleton pattern",
            },
            "agentes_especializados": list(
                chatbot_graph.obter_agentes_disponiveis().keys()
            ),
            "fluxo_processamento": [
                "1. Recebe pergunta do usuário",
                "2. Router analisa contexto e palavras-chave",
                "3. Seleciona agente especializado",
                "4. Agente processa e gera resposta",
                "5. Finalizer formata saída",
                "6. Retorna resposta estruturada",
            ],
        }

    except Exception as e:
        logger.error(f"[LangGraph] Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/chatbot/langgraph/debug")
async def debug_langgraph(pergunta: PerguntaChatbot):
    """
    Executa o LangGraph em modo debug para análise detalhada

    Útil para desenvolvedores analisarem o fluxo de decisão
    e otimização do roteamento entre agentes.
    """
    try:
        logger.info(
            f"[DEBUG] Iniciando debug LangGraph para pergunta: {pergunta.pergunta}"
        )

        # Validar se o carro existe
        from app.database import get_carro_by_id

        carro = get_carro_by_id(pergunta.carro_id)
        if not carro:
            raise HTTPException(
                status_code=404,
                detail=f"Carro com ID {pergunta.carro_id} não encontrado",
            )

        # Executar debug do LangGraph
        chatbot_graph = get_chatbot_graph()
        debug_info = chatbot_graph.executar_debug(
            carro_id=pergunta.carro_id, carro_data=carro, pergunta=pergunta.pergunta
        )

        return {
            "debug_langgraph": debug_info,
            "carro_analisado": {
                "id": pergunta.carro_id,
                "veiculo": f"{carro.get('marca')} {carro.get('modelo')} {carro.get('ano')}",
            },
            "modo": "DEBUG_MODE",
            "timestamp": "2024-01-01T00:00:00",  # Em prod usar datetime
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DEBUG] Erro no debug LangGraph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no debug: {str(e)}")


@router.post("/chatbot/feedback")
async def registrar_feedback(conversation_id: str, rating: int, comentario: str = None):
    """
    Registra feedback do usuário sobre uma resposta do LangGraph

    Usado para melhorar continuamente a qualidade das respostas
    e otimizar o roteamento entre agentes.
    """
    try:
        # Validar rating
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating deve estar entre 1 e 5")

        # Em implementação real, salvaria no banco de dados para análise
        feedback_data = {
            "conversation_id": conversation_id,
            "rating": rating,
            "comentario": comentario,
            "framework": "LangGraph",
            "timestamp": "2024-01-01T00:00:00",  # Usar datetime real
        }

        logger.info(f"[LangGraph] Feedback registrado: {feedback_data}")

        return {
            "message": "Feedback registrado com sucesso",
            "agradecimento": "Obrigado! Seu feedback ajuda a melhorar nossos agentes IA 🤖✨",
            "framework": "LangGraph",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[LangGraph] Erro ao registrar feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# Health check específico para o LangGraph Chatbot
@router.get("/chatbot/health")
async def health_check():
    """
    Verifica se o sistema de chatbot LangGraph está funcionando corretamente
    """
    try:
        # Teste básico de funcionamento do LangGraph
        chatbot_graph = get_chatbot_graph()
        agentes_disponiveis = chatbot_graph.obter_agentes_disponiveis()
        estatisticas = chatbot_graph.obter_estatisticas_grafo()

        return {
            "status": "healthy",
            "framework": "LangGraph",
            "agentes_carregados": len(agentes_disponiveis),
            "nodes_no_grafo": estatisticas.get("total_nodes", 0),
            "grafo_compilado": estatisticas.get("status") == "compiled and ready",
            "timestamp": "2024-01-01T00:00:00",  # Usar datetime real
            "versao": "2.0.0 - LangGraph Edition",
            "performance": "Singleton pattern ativo",
        }

    except Exception as e:
        logger.error(f"[LangGraph] Erro no health check: {str(e)}")
        return {
            "status": "unhealthy",
            "framework": "LangGraph",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00",
            "action": "Verificar logs do servidor",
        }
