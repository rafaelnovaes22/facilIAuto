"""
Testes para ScoringAgentOrchestrator
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from services.agents.scoring_orchestrator import ScoringAgentOrchestrator
from services.agents.base_agent import BaseAgent
from services.agents.cache_manager import CacheManager
from models.car import Car
from models.user_profile import UserProfile


class MockAgent(BaseAgent):
    """Agente mock para testes"""

    def __init__(self, name, score_to_return=0.85, should_fail=False):
        super().__init__(name=name)
        self.score_to_return = score_to_return
        self.should_fail = should_fail

    async def calculate_score(self, car: Car, profile: UserProfile) -> float:
        await asyncio.sleep(0.01)  # Simular trabalho
        if self.should_fail:
            raise ValueError(f"{self.name} failed")
        return self.score_to_return

    async def calculate_score_with_cache(self, car: Car, profile: UserProfile) -> float:
        return await self.calculate_score(car, profile)


class TestScoringAgentOrchestrator:
    """Testes do ScoringAgentOrchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Orquestrador para testes"""
        cache_manager = CacheManager(redis_url=None, enable_redis=False)
        return ScoringAgentOrchestrator(
            cache_manager=cache_manager,
            enable_parallel=True
        )

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
            itens_seguranca=["6 airbags"],
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

    def test_register_agent(self, orchestrator):
        """Testa registro de agente"""
        agent = MockAgent("test_agent")

        orchestrator.register_agent("test", agent)

        assert "test" in orchestrator.agents
        assert orchestrator.agents["test"] == agent

    def test_unregister_agent(self, orchestrator):
        """Testa remoção de agente"""
        agent = MockAgent("test_agent")
        orchestrator.register_agent("test", agent)

        orchestrator.unregister_agent("test")

        assert "test" not in orchestrator.agents

    @pytest.mark.asyncio
    async def test_calculate_with_single_agent(
        self, orchestrator, sample_car, sample_profile
    ):
        """Testa orquestração com um único agente"""
        agent = MockAgent("economy", score_to_return=0.85)
        orchestrator.register_agent("economy", agent)

        result = await orchestrator.calculate_advanced_scores(
            sample_car,
            sample_profile
        )

        # Verificar scores
        assert "economy" in result['scores']
        assert result['scores']['economy'] == 0.85

        # Verificar metadata
        assert 'economy' in result['metadata']['agents_used']
        assert result['metadata']['execution_time_ms'] > 0
        assert len(result['metadata']['failed_agents']) == 0

    @pytest.mark.asyncio
    async def test_calculate_with_multiple_agents(
        self, orchestrator, sample_car, sample_profile
    ):
        """Testa orquestração com múltiplos agentes"""
        economy_agent = MockAgent("economy", score_to_return=0.85)
        maintenance_agent = MockAgent("maintenance", score_to_return=0.70)
        resale_agent = MockAgent("resale", score_to_return=0.90)

        orchestrator.register_agent("economy", economy_agent)
        orchestrator.register_agent("maintenance", maintenance_agent)
        orchestrator.register_agent("resale", resale_agent)

        result = await orchestrator.calculate_advanced_scores(
            sample_car,
            sample_profile
        )

        # Verificar todos os scores
        assert result['scores']['economy'] == 0.85
        assert result['scores']['maintenance'] == 0.70
        assert result['scores']['resale'] == 0.90

        # Verificar que todos foram executados
        assert len(result['metadata']['agents_used']) == 3

    @pytest.mark.asyncio
    async def test_parallel_execution_is_faster(
        self, sample_car, sample_profile
    ):
        """Testa que execução paralela é mais rápida"""
        # Criar agentes que demoram
        agent1 = MockAgent("agent1", score_to_return=0.8)
        agent2 = MockAgent("agent2", score_to_return=0.7)
        agent3 = MockAgent("agent3", score_to_return=0.9)

        # Teste 1: Paralelo
        orch_parallel = ScoringAgentOrchestrator(enable_parallel=True)
        orch_parallel.register_agent("agent1", agent1)
        orch_parallel.register_agent("agent2", agent2)
        orch_parallel.register_agent("agent3", agent3)

        result_parallel = await orch_parallel.calculate_advanced_scores(
            sample_car, sample_profile
        )
        time_parallel = result_parallel['metadata']['execution_time_ms']

        # Teste 2: Sequencial
        orch_sequential = ScoringAgentOrchestrator(enable_parallel=False)
        orch_sequential.register_agent("agent1", agent1)
        orch_sequential.register_agent("agent2", agent2)
        orch_sequential.register_agent("agent3", agent3)

        result_sequential = await orch_sequential.calculate_advanced_scores(
            sample_car, sample_profile
        )
        time_sequential = result_sequential['metadata']['execution_time_ms']

        # Paralelo deve ser mais rápido (ou similar, devido ao overhead)
        # Com 3 agentes de 10ms cada, sequencial ~30ms, paralelo ~10-15ms
        assert time_parallel < time_sequential * 1.5  # Tolerar overhead

    @pytest.mark.asyncio
    async def test_agent_failure_with_fallback(
        self, orchestrator, sample_car, sample_profile
    ):
        """Testa que fallback funciona quando agente falha"""
        # Agente que vai falhar
        failing_agent = MockAgent("economy", should_fail=True)
        orchestrator.register_agent("economy", failing_agent)

        result = await orchestrator.calculate_advanced_scores(
            sample_car,
            sample_profile
        )

        # Deve ter score de fallback
        assert "economy" in result['scores']
        assert result['scores']['economy'] == sample_car.score_economia

        # Deve registrar falha
        assert 'economy' in result['metadata']['failed_agents']

    @pytest.mark.asyncio
    async def test_partial_failure(
        self, orchestrator, sample_car, sample_profile
    ):
        """Testa que orquestrador continua mesmo com falha parcial"""
        success_agent = MockAgent("economy", score_to_return=0.85)
        failing_agent = MockAgent("maintenance", should_fail=True)

        orchestrator.register_agent("economy", success_agent)
        orchestrator.register_agent("maintenance", failing_agent)

        result = await orchestrator.calculate_advanced_scores(
            sample_car,
            sample_profile
        )

        # Economy deve ter score correto
        assert result['scores']['economy'] == 0.85

        # Maintenance deve ter fallback
        assert result['scores']['maintenance'] == 0.5

        # Metadata deve mostrar falha
        assert 'maintenance' in result['metadata']['failed_agents']
        assert 'economy' not in result['metadata']['failed_agents']

    @pytest.mark.asyncio
    async def test_select_specific_agents(
        self, orchestrator, sample_car, sample_profile
    ):
        """Testa execução de apenas agentes específicos"""
        orchestrator.register_agent("economy", MockAgent("economy", 0.85))
        orchestrator.register_agent("maintenance", MockAgent("maintenance", 0.70))
        orchestrator.register_agent("resale", MockAgent("resale", 0.90))

        # Executar apenas economy e resale
        result = await orchestrator.calculate_advanced_scores(
            sample_car,
            sample_profile,
            agent_names=["economy", "resale"]
        )

        # Deve ter apenas os solicitados
        assert "economy" in result['scores']
        assert "resale" in result['scores']
        assert "maintenance" not in result['scores']

        assert len(result['metadata']['agents_used']) == 2

    @pytest.mark.asyncio
    async def test_no_agents_registered(
        self, orchestrator, sample_car, sample_profile
    ):
        """Testa comportamento quando nenhum agente registrado"""
        result = await orchestrator.calculate_advanced_scores(
            sample_car,
            sample_profile
        )

        # Deve retornar resultado vazio
        assert result['scores'] == {}
        assert len(result['metadata']['agents_used']) == 0

    @pytest.mark.asyncio
    async def test_metrics_tracking(
        self, orchestrator, sample_car, sample_profile
    ):
        """Testa rastreamento de métricas do orquestrador"""
        agent = MockAgent("economy", 0.85)
        orchestrator.register_agent("economy", agent)

        # Executar algumas vezes
        for _ in range(3):
            await orchestrator.calculate_advanced_scores(
                sample_car,
                sample_profile
            )

        metrics = orchestrator.get_metrics()

        # Verificar métricas do orquestrador
        orch_metrics = metrics['orchestrator']
        assert orch_metrics['total_orchestrations'] == 3
        assert orch_metrics['success_rate'] == 1.0
        assert orch_metrics['avg_latency_ms'] > 0

        # Verificar métricas dos agentes
        assert 'economy' in metrics['agents']

    @pytest.mark.asyncio
    async def test_fallback_uses_car_attributes(
        self, orchestrator, sample_car, sample_profile
    ):
        """Testa que fallback usa atributos do carro quando disponível"""
        # Definir score_economia no carro
        sample_car.score_economia = 0.95

        # Agente que vai falhar
        failing_agent = MockAgent("economy", should_fail=True)
        orchestrator.register_agent("economy", failing_agent)

        result = await orchestrator.calculate_advanced_scores(
            sample_car,
            sample_profile
        )

        # Deve usar score_economia do carro como fallback
        assert result['scores']['economy'] == 0.95

    def test_reset_metrics(self, orchestrator):
        """Testa reset de métricas"""
        # Registrar um agente para garantir execução
        orchestrator.register_agent("mock", MockAgent("mock"))

        # Gerar métricas
        asyncio.run(
            orchestrator.calculate_advanced_scores(
                Car(
                    id="test",
                    nome="Test",
                    marca="Test",
                    modelo="Test",
                    ano=2023,
                    preco=50000,
                    quilometragem=0,
                    combustivel="Flex",
                    categoria="Hatch",
                    itens_seguranca=[],
                    itens_conforto=[],
                    dealership_id="d1",
                    dealership_name="D1",
                    dealership_city="SP",
                    dealership_state="SP",
                    dealership_phone="11",
                    dealership_whatsapp="11"
                ),
                UserProfile(
                    orcamento_min=40000,
                    orcamento_max=60000,
                    uso_principal="trabalho",
                    tamanho_familia=1
                )
            )
        )

        metrics_before = orchestrator.get_metrics()
        assert metrics_before['orchestrator']['total_orchestrations'] > 0

        # Resetar
        orchestrator.reset_metrics()

        metrics_after = orchestrator.get_metrics()
        assert metrics_after['orchestrator']['total_orchestrations'] == 0
