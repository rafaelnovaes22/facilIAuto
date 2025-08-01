"""
🧪 PyTest Configuration - FacilIAuto XP
Fixtures e configurações globais para testes
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.api import app
from app.models import QuestionarioBusca

# 🔧 Mock Database Configuration
# Como o projeto usa PostgreSQL direto (não SQLAlchemy ORM), 
# vamos mockar as funções de banco de dados


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def mock_database():
    """Mock database functions for testing."""
    with patch('app.database.get_carros') as mock_get_carros, \
         patch('app.database.get_carro_by_id') as mock_get_carro_by_id:
        
        # Mock default return values
        mock_get_carros.return_value = []
        mock_get_carro_by_id.return_value = None
        
        yield {
            'get_carros': mock_get_carros,
            'get_carro_by_id': mock_get_carro_by_id
        }


@pytest.fixture(scope="function")
def test_client(mock_database) -> TestClient:
    """Create a test client with mocked database."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_questionario() -> QuestionarioBusca:
    """Questionário de exemplo para testes."""
    return QuestionarioBusca(
        marca_preferida="TOYOTA",
        modelo_especifico="Corolla",
        marcas_alternativas=["HONDA", "VOLKSWAGEN"],
        modelos_alternativos=["Civic", "Jetta"],
        urgencia="hoje_amanha",
        regiao="SP",
        uso_principal=["urbano"],
        pessoas_transportar=4,
        criancas=False,
        animais=False,
        espaco_carga="medio",
        potencia_desejada="media",
        prioridade="economia",
        orcamento_min=50000,
        orcamento_max=80000
    )


@pytest.fixture
def minimal_questionario() -> QuestionarioBusca:
    """Questionário mínimo para testes."""
    return QuestionarioBusca(
        marca_preferida="sem_preferencia",
        modelo_especifico="aberto_opcoes",
        urgencia="sem_pressa",
        regiao="SP",
        uso_principal=["urbano"],
        pessoas_transportar=4,
        criancas=False,
        animais=False,
        espaco_carga="medio",
        potencia_desejada="media",
        prioridade="equilibrio"
    )


@pytest.fixture
def mock_carros_data():
    """Dados mock de carros para testes."""
    return [
        {
            "id": "1",
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2022,
            "preco": 65000,
            "km": 25000,
            "combustivel": "Flex",
            "cor": "Branco",
            "regiao": ["SP", "RJ"],
            "uso_recomendado": ["urbano", "viagem"],
            "pessoas_capacidade": 5,
            "espaco_carga": "medio",
            "potencia": "media",
            "fotos": ["foto1.jpg"],
            "descricao": "Corolla 2022 em excelente estado",
            "opcionais": ["ar_condicionado", "direcao_hidraulica"],
            "destaque": True
        },
        {
            "id": "2", 
            "marca": "Honda",
            "modelo": "Civic",
            "ano": 2021,
            "preco": 70000,
            "km": 30000,
            "combustivel": "Flex",
            "cor": "Prata",
            "regiao": ["SP"],
            "uso_recomendado": ["urbano", "esportivo"],
            "pessoas_capacidade": 5,
            "espaco_carga": "medio",
            "potencia": "alta",
            "fotos": ["foto2.jpg"],
            "descricao": "Civic 2021 esportivo",
            "opcionais": ["ar_condicionado", "multimidia"],
            "destaque": False
        }
    ]


@pytest.fixture
def setup_mock_carros_data(mock_database, mock_carros_data):
    """Configure mock database with test data."""
    mock_database['get_carros'].return_value = mock_carros_data
    mock_database['get_carro_by_id'].side_effect = lambda car_id: next(
        (car for car in mock_carros_data if car['id'] == car_id), None
    )
    return mock_database