"""
Testes para WeightOptimizerAgent
"""

import pytest
from unittest.mock import Mock, patch

from services.agents.weight_optimizer_agent import WeightOptimizerAgent
from models.user_profile import UserProfile
from models.car import Car


class TestWeightOptimizerAgent:
    """Testes do WeightOptimizerAgent"""

    @pytest.fixture
    def optimizer(self):
        """Agente otimizador para testes com Semantic Service mockado"""
        agent = WeightOptimizerAgent(interaction_service=Mock())
        # Mockar o analisador semântico para não interferir nos testes de regressão
        agent.semantic_analyzer = Mock()
        agent.semantic_analyzer.analyze_profile.return_value = {}  # Sem ajuste por padrão
        return agent

    @pytest.fixture
    def profile(self):
        """Perfil base"""
        return UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="dia_a_dia",
            tamanho_familia=1,
            renda_mensal=5000
        )

    def test_default_weights(self, optimizer, profile):
        """Testa pesos padrão"""
        # Uso 'dia_a_dia' deve cair no default
        weights = optimizer.get_optimized_weights(profile)
        
        assert weights['category'] == 0.30
        assert weights['priorities'] == 0.40
        assert weights['preferences'] == 0.20
        assert weights['budget'] == 0.10

    def test_family_weights(self, optimizer):
        """Testa pesos para perfil família"""
        profile = UserProfile(
            orcamento_min=50, orcamento_max=100,
            uso_principal="familia",
            tamanho_familia=4,
            renda_mensal=5000
        )
        weights = optimizer.get_optimized_weights(profile)
        
        # Família prioriza categoria e prioridades (segurança/espaço)
        assert weights['category'] == 0.40
        assert weights['priorities'] == 0.45
        assert weights['budget'] == 0.05

    def test_commercial_weights(self, optimizer):
        """Testa pesos para perfil comercial"""
        profile = UserProfile(
            orcamento_min=50, orcamento_max=100,
            uso_principal="comercial",
            tamanho_familia=1,
            renda_mensal=5000
        )
        weights = optimizer.get_optimized_weights(profile)
        
        # Comercial prioriza categoria (tipo de veículo)
        assert weights['category'] == 0.45
        assert weights['priorities'] == 0.35

    def test_app_transport_weights(self, optimizer):
        """Testa pesos para transporte de app"""
        profile = UserProfile(
            orcamento_min=50, orcamento_max=100,
            uso_principal="transporte_passageiros",
            tamanho_familia=1,
            renda_mensal=5000
        )
        weights = optimizer.get_optimized_weights(profile)
        
        # Transporte prioriza categoria (aceitação no app)
        assert weights['category'] == 0.50

    @pytest.mark.asyncio
    async def test_calculate_score_returns_valid_float(self, optimizer, profile):
        """Testa que calculate_score retorna valor válido"""
        car = Car(
            id="test",
            nome="Test",
            marca="Test",
            modelo="Test",
            ano=2020,
            preco=50000,
            quilometragem=10000,
            combustivel="Flex",
            categoria="Hatch",
            dealership_id="d1",
            dealership_name="D1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )
        
        score = await optimizer.calculate_score(car, profile)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_weights_sum_approx_one(self, optimizer, profile):
        """Testa que soma dos pesos é aproximadamente 1.0"""
        weights = optimizer.get_optimized_weights(profile)
        
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.001

    def test_semantic_adjustment_blending(self, optimizer, profile):
        """Testa se o ajuste semântico (conexionista) influencia os pesos corretamente"""
        # Configurar mock para retornar ajuste
        # Ex: "Quero segurança" -> safety +0.2
        optimizer.semantic_analyzer.analyze_profile.return_value = {
            'safety': 0.2
        }
        
        # Perfil base (dia a dia)
        # Default: Cat 0.3, Prio 0.4, Pref 0.2, Budget 0.1
        
        weights = optimizer.get_optimized_weights(profile)
        
        # Lógica de projeção: 'safety' aumenta 'priorities'
        # macro['priorities'] += 0.2 * 0.5 = +0.1
        # Base Prio = 0.4 -> 0.4 + (0.1 * 0.5) = 0.45
        
        # O peso de 'priorities' deve ter aumentado em relação ao base
        assert weights['priorities'] > 0.40 
        assert weights['ml_adjusted'] is True
