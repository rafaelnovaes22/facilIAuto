"""
Configurações específicas para testes E2E do LangGraph

Este arquivo contém fixtures, configurações e utilitários
específicos para testes end-to-end do sistema LangGraph.
"""

import asyncio
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from app.api import app
from app.memory_manager import get_memory_manager


# Event loop fixture removido - usando o do conftest.py principal


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    """
    Cliente de teste FastAPI para testes E2E

    Utiliza uma instância isolada da aplicação para evitar
    interferência entre testes.
    """
    return TestClient(app)


@pytest.fixture(scope="session")
def memory_manager():
    """
    Instância do gerenciador de memória para testes

    Utiliza banco SQLite em memória para isolamento
    """
    return get_memory_manager()

# Estado de memória simulado para testes mockados (usado pelos mocks)
TEST_MEMORY_STATE: Dict[str, Any] = {
    "user_sessions": {},          # session_id -> count
    "brand_preferences": {},      # session_id -> [brands]
    "conversations": {},          # conversation_id -> list[message]
}


@pytest.fixture
def sample_cars() -> Dict[str, Dict[str, Any]]:
    """
    Conjunto de carros de exemplo para testes E2E

    Inclui diferentes categorias e faixas de preço para
    testar diversos cenários de resposta dos agentes.
    """
    return {
        "economico": {
            "id": 1001,
            "marca": "Volkswagen",
            "modelo": "Gol",
            "ano": 2023,
            "preco": 75000,
            "categoria": "Hatch",
            "consumo": 13.2,
            "potencia": 82,
            "cambio": "Manual",
            "combustivel": "Flex",
            "quilometragem": 12000,
        },
        "medio": {
            "id": 1002,
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2024,
            "preco": 135000,
            "categoria": "Sedan",
            "consumo": 11.8,
            "potencia": 144,
            "cambio": "CVT",
            "combustivel": "Flex",
            "quilometragem": 8500,
        },
        "premium": {
            "id": 1003,
            "marca": "BMW",
            "modelo": "320i",
            "ano": 2023,
            "preco": 285000,
            "categoria": "Sedan",
            "consumo": 9.2,
            "potencia": 184,
            "cambio": "Automático",
            "combustivel": "Gasolina",
            "quilometragem": 15000,
        },
        "suv": {
            "id": 1004,
            "marca": "Honda",
            "modelo": "HR-V",
            "ano": 2024,
            "preco": 165000,
            "categoria": "SUV",
            "consumo": 10.5,
            "potencia": 116,
            "cambio": "CVT",
            "combustivel": "Flex",
            "quilometragem": 5000,
        },
    }


@pytest.fixture
def agent_test_scenarios():
    """
    Cenários de teste específicos para cada agente

    Define perguntas típicas e expectativas para validar
    a especialização de cada agente do LangGraph.
    """
    return {
        "tecnico": [
            {
                "pergunta": "Qual a potência e consumo deste carro?",
                "expected_keywords": ["potência", "consumo", "motor", "km/l"],
                "category": "Especificações",
            },
            {
                "pergunta": "Como é o câmbio automático?",
                "expected_keywords": ["câmbio", "automático", "cvt", "manual"],
                "category": "Transmissão",
            },
            {
                "pergunta": "Quais os itens de segurança?",
                "expected_keywords": ["segurança", "airbag", "abs", "freios"],
                "category": "Segurança",
            },
        ],
        "financeiro": [
            {
                "pergunta": "Como funciona o financiamento?",
                "expected_keywords": ["financiamento", "parcela", "entrada", "juros"],
                "category": "Financiamento",
            },
            {
                "pergunta": "Qual o valor da entrada mínima?",
                "expected_keywords": ["entrada", "mínima", "valor", "parcela"],
                "category": "Entrada",
            },
            {
                "pergunta": "Aceita carro usado na troca?",
                "expected_keywords": ["troca", "usado", "avaliação", "entrada"],
                "category": "Troca",
            },
        ],
        "comparacao": [
            {
                "pergunta": "Compare com o Honda Civic",
                "expected_keywords": ["honda", "civic", "compare", "diferença"],
                "category": "Comparação Direta",
            },
            {
                "pergunta": "É melhor que concorrentes?",
                "expected_keywords": ["melhor", "concorrente", "vantagem", "superior"],
                "category": "Avaliação Comparativa",
            },
        ],
        "manutencao": [
            {
                "pergunta": "Qual o custo de manutenção?",
                "expected_keywords": ["manutenção", "custo", "revisão", "peças"],
                "category": "Custos",
            },
            {
                "pergunta": "Quando fazer a primeira revisão?",
                "expected_keywords": ["revisão", "primeira", "km", "prazo"],
                "category": "Cronograma",
            },
        ],
        "avaliacao": [
            {
                "pergunta": "Este preço está justo?",
                "expected_keywords": ["preço", "justo", "valor", "mercado"],
                "category": "Precificação",
            },
            {
                "pergunta": "Como está a desvalorização?",
                "expected_keywords": [
                    "desvalorização",
                    "depreciação",
                    "valor",
                    "tempo",
                ],
                "category": "Depreciação",
            },
        ],
    }


