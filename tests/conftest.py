# -*- coding: utf-8 -*-
"""
Configuração global de testes para facilIAuto

Este arquivo contém fixtures e configurações compartilhadas
entre todos os testes do projeto.
"""

import os
import sqlite3
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Configurar variáveis de ambiente para testes
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///test.db"


@pytest.fixture
def mock_database():
    """Mock do banco de dados SQLite para testes"""
    # Criar banco em memória para testes
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Criar tabelas básicas
    cursor.execute(
        """
        CREATE TABLE carros (
            id INTEGER PRIMARY KEY,
            marca TEXT,
            modelo TEXT,
            ano INTEGER,
            preco REAL,
            categoria TEXT,
            consumo REAL,
            potencia INTEGER,
            cambio TEXT,
            combustivel TEXT,
            quilometragem INTEGER,
            cor TEXT
        )
    """
    )

    # Inserir dados de teste
    cursor.execute(
        """
        INSERT INTO carros (marca, modelo, ano, preco, categoria, consumo, potencia, cambio, combustivel, quilometragem, cor)
        VALUES ('Toyota', 'Corolla', 2023, 120000, 'Sedan', 12.5, 154, 'CVT', 'Flex', 10000, 'Branco')
    """
    )

    cursor.execute(
        """
        INSERT INTO carros (marca, modelo, ano, preco, categoria, consumo, potencia, cambio, combustivel, quilometragem, cor)
        VALUES ('Honda', 'Civic', 2023, 140000, 'Sedan', 11.8, 158, 'CVT', 'Flex', 5000, 'Preto')
    """
    )

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def mock_chatbot():
    """Mock do chatbot LangGraph"""
    chatbot = MagicMock()
    chatbot.processar_pergunta = AsyncMock(
        return_value={
            "resposta": "Esta é uma resposta de teste do chatbot",
            "agente": "teste",
            "confianca": 0.95,
            "dados_utilizados": ["teste"],
            "sugestoes_followup": ["Pergunta de follow-up teste"],
        }
    )
    chatbot.obter_agentes_disponiveis = MagicMock(
        return_value={
            "tecnico": {
                "nome": "Agente Técnico",
                "emoji": "🔧",
                "especialidades": ["especificações", "performance"],
            }
        }
    )
    return chatbot


@pytest.fixture
def test_client(mock_chatbot):
    """Cliente HTTP para testes de API"""
    # Patch do construtor do grafo para retornar o mock de chatbot
    with patch("app.chatbot_api.get_chatbot_graph", return_value=mock_chatbot):
        # Patch dos dados de carros para garantir dados determinísticos
        with patch("app.database.get_carros") as mock_get_carros:
            mock_get_carros.return_value = [
                {
                    "id": 1,
                    "marca": "Toyota",
                    "modelo": "Corolla",
                    "ano": 2023,
                    "preco": 120000,
                    "categoria": "Sedan",
                }
            ]

            from app.api import app

            yield TestClient(app)


@pytest.fixture
def sample_car():
    """Dados de exemplo de um carro para testes"""
    return {
        "id": 1,
        "marca": "Toyota",
        "modelo": "Corolla",
        "ano": 2023,
        "preco": 120000,
        "categoria": "Sedan",
        "consumo": 12.5,
        "potencia": 154,
        "cambio": "CVT",
        "combustivel": "Flex",
        "quilometragem": 10000,
        "cor": "Branco",
        "opcionais": [
            "Ar Condicionado",
            "Central Multimidia",
            "Sensor de Estacionamento",
        ],
    }


@pytest.fixture
def mock_memory_manager():
    """Mock do gerenciador de memória"""
    memory = MagicMock()
    # Usar mocks síncronos para evitar 'coroutine was never awaited'
    memory.get_conversation_history = MagicMock(return_value=(None, []))
    memory.save_conversation = MagicMock()
    memory.get_user_context = MagicMock(
        return_value={
            "recent_conversations": 0,
            "preferred_agents": {},
            "brand_preferences": [],
        }
    )
    memory.get_similar_conversations = MagicMock(return_value=[])
    memory.get_conversation_analytics = MagicMock(
        return_value={
            "total_conversations": 1,
            "total_messages": 2,
            "avg_messages_per_conversation": 2.0,
            "agents_usage": {"teste": 1},
        }
    )
    # Métodos utilitários eventualmente chamados pelos testes
    memory.add_message = MagicMock(return_value="msg_1")
    memory.add_context = MagicMock(return_value="ctx_1")
    memory._extract_and_persist_context = MagicMock(return_value=None)
    memory.create_conversation = MagicMock(return_value="conv_1")
    return memory


# Alias usado pelos testes de memória
@pytest.fixture
def memory_manager(mock_memory_manager):
    """Fornece o gerenciador de memória para os testes que esperam 'memory_manager'"""
    return mock_memory_manager


# ID de conversa padrão para testes
@pytest.fixture
def conversation_id():
    return "test_conversation_id"


# Configurações de performance para testes
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Configurar ambiente de teste automaticamente"""
    # Configurar timeout padrão para testes async
    os.environ["PYTEST_TIMEOUT"] = "30"

    # Configurar logging para testes
    import logging

    logging.getLogger().setLevel(logging.WARNING)

    yield

    # Cleanup após testes
    if os.path.exists("test.db"):
        os.remove("test.db")


# Markers personalizados
def pytest_configure(config):
    """Configurar markers personalizados"""
    config.addinivalue_line("markers", "e2e: marca testes end-to-end")
    config.addinivalue_line("markers", "integration: marca testes de integração")
    config.addinivalue_line("markers", "unit: marca testes unitários")
    config.addinivalue_line("markers", "slow: marca testes lentos")
    config.addinivalue_line(
        "markers", "requires_db: marca testes que precisam de database"
    )
    config.addinivalue_line(
        "markers", "xp_methodology: marca testes seguindo metodologia XP"
    )
