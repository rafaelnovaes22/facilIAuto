# -*- coding: utf-8 -*-
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_chatbot():
    chatbot = MagicMock()

    def processar_pergunta(**kwargs):
        pergunta = kwargs.get("pergunta", "")
        agente = "geral"
        if "consumo" in pergunta.lower():
            agente = "tecnico"
        elif any(x in pergunta.lower() for x in ["preço", "financ", "custa"]):
            agente = "financeiro"
        elif any(x in pergunta.lower() for x in ["família", "familia", "uso"]):
            agente = "uso_principal"
        resposta_long = (
            f"Resposta mock detalhada do agente {agente}. "
            "Inclui informações suficientes para testes E2E, "
            "com conteúdo descritivo para ultrapassar o limite mínimo de caracteres."
        )
        return {
            "resposta": resposta_long,
            "agente": agente,
            "confianca": 0.9,
            "conversation_id": (kwargs.get("conversation_id") or "e2e_conv"),
            "dados_utilizados": ["mock"],
            "sugestoes_followup": ["Teste"],
        }

    chatbot.processar_pergunta = MagicMock(side_effect=processar_pergunta)
    chatbot.obter_agentes_disponiveis = MagicMock(
        return_value={
            "tecnico": {
                "nome": "Agente Técnico",
                "emoji": "🔧",
                "especialidades": ["consumo", "motor"],
            },
            "financeiro": {"nome": "Agente Financeiro", "emoji": "💰"},
            "uso_principal": {"nome": "Uso Principal", "emoji": "🚗"},
            "avaliacao": {"nome": "Avaliacao", "emoji": "⭐"},
            "comparacao": {"nome": "Comparacao", "emoji": "⚖️"},
            "manutencao": {"nome": "Manutencao", "emoji": "🛠️"},
        }
    )
    chatbot.obter_estatisticas_grafo = MagicMock(
        return_value={"total_nodes": 6, "status": "compiled and ready"}
    )
    return chatbot


@pytest.fixture
def mock_chatbot_client(mock_chatbot):
    with patch("app.chatbot_api.get_chatbot_graph", return_value=mock_chatbot):
        with patch("app.database.get_carros") as mock_get_carros, patch(
            "app.database.get_carro_by_id"
        ) as mock_get_carro_by_id:
            mock_get_carros.return_value = [
                {"id": 1, "marca": "Toyota", "modelo": "Corolla", "ano": 2023}
            ]
            mock_get_carro_by_id.side_effect = lambda cid: {
                "id": int(cid),
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2023,
            }
            from app.api import app

            yield TestClient(app)
