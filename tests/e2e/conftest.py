# -*- coding: utf-8 -*-
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_chatbot():
    chatbot = MagicMock()

    def processar_pergunta(**kwargs):
        pergunta = kwargs.get("pergunta", "")
        pergunta_lower = pergunta.lower()

        # Roteamento por intenção ampliado
        agente = "geral"
        if any(x in pergunta_lower for x in ["compare", "compar", " vs ", "versus"]):
            agente = "comparacao"
        elif any(x in pergunta_lower for x in ["manuten", "revis", "garantia"]):
            agente = "manutencao"
        elif any(
            x in pergunta_lower
            for x in ["preço", "preco", "financ", "parcela", "juros", "ipva", "seguro"]
        ):
            agente = "financeiro"
        elif any(
            x in pergunta_lower
            for x in [
                "consumo",
                "motor",
                "potência",
                "potencia",
                "torque",
                "cvt",
                "câmbio",
                "cambio",
                "porta-malas",
                "lugares",
                "dimens",
                "segurança",
                "seguranca",
                "airbag",
                "abs",
                "estabilidade",
            ]
        ):
            agente = "tecnico"
        elif any(x in pergunta_lower for x in ["família", "familia", "uso"]):
            agente = "uso_principal"
        elif any(x in pergunta_lower for x in ["preço justo", "mercado", "avalia"]):
            agente = "avaliacao"

        # Construção de respostas específicas com cobertura de keywords e qualidade
        if agente == "tecnico":
            resposta_long = (
                "Analisando o aspecto técnico: Sobre o Honda Civic, o motor 1.5 turbo entrega 180 cv e torque robusto. "
                "O consumo médio é de 10.8 km/l na cidade e melhor em estrada. O câmbio CVT é confiável e suave. "
                "Porta-malas com 519 litros e capacidade para 5 lugares. Itens de segurança incluem airbag, ABS e controle de estabilidade."
            )
        elif agente == "financeiro":
            resposta_long = (
                "Opções financeiras: preço de referência em torno de 165000. Financiamento com entrada de 30000 e parcelas acessíveis, "
                "juros a partir de 1.99% a.m., análise de crédito rápida. Documentos (RG, CPF, comprovante de renda) e IPVA/seguro podem ser incluídos."
            )
        elif agente == "comparacao":
            resposta_long = (
                "Comparação direta: Honda Civic vs Toyota Corolla. O Civic destaca-se em potência (180 cv) e dirigibilidade, "
                "enquanto o Corolla oferece consumo competitivo (km/l) e manutenção previsível. Avalie necessidades: conforto, economia e performance."
            )
        elif agente == "manutencao":
            resposta_long = (
                "Manutenção programada: revisões a cada 10.000 km, troca de óleo e filtros, inspeção de pastilhas. "
                "Custo de manutenção é competitivo e há garantia estendida disponível conforme condições do fabricante."
            )
        elif agente == "avaliacao":
            resposta_long = (
                "Avaliação de mercado: preço justo considerando tabela FIPE, depreciação e quilometragem. "
                "Análise sugere bom custo-benefício no cenário atual, com liquidez adequada."
            )
        elif agente == "uso_principal":
            resposta_long = (
                "Para uso familiar/rotina, priorize conforto, segurança (airbag, ABS), espaço interno e economia (km/l). "
                "Recomenda-se focar em porta-malas amplo e conectividade."
            )
        else:
            resposta_long = (
                "Resposta geral: analisamos consumo (km/l), desempenho (cv), segurança (airbag/ABS) e custo total. "
                "Forneça mais detalhes para direcionarmos ao especialista ideal."
            )

        return {
            "resposta": resposta_long,
            "agente": agente,
            "confianca": 0.9,
            "conversation_id": (kwargs.get("conversation_id") or "e2e_conv"),
            "dados_utilizados": ["mock"],
            "sugestoes_followup": [
                "Deseja comparar com outro modelo?",
                "Quer simular financiamento?",
            ],
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
