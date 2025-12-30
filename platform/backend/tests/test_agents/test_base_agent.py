"""
Testes para BaseAgent
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from services.agents.base_agent import BaseAgent
from services.agents.cache_manager import CacheManager
from models.car import Car
from models.user_profile import UserProfile


class ConcreteAgent(BaseAgent):
    """Implementação concreta de BaseAgent para testes"""

    def __init__(self, cache_manager=None, score_to_return=0.85):
        super().__init__(cache_manager, name="TestAgent")
        self.score_to_return = score_to_return
        self.call_count = 0

    async def calculate_score(self, car: Car, profile: UserProfile) -> float:
        """Implementação de teste que retorna score fixo"""
        self.call_count += 1
        await asyncio.sleep(0.01)  # Simular trabalho
        return self.score_to_return


class TestBaseAgent:
    """Testes do BaseAgent"""

    @pytest.fixture
    def sample_car(self):
        """Carro de teste"""
        return Car(
            id="test-car-1",
            nome="Volkswagen Taos 1.4 TSI",
            marca="Volkswagen",
            modelo="Taos",
            ano=2023,
            preco=85000,
            quilometragem=20000,
            combustivel="Flex",
            categoria="SUV Compacto",
            consumo_cidade=11.0,
            consumo_estrada=13.5,
            score_economia=0.8,
            itens_seguranca=["6 airbags", "ABS"],
            itens_conforto=["Ar-condicionado"],
            dealership_id="dealer-1",
            dealership_name="Concessionária Teste",
            dealership_city="São Paulo",
            dealership_state="SP",
            dealership_phone="(11) 9999-9999",
            dealership_whatsapp="5511999999999"
        )

    @pytest.fixture
    def sample_profile(self):
        """Perfil de teste"""
        return UserProfile(
            orcamento_min=60000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4
        )

    @pytest.mark.asyncio
    async def test_concrete_agent_calculates_score(self, sample_car, sample_profile):
        """Testa que agente concreto calcula score corretamente"""
        agent = ConcreteAgent(score_to_return=0.85)

        score = await agent.calculate_score(sample_car, sample_profile)

        assert score == 0.85
        assert agent.call_count == 1

    @pytest.mark.asyncio
    async def test_calculate_score_with_cache_no_cache_manager(
        self, sample_car, sample_profile
    ):
        """Testa cálculo sem cache manager (fallback direto)"""
        agent = ConcreteAgent(cache_manager=None, score_to_return=0.75)

        score = await agent.calculate_score_with_cache(sample_car, sample_profile)

        assert score == 0.75
        assert agent.call_count == 1

    @pytest.mark.asyncio
    async def test_calculate_score_with_cache_miss(self, sample_car, sample_profile):
        """Testa cache miss - deve calcular e salvar"""
        cache_manager = Mock(spec=CacheManager)
        cache_manager.get = AsyncMock(return_value=None)  # Cache miss
        cache_manager.set = AsyncMock()

        agent = ConcreteAgent(cache_manager=cache_manager, score_to_return=0.80)

        score = await agent.calculate_score_with_cache(sample_car, sample_profile)

        # Verificar resultado
        assert score == 0.80
        assert agent.call_count == 1

        # Verificar que tentou buscar do cache
        assert cache_manager.get.called

        # Verificar que salvou no cache
        assert cache_manager.set.called

    @pytest.mark.asyncio
    async def test_calculate_score_with_cache_hit(self, sample_car, sample_profile):
        """Testa cache hit - NÃO deve calcular"""
        cache_manager = Mock(spec=CacheManager)
        cache_manager.get = AsyncMock(return_value=0.90)  # Cache hit

        agent = ConcreteAgent(cache_manager=cache_manager, score_to_return=0.80)

        score = await agent.calculate_score_with_cache(sample_car, sample_profile)

        # Verificar resultado do cache
        assert score == 0.90

        # Verificar que NÃO calculou (cache hit)
        assert agent.call_count == 0

        # Verificar métricas
        metrics = agent.get_metrics()
        assert metrics['cache_hits'] == 1
        assert metrics['cache_misses'] == 0

    @pytest.mark.asyncio
    async def test_validate_score_valid(self, sample_car, sample_profile):
        """Testa validação de score válido"""
        agent = ConcreteAgent(score_to_return=0.75)

        assert agent._validate_score(0.0) is True
        assert agent._validate_score(0.5) is True
        assert agent._validate_score(1.0) is True
        assert agent._validate_score(0.85) is True

    @pytest.mark.asyncio
    async def test_validate_score_invalid(self, sample_car, sample_profile):
        """Testa validação de score inválido"""
        agent = ConcreteAgent()

        # Fora do range
        assert agent._validate_score(-0.1) is False
        assert agent._validate_score(1.1) is False

        # Tipo errado
        assert agent._validate_score("0.5") is False
        assert agent._validate_score(None) is False

        # NaN/Inf
        assert agent._validate_score(float('nan')) is False
        assert agent._validate_score(float('inf')) is False

    @pytest.mark.asyncio
    async def test_fallback_on_invalid_score(self, sample_car, sample_profile):
        """Testa que usa fallback quando score é inválido"""
        agent = ConcreteAgent(score_to_return=1.5)  # Score inválido (>1.0)

        score = await agent.calculate_score_with_cache(sample_car, sample_profile)

        # Deve usar fallback (0.5 por padrão)
        assert score == 0.5

    @pytest.mark.asyncio
    async def test_metrics_tracking(self, sample_car, sample_profile):
        """Testa que métricas são rastreadas corretamente"""
        agent = ConcreteAgent(score_to_return=0.85)

        # Executar algumas vezes
        for _ in range(3):
            await agent.calculate_score_with_cache(sample_car, sample_profile)

        metrics = agent.get_metrics()

        assert metrics['total_calls'] == 3
        assert metrics['success_calls'] == 3
        assert metrics['failed_calls'] == 0
        assert metrics['success_rate'] == 1.0
        assert metrics['avg_latency_ms'] > 0

    @pytest.mark.asyncio
    async def test_metrics_with_failures(self, sample_car, sample_profile):
        """Testa métricas com falhas"""

        class FailingAgent(ConcreteAgent):
            async def calculate_score(self, car, profile):
                raise ValueError("Test error")

        agent = FailingAgent()

        # Executar (vai falhar)
        score = await agent.calculate_score_with_cache(sample_car, sample_profile)

        # Deve retornar fallback
        assert score == 0.5

        # Verificar métricas
        metrics = agent.get_metrics()
        assert metrics['failed_calls'] == 1
        assert metrics['success_rate'] == 0.0

    def test_build_cache_key(self, sample_car, sample_profile):
        """Testa construção de chave de cache"""
        agent = ConcreteAgent()

        key1 = agent._build_cache_key(sample_car, sample_profile)

        # Deve ser string
        assert isinstance(key1, str)

        # Deve conter nome do agente
        assert "TestAgent" in key1

        # Deve conter ID do carro
        assert sample_car.id in key1

        # Mesmos parâmetros = mesma chave
        key2 = agent._build_cache_key(sample_car, sample_profile)
        assert key1 == key2

    def test_get_fallback_score(self, sample_car):
        """Testa score de fallback padrão"""
        agent = ConcreteAgent()

        score = agent._get_fallback_score(sample_car)

        # Padrão é 0.5
        assert score == 0.5

    def test_get_cache_ttl(self):
        """Testa TTL padrão do cache"""
        agent = ConcreteAgent()

        ttl = agent._get_cache_ttl()

        # Padrão é 1 dia (86400 segundos)
        assert ttl == 86400

    def test_reset_metrics(self, sample_car, sample_profile):
        """Testa reset de métricas"""
        agent = ConcreteAgent()

        # Executar para gerar métricas
        asyncio.run(agent.calculate_score_with_cache(sample_car, sample_profile))

        metrics_before = agent.get_metrics()
        assert metrics_before['total_calls'] > 0

        # Resetar
        agent.reset_metrics()

        metrics_after = agent.get_metrics()
        assert metrics_after['total_calls'] == 0
        assert metrics_after['success_calls'] == 0
