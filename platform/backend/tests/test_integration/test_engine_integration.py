"""
Integration Tests for Recommendation Engine + Agents

Verifica a integração completa:
Engine -> Orchestrator -> Agents (Economy, Maintenance, Resale, Weights)
"""

import pytest
from unittest.mock import Mock, patch
from services.unified_recommendation_engine import UnifiedRecommendationEngine
from services.agents.scoring_orchestrator import ScoringAgentOrchestrator
from models.car import Car
from models.user_profile import UserProfile

# Mock do LLM Service para não falhar sem credenciais
@pytest.fixture
def mock_llm_service():
    with patch('services.unified_recommendation_engine.LLMJustificationService') as MockService:
        instance = MockService.return_value
        instance.generate_justification.return_value = "Justificativa Mock"
        yield MockService

@pytest.fixture
def engine(mock_llm_service):
    """Engine inicializada com mocks de dados"""
    # Usar use_llm=False para simplificar testes
    engine = UnifiedRecommendationEngine(data_dir="tests/data", use_llm=False)
    
    # Mock dos dados básicos
    engine.dealerships = []
    engine.all_cars = []
    
    return engine

@pytest.fixture
def sample_car():
    return Car(
        id="c1",
        nome="Toyota Corolla",
        marca="Toyota",
        modelo="Corolla",
        ano=2021,
        preco=120000,
        quilometragem=40000,
        combustivel="Flex",
        categoria="Sedan",
        score_economia=0.8,
        score_conforto=0.9,
        score_seguranca=0.9,
        score_performance=0.7,
        indice_revenda=0.9,
        dealership_id="d1",
        dealership_name="Dealer 1",
        dealership_city="SP",
        dealership_state="SP",
        dealership_phone="11",
        dealership_whatsapp="11"
    )

@pytest.fixture
def sample_profile():
    return UserProfile(
        orcamento_min=100000,
        orcamento_max=150000,
        uso_principal="familia",
        prioridades={"economia": 3, "conforto": 5, "seguranca": 5},
        tamanho_familia=4,
        renda_mensal=15000
    )

class TestEngineIntegration:
    
    def test_orchestrator_initialization(self, engine):
        """Testa se o orquestrador e agentes foram inicializados"""
        assert isinstance(engine.orchestrator, ScoringAgentOrchestrator)
        assert "economy" in engine.orchestrator.agents
        assert "maintenance" in engine.orchestrator.agents
        assert "resale" in engine.orchestrator.agents
        assert "weight_optimizer" in engine.orchestrator.agents

    @pytest.mark.asyncio
    async def test_calculate_advanced_match_score(self, engine, sample_car, sample_profile):
        """Testa o fluxo completo de cálculo de score avançado"""
        
        # Executar cálculo
        start_score = await engine.calculate_advanced_match_score(sample_car, sample_profile)
        
        # Verificações
        assert "final_score" in start_score
        assert "breakdown" in start_score
        assert "metadata" in start_score
        
        breakdown = start_score["breakdown"]
        metadata = start_score["metadata"]
        
        # Verificar se agentes foram usados
        assert "economy" in metadata["agents_used"]
        assert "maintenance" in metadata["agents_used"]
        assert "resale" in metadata["agents_used"]
        
        # Verificar se houve processamento real (score > 0)
        assert start_score["final_score"] > 0.0
        assert breakdown["agent_scores"]["economy"] > 0
    
    @pytest.mark.asyncio
    async def test_weight_optimizer_integration(self, engine, sample_car, sample_profile):
        """Testa se pesos personalizados estão sendo usados"""
        
        # Perfil família deve ter peso alto para segurança (prioridades) e categoria
        result = await engine.calculate_advanced_match_score(sample_car, sample_profile)
        weights = result["breakdown"]["weights_used"]
        
        # Verificar pesos de perfil família
        assert weights["category"] >= 0.40  # 0.40 no WeightOptimizer para familia
        assert weights["priorities"] >= 0.40