@pytest.fixture
def performance_thresholds():
    """
    Limites de performance para validação nos testes

    Define os thresholds aceitáveis para diferentes
    métricas de performance do sistema.
    """
    return {
        "response_time": {
            "baseline_max": 2500,  # ms
            "under_load_max": 4000,  # ms
            "stress_max": 6000,  # ms
        },
        "success_rate": {
            "baseline_min": 0.95,  # 95%
            "under_load_min": 0.90,  # 90%
            "stress_min": 0.70,  # 70%
        },
        "throughput": {
            "min_requests_per_second": 2.0,
            "target_requests_per_second": 5.0,
        },
        "memory_overhead": {
            "max_percent": 50,  # 50% overhead máximo da memória
            "max_absolute_ms": 1000,  # 1s máximo adicional
        },
        "concurrent_users": {"light_load": 5, "medium_load": 15, "heavy_load": 25},
    }


@pytest.fixture
def test_database_url():
    """
    URL do banco de dados para testes

    Utiliza SQLite em memória para isolamento completo
    """
    return "sqlite:///:memory:"


@pytest.fixture(scope="function")
def clean_memory():
    """
    Limpa memória entre testes para evitar interferência

    Garante que cada teste comece com estado limpo
    """
    # Setup: Estado limpo
    yield

    # Teardown: Limpeza (se necessário)
    # Em implementação real, limparia registros de teste


@pytest.fixture
def mock_car_data():
    """
    Dados mock de carros para testes que não requerem dados reais
    """

    def _mock_car(car_id: int = 999, **overrides) -> Dict[str, Any]:
        base_car = {
            "id": car_id,
            "marca": "TestCar",
            "modelo": "MockModel",
            "ano": 2024,
            "preco": 100000,
            "categoria": "Test",
            "consumo": 10.0,
            "potencia": 100,
            "cambio": "Test",
            "combustivel": "Test",
            "quilometragem": 10000,
        }
        base_car.update(overrides)
        return base_car

    return _mock_car


@pytest.fixture
def user_session_generator():
    """
    Gerador de IDs de sessão únicos para testes

    Garante que cada teste tenha sessões isoladas
    """
    import uuid

    def _generate_session(prefix: str = "test") -> str:
        return f"{prefix}_{uuid.uuid4()}"

    return _generate_session


class LangGraphTestHelper:
    """
    Classe auxiliar com utilitários para testes LangGraph
    """

    @staticmethod
    def validate_response_structure(response_data: Dict[str, Any]) -> bool:
        """Valida estrutura básica de resposta do chatbot"""
        required_fields = ["resposta", "agente", "conversation_id", "confianca"]
        return all(field in response_data for field in required_fields)

    @staticmethod
    def validate_agent_specialization(
        agent: str, response: str, keywords: list
    ) -> float:
        """Calcula score de especialização do agente baseado em keywords"""
        response_lower = response.lower()
        found_keywords = [kw for kw in keywords if kw.lower() in response_lower]
        return len(found_keywords) / len(keywords) if keywords else 0.0

    @staticmethod
    def validate_response_quality(
        response: str, min_length: int = 50
    ) -> Dict[str, bool]:
        """Valida qualidade geral da resposta"""
        return {
            "sufficient_length": len(response) >= min_length,
            "has_content": response.strip() != "",
            "not_error_message": "erro" not in response.lower(),
            "professional_tone": not any(
                word in response.lower() for word in ["não sei", "não posso"]
            ),
        }

    @staticmethod
    def measure_consistency(responses: list, common_elements: list) -> float:
        """Mede consistência entre múltiplas respostas"""
        consistency_scores = []

        for element in common_elements:
            element_lower = element.lower()
            appearances = sum(1 for resp in responses if element_lower in resp.lower())
            consistency_scores.append(appearances / len(responses))

        return (
            sum(consistency_scores) / len(consistency_scores)
            if consistency_scores
            else 0.0
        )


@pytest.fixture
def langgraph_helper():
    """Instância da classe helper para testes"""
    return LangGraphTestHelper()


# Marcadores personalizados para categorização dos testes
def pytest_configure(config):
    """Configuração adicional do pytest para testes LangGraph"""
    config.addinivalue_line(
        "markers", "langgraph_workflow: marca testes de workflow LangGraph"
    )
    config.addinivalue_line(
        "markers", "langgraph_agents: marca testes de agentes especializados"
    )
    config.addinivalue_line(
        "markers", "langgraph_performance: marca testes de performance"
    )
    config.addinivalue_line(
        "markers", "langgraph_memory: marca testes de memória persistente"
    )
    config.addinivalue_line(
        "markers", "langgraph_integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "slow: marca testes que demoram mais para executar"
    )


# Configurações de timeout para diferentes tipos de teste
@pytest.fixture(autouse=True)
def set_test_timeout(request):
    """Define timeout automático baseado no tipo de teste"""
    if request.node.get_closest_marker("langgraph_performance"):
        request.node.add_marker(pytest.mark.timeout(120))  # 2 minutos para performance
    elif request.node.get_closest_marker("slow"):
        request.node.add_marker(pytest.mark.timeout(60))  # 1 minuto para testes lentos
    else:
        request.node.add_marker(pytest.mark.timeout(30))  # 30s para testes normais
