"""
Testes para MaintenanceAgent
"""

import pytest
from unittest.mock import Mock

from services.agents.maintenance_agent import MaintenanceAgent
from services.agents.cache_manager import CacheManager
from models.car import Car
from models.user_profile import UserProfile


class TestMaintenanceAgent:
    """Testes do MaintenanceAgent"""

    @pytest.fixture
    def cache_manager(self):
        """Cache manager para testes"""
        return CacheManager(redis_url=None, enable_redis=False)

    @pytest.fixture
    def maintenance_agent(self, cache_manager):
        """Maintenance agent para testes"""
        return MaintenanceAgent(cache_manager=cache_manager)

    @pytest.fixture
    def toyota_novo(self):
        """Toyota novo (confiável + baixo custo)"""
        return Car(
            id="toyota-1",
            nome="Toyota Corolla 2.0",
            marca="Toyota",
            modelo="Corolla",
            ano=2023,
            preco=120000,
            quilometragem=15000,
            combustivel="Flex",
            categoria="Sedan",
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
    def fiat_antigo(self):
        """Fiat antigo (menos confiável + alto km)"""
        return Car(
            id="fiat-1",
            nome="Fiat Palio 1.0",
            marca="Fiat",
            modelo="Palio",
            ano=2010,
            preco=25000,
            quilometragem=180000,
            combustivel="Flex",
            categoria="Hatch",
            itens_seguranca=["ABS"],
            itens_conforto=[],
            dealership_id="d1",
            dealership_name="Dealer 1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )

    @pytest.fixture
    def jeep_usado(self):
        """Jeep usado (problemas conhecidos)"""
        return Car(
            id="jeep-1",
            nome="Jeep Compass 2.0",
            marca="Jeep",
            modelo="Compass",
            ano=2019,
            preco=100000,
            quilometragem=80000,
            combustivel="Flex",
            categoria="SUV",
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
    def profile_padrao(self):
        """Perfil padrão"""
        return UserProfile(
            orcamento_min=50000,
            orcamento_max=150000,
            uso_principal="familia",
            tamanho_familia=4
        )

    @pytest.mark.asyncio
    async def test_toyota_novo_high_score(
        self, maintenance_agent, toyota_novo, profile_padrao
    ):
        """Testa que Toyota novo recebe score alto"""
        score = await maintenance_agent.calculate_score(toyota_novo, profile_padrao)

        # Toyota é confiável, novo, baixo km → score alto
        assert score > 0.7
        assert score <= 1.0

    @pytest.mark.asyncio
    async def test_fiat_antigo_low_score(
        self, maintenance_agent, fiat_antigo, profile_padrao
    ):
        """Testa que Fiat antigo recebe score baixo"""
        score = await maintenance_agent.calculate_score(fiat_antigo, profile_padrao)

        # Fiat menos confiável, antigo (14 anos), alto km (180k) → score baixo
        assert score < 0.6

    @pytest.mark.asyncio
    async def test_toyota_vs_fiat_same_age(
        self, maintenance_agent, profile_padrao
    ):
        """Testa que marca afeta score (mesma idade/km)"""
        # Dois carros com mesma idade e km
        toyota = Car(
            id="t1",
            nome="Toyota Test",
            marca="Toyota",
            modelo="Test",
            ano=2020,
            preco=80000,
            quilometragem=60000,
            combustivel="Flex",
            categoria="Sedan",
            itens_seguranca=[],
            itens_conforto=[],
            dealership_id="d1",
            dealership_name="D1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )

        fiat = Car(
            id="f1",
            nome="Fiat Test",
            marca="Fiat",
            modelo="Test",
            ano=2020,
            preco=60000,
            quilometragem=60000,
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
        )

        score_toyota = await maintenance_agent.calculate_score(toyota, profile_padrao)
        score_fiat = await maintenance_agent.calculate_score(fiat, profile_padrao)

        # Toyota deve ter score maior (mais confiável + custo menor)
        assert score_toyota > score_fiat

    @pytest.mark.asyncio
    async def test_jeep_problemas_conhecidos(
        self, maintenance_agent, jeep_usado, profile_padrao
    ):
        """Testa penalização por problemas conhecidos"""
        score = await maintenance_agent.calculate_score(jeep_usado, profile_padrao)

        # Jeep tem problemas conhecidos → penalização
        # Score deve ser médio/baixo
        assert score < 0.7

    @pytest.mark.asyncio
    async def test_age_affects_cost(self, maintenance_agent):
        """Testa que idade afeta custo de manutenção"""
        marca = "Toyota"
        quilometragem = 50000

        # Carro novo (2023)
        cost_new = maintenance_agent._calculate_annual_cost(marca, 2023, quilometragem)

        # Carro antigo (2015 - 9 anos)
        cost_old = maintenance_agent._calculate_annual_cost(marca, 2015, quilometragem)

        # Carro antigo deve ter custo maior
        assert cost_old > cost_new

        # Diferença deve ser significativa (idade aumenta 10% ao ano)
        # 9 anos × 10% = 90% de aumento
        assert cost_old >= cost_new * 1.5  # Pelo menos 50% mais caro

    @pytest.mark.asyncio
    async def test_mileage_affects_cost(self, maintenance_agent):
        """Testa que quilometragem afeta custo"""
        marca = "Honda"
        ano = 2020

        # Baixo km (30k)
        cost_low = maintenance_agent._calculate_annual_cost(marca, ano, 30000)

        # Alto km (150k)
        cost_high = maintenance_agent._calculate_annual_cost(marca, ano, 150000)

        # Alto km deve ter custo maior
        assert cost_high > cost_low

    def test_mileage_multiplier_tiers(self, maintenance_agent):
        """Testa faixas de multiplicador por km"""
        # Novo (< 30k)
        assert maintenance_agent._get_mileage_multiplier(20000) == 1.0

        # Baixo (30k-60k)
        assert maintenance_agent._get_mileage_multiplier(50000) == 1.1

        # Médio (60k-100k)
        assert maintenance_agent._get_mileage_multiplier(80000) == 1.2

        # Alto (100k-150k)
        assert maintenance_agent._get_mileage_multiplier(120000) == 1.4

        # Muito alto (> 150k)
        assert maintenance_agent._get_mileage_multiplier(180000) == 1.7

    def test_brand_reliability(self, maintenance_agent):
        """Testa índice de confiabilidade por marca"""
        # Toyota é muito confiável
        toyota_rel = maintenance_agent._get_brand_reliability("Toyota")
        assert toyota_rel >= 0.9

        # Fiat é menos confiável
        fiat_rel = maintenance_agent._get_brand_reliability("Fiat")
        assert fiat_rel < 0.8

        # Toyota > Fiat
        assert toyota_rel > fiat_rel

    def test_wear_penalty_by_age(self, maintenance_agent):
        """Testa penalização por idade"""
        # Novo (2023 - 1 ano)
        penalty_new = maintenance_agent._calculate_wear_penalty(2023, 30000)

        # Antigo (2010 - 14 anos)
        penalty_old = maintenance_agent._calculate_wear_penalty(2010, 30000)

        # Carro antigo deve ter mais penalização
        assert penalty_old > penalty_new

    def test_wear_penalty_by_mileage(self, maintenance_agent):
        """Testa penalização por quilometragem"""
        ano = 2020

        # Baixo km
        penalty_low = maintenance_agent._calculate_wear_penalty(ano, 40000)

        # Alto km
        penalty_high = maintenance_agent._calculate_wear_penalty(ano, 180000)

        # Alto km deve ter mais penalização
        assert penalty_high > penalty_low

    def test_known_issues_penalty(self, maintenance_agent):
        """Testa penalização por problemas conhecidos"""
        # Jeep tem 2 problemas conhecidos
        jeep_penalty = maintenance_agent._get_known_issues_penalty("Jeep")
        assert jeep_penalty == 0.2

        # Toyota não tem problemas conhecidos
        toyota_penalty = maintenance_agent._get_known_issues_penalty("Toyota")
        assert toyota_penalty == 0.0

    def test_normalize_cost(self, maintenance_agent):
        """Testa normalização de custo"""
        # Custo muito baixo (R$ 1.500/ano)
        score_low = maintenance_agent._normalize_cost(1500)
        assert score_low == 1.0

        # Custo médio (R$ 4.000/ano)
        score_mid = maintenance_agent._normalize_cost(4000)
        assert 0.3 < score_mid < 0.7

        # Custo muito alto (R$ 8.000/ano)
        score_high = maintenance_agent._normalize_cost(8000)
        assert score_high == 0.0

        # Menor custo = maior score
        assert score_low > score_mid > score_high

    @pytest.mark.asyncio
    async def test_cache_works(
        self, maintenance_agent, toyota_novo, profile_padrao
    ):
        """Testa que cache funciona"""
        # Primeira chamada - cache miss
        score1 = await maintenance_agent.calculate_score_with_cache(
            toyota_novo, profile_padrao
        )

        # Segunda chamada - cache hit
        score2 = await maintenance_agent.calculate_score_with_cache(
            toyota_novo, profile_padrao
        )

        # Scores devem ser iguais
        assert score1 == score2

        # Verificar métricas
        metrics = maintenance_agent.get_metrics()
        assert metrics['cache_hits'] >= 1

    def test_cache_ttl_is_30_days(self, maintenance_agent):
        """Testa que TTL do cache é 30 dias"""
        ttl = maintenance_agent._get_cache_ttl()

        assert ttl == 30 * 24 * 3600  # 30 dias em segundos

    def test_get_maintenance_breakdown(self, maintenance_agent, toyota_novo):
        """Testa método de detalhamento de manutenção"""
        breakdown = maintenance_agent.get_maintenance_breakdown(toyota_novo)

        # Verificar estrutura
        assert "custo_anual_estimado" in breakdown
        assert "custo_mensal_estimado" in breakdown
        assert "confiabilidade_marca" in breakdown
        assert "penalizacao_desgaste" in breakdown
        assert "penalizacao_problemas" in breakdown
        assert "problemas_conhecidos" in breakdown
        assert "idade_anos" in breakdown
        assert "quilometragem" in breakdown

        # Verificar valores
        assert breakdown["custo_anual_estimado"] > 0
        assert breakdown["custo_mensal_estimado"] > 0
        assert 0 <= breakdown["confiabilidade_marca"] <= 1
        assert 0 <= breakdown["penalizacao_desgaste"] <= 1

        # Custo mensal deve ser 1/12 do anual
        assert abs(
            breakdown["custo_mensal_estimado"] -
            breakdown["custo_anual_estimado"] / 12
        ) < 1.0  # Margem de arredondamento

    @pytest.mark.asyncio
    async def test_premium_brands_lower_score(
        self, maintenance_agent, profile_padrao
    ):
        """Testa que marcas premium têm score menor (custo alto)"""
        # BMW (premium, custo alto)
        bmw = Car(
            id="bmw-1",
            nome="BMW 320i",
            marca="BMW",
            modelo="320i",
            ano=2022,
            preco=200000,
            quilometragem=30000,
            combustivel="Gasolina",
            categoria="Sedan",
            itens_seguranca=[],
            itens_conforto=[],
            dealership_id="d1",
            dealership_name="D1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )

        # Toyota (popular, custo baixo)
        toyota = Car(
            id="toyota-1",
            nome="Toyota Corolla",
            marca="Toyota",
            modelo="Corolla",
            ano=2022,
            preco=120000,
            quilometragem=30000,
            combustivel="Flex",
            categoria="Sedan",
            itens_seguranca=[],
            itens_conforto=[],
            dealership_id="d1",
            dealership_name="D1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )

        score_bmw = await maintenance_agent.calculate_score(bmw, profile_padrao)
        score_toyota = await maintenance_agent.calculate_score(toyota, profile_padrao)

        # Toyota deve ter score maior (custo menor + mais confiável)
        assert score_toyota > score_bmw
