"""
Testes para EconomyAgent
"""

import pytest
from unittest.mock import Mock, patch

from services.agents.economy_agent import EconomyAgent
from services.agents.cache_manager import CacheManager
from models.car import Car
from models.user_profile import UserProfile


class TestEconomyAgent:
    """Testes do EconomyAgent"""

    @pytest.fixture
    def cache_manager(self):
        """Cache manager para testes"""
        return CacheManager(redis_url=None, enable_redis=False)

    @pytest.fixture
    def economy_agent(self, cache_manager):
        """Economy agent para testes"""
        return EconomyAgent(cache_manager=cache_manager)

    @pytest.fixture
    def hatch_economico(self):
        """Hatch econômico (15 km/L)"""
        return Car(
            id="hatch-1",
            nome="Fiat Argo 1.0",
            marca="Fiat",
            modelo="Argo",
            ano=2023,
            preco=60000,
            quilometragem=10000,
            combustivel="Flex",
            categoria="Hatch",
            consumo_cidade=15.2,
            consumo_estrada=17.0,
            score_economia=0.9,
            itens_seguranca=["ABS"],
            itens_conforto=["Ar"],
            dealership_id="d1",
            dealership_name="Dealer 1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )

    @pytest.fixture
    def suv_medio(self):
        """SUV consumo médio (10 km/L)"""
        return Car(
            id="suv-1",
            nome="Jeep Compass 2.0",
            marca="Jeep",
            modelo="Compass",
            ano=2023,
            preco=150000,
            quilometragem=5000,
            combustivel="Flex",
            categoria="SUV",
            consumo_cidade=9.8,
            consumo_estrada=11.5,
            score_economia=0.6,
            itens_seguranca=["ABS"],
            itens_conforto=["Ar"],
            dealership_id="d1",
            dealership_name="Dealer 1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )

    @pytest.fixture
    def profile_familia(self):
        """Perfil familiar padrão"""
        return UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            renda_mensal=5000
        )

    @pytest.mark.asyncio
    async def test_hatch_economico_high_score(
        self, economy_agent, hatch_economico, profile_familia
    ):
        """Testa que hatch econômico recebe score bom"""
        score = await economy_agent.calculate_score(hatch_economico, profile_familia)

        # Hatch com 15.2 km/L é muito bom, deve ter score > 0.55
        # (custo mensal ainda pesa no cálculo final)
        assert score > 0.55
        assert score <= 1.0

    @pytest.mark.asyncio
    async def test_suv_medio_medium_score(
        self, economy_agent, suv_medio, profile_familia
    ):
        """Testa que SUV com consumo médio recebe score médio"""
        score = await economy_agent.calculate_score(suv_medio, profile_familia)

        # SUV com 9.8 km/L é médio para categoria, deve ter score ~0.5-0.7
        assert 0.4 <= score <= 0.8

    @pytest.mark.asyncio
    async def test_hatch_vs_suv_same_consumption(
        self, economy_agent, profile_familia
    ):
        """Testa que normalização por categoria funciona"""
        # Dois carros com MESMO consumo (12 km/L)
        hatch = Car(
            id="h1",
            nome="Hatch Test",
            marca="Test",
            modelo="H",
            ano=2023,
            preco=50000,
            quilometragem=0,
            combustivel="Flex",
            categoria="Hatch",
            consumo_cidade=12.0,  # Abaixo da média de Hatch (13.5)
            itens_seguranca=[],
            itens_conforto=[],
            dealership_id="d1",
            dealership_name="D1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )

        suv = Car(
            id="s1",
            nome="SUV Test",
            marca="Test",
            modelo="S",
            ano=2023,
            preco=80000,
            quilometragem=0,
            combustivel="Flex",
            categoria="SUV",
            consumo_cidade=12.0,  # ACIMA da média de SUV (9.5)
            itens_seguranca=[],
            itens_conforto=[],
            dealership_id="d1",
            dealership_name="D1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )

        score_hatch = await economy_agent.calculate_score(hatch, profile_familia)
        score_suv = await economy_agent.calculate_score(suv, profile_familia)

        # SUV deve ter score MAIOR porque 12 km/L é excelente para SUV
        # mas apenas médio para Hatch
        assert score_suv > score_hatch

    @pytest.mark.asyncio
    async def test_fuel_type_bonus(self, economy_agent, profile_familia):
        """Testa que tipo de combustível afeta score"""
        base_car_data = {
            "id": "test",
            "nome": "Test",
            "marca": "Test",
            "modelo": "Test",
            "ano": 2023,
            "preco": 60000,
            "quilometragem": 0,
            "categoria": "Hatch",
            "consumo_cidade": 13.0,
            "itens_seguranca": [],
            "itens_conforto": [],
            "dealership_id": "d1",
            "dealership_name": "D1",
            "dealership_city": "SP",
            "dealership_state": "SP",
            "dealership_phone": "11",
            "dealership_whatsapp": "11"
        }

        # Flex (bonus alto)
        car_flex = Car(**{**base_car_data, "combustivel": "Flex"})
        # Gasolina (bonus baixo)
        car_gasolina = Car(**{**base_car_data, "combustivel": "Gasolina"})

        score_flex = await economy_agent.calculate_score(car_flex, profile_familia)
        score_gasolina = await economy_agent.calculate_score(car_gasolina, profile_familia)

        # Flex deve ter score levemente maior (bonus 10%)
        assert score_flex >= score_gasolina

    @pytest.mark.asyncio
    async def test_different_monthly_km_by_usage(self, economy_agent):
        """Testa que km mensal varia por uso principal"""
        car = Car(
            id="test",
            nome="Test",
            marca="Test",
            modelo="Test",
            ano=2023,
            preco=60000,
            quilometragem=0,
            combustivel="Flex",
            categoria="Hatch",
            consumo_cidade=13.0,
            itens_seguranca=[],
            itens_conforto=[],
            dealership_id="d1",
            dealership_name="D1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )

        # Comercial (alto km)
        profile_comercial = UserProfile(
            orcamento_min=50000,
            orcamento_max=80000,
            uso_principal="comercial",
            tamanho_familia=1,
            renda_mensal=5000
        )

        # Lazer (baixo km)
        profile_lazer = UserProfile(
            orcamento_min=50000,
            orcamento_max=80000,
            uso_principal="lazer",
            tamanho_familia=2,
            renda_mensal=5000
        )

        score_comercial = await economy_agent.calculate_score(car, profile_comercial)
        score_lazer = await economy_agent.calculate_score(car, profile_lazer)

        # Lazer deve ter score melhor (menor custo mensal)
        # porque roda menos km
        assert score_lazer >= score_comercial

    @pytest.mark.asyncio
    async def test_fallback_when_no_consumption_data(
        self, economy_agent, profile_familia
    ):
        """Testa fallback quando não há dados de consumo"""
        car_sem_consumo = Car(
            id="test",
            nome="Test",
            marca="Test",
            modelo="Test",
            ano=2023,
            preco=60000,
            quilometragem=0,
            combustivel="Flex",
            categoria="Hatch",
            # SEM consumo_cidade, consumo_estrada, consumo
            score_economia=0.75,  # Tem score genérico
            itens_seguranca=[],
            itens_conforto=[],
            dealership_id="d1",
            dealership_name="D1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )

        score = await economy_agent.calculate_score(car_sem_consumo, profile_familia)

        # Deve usar estimativa por categoria ou fallback
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_cache_works(self, economy_agent, hatch_economico, profile_familia):
        """Testa que cache funciona corretamente"""
        # Primeira chamada - cache miss
        score1 = await economy_agent.calculate_score_with_cache(
            hatch_economico, profile_familia
        )

        # Segunda chamada - cache hit
        score2 = await economy_agent.calculate_score_with_cache(
            hatch_economico, profile_familia
        )

        # Scores devem ser iguais
        assert score1 == score2

        # Verificar métricas
        metrics = economy_agent.get_metrics()
        assert metrics['total_calls'] == 2
        assert metrics['cache_hits'] == 1  # Segunda chamada foi hit
        assert metrics['cache_misses'] == 1  # Primeira chamada foi miss

    @pytest.mark.asyncio
    async def test_fuel_efficiency_priority(self, economy_agent):
        """Testa prioridade de consumo: cidade > estrada > consumo > categoria"""
        # Carro com todos os consumos
        car_completo = Car(
            id="test",
            nome="Test",
            marca="Test",
            modelo="Test",
            ano=2023,
            preco=60000,
            quilometragem=0,
            combustivel="Flex",
            categoria="Hatch",
            consumo_cidade=15.0,  # Deve usar este
            consumo_estrada=18.0,
            consumo=16.0,
            itens_seguranca=[],
            itens_conforto=[],
            dealership_id="d1",
            dealership_name="D1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )

        efficiency = economy_agent._get_fuel_efficiency(car_completo)

        # Deve usar consumo_cidade (prioridade 1)
        assert efficiency == 15.0

    @pytest.mark.asyncio
    async def test_cost_penalization_by_income(self, economy_agent, hatch_economico):
        """Testa penalização quando custo é alto em relação à renda"""
        # Perfil com renda baixa
        profile_renda_baixa = UserProfile(
            orcamento_min=50000,
            orcamento_max=70000,
            uso_principal="trabalho",
            tamanho_familia=1,
            renda_mensal=2000  # Renda baixa
        )

        # Perfil com renda alta
        profile_renda_alta = UserProfile(
            orcamento_min=50000,
            orcamento_max=70000,
            uso_principal="trabalho",
            tamanho_familia=1,
            renda_mensal=10000  # Renda alta
        )

        score_baixa = await economy_agent.calculate_score(
            hatch_economico, profile_renda_baixa
        )
        score_alta = await economy_agent.calculate_score(
            hatch_economico, profile_renda_alta
        )

        # Score deve ser melhor para quem tem renda alta
        # (mesmo custo absoluto representa % menor da renda)
        assert score_alta >= score_baixa

    def test_normalize_fuel_efficiency_by_category(self, economy_agent):
        """Testa normalização por categoria"""
        # Hatch com 15 km/L (excelente para Hatch)
        score_hatch = economy_agent._normalize_fuel_efficiency(15.0, "Hatch")

        # SUV com 15 km/L (EXCEPCIONAL para SUV)
        score_suv = economy_agent._normalize_fuel_efficiency(15.0, "SUV")

        # SUV deve ter score maior (15 km/L é muito acima da média de SUV)
        assert score_suv > score_hatch
        assert score_suv > 0.9  # Deve ser muito alto

    def test_normalize_fuel_cost(self, economy_agent):
        """Testa normalização de custo mensal"""
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            renda_mensal=5000
        )

        # Custo baixo (R$ 200/mês)
        score_low = economy_agent._normalize_fuel_cost(200, profile)

        # Custo médio (R$ 500/mês)
        score_mid = economy_agent._normalize_fuel_cost(500, profile)

        # Custo alto (R$ 800/mês)
        score_high = economy_agent._normalize_fuel_cost(800, profile)

        # Menor custo = maior score
        assert score_low > score_mid > score_high
        assert score_low > 0.8
        assert score_high < 0.3

    def test_cache_ttl_is_7_days(self, economy_agent):
        """Testa que TTL do cache é 7 dias"""
        ttl = economy_agent._get_cache_ttl()

        assert ttl == 7 * 24 * 3600  # 7 dias em segundos
