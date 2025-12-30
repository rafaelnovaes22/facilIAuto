"""
Testes para ResaleAgent
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from services.agents.resale_agent import ResaleAgent
from services.agents.cache_manager import CacheManager
from models.car import Car
from models.user_profile import UserProfile


class TestResaleAgent:
    """Testes do ResaleAgent"""

    @pytest.fixture
    def cache_manager(self):
        """Cache manager para testes"""
        return CacheManager(redis_url=None, enable_redis=False)

    @pytest.fixture
    def resale_agent(self, cache_manager):
        """Resale agent para testes"""
        return ResaleAgent(cache_manager=cache_manager)

    @pytest.fixture
    def toyota_novo(self):
        """Toyota Corolla novo (alta revenda)"""
        current_year = datetime.now().year
        return Car(
            id="toyota-1",
            nome="Toyota Corolla Altis",
            marca="Toyota",
            modelo="Corolla",
            ano=current_year,
            preco=150000,
            quilometragem=0,
            combustivel="Flex",
            categoria="Sedan",
            itens_seguranca=["ABS", "Airbag"],
            itens_conforto=["Ar", "Couro"],
            dealership_id="d1",
            dealership_name="Dealer 1",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="11",
            dealership_whatsapp="11"
        )

    @pytest.fixture
    def peugeot_antigo(self):
        """Peugeot antigo (baixa revenda)"""
        current_year = datetime.now().year
        return Car(
            id="peugeot-1",
            nome="Peugeot 208",
            marca="Peugeot",
            modelo="208",
            ano=current_year - 5,
            preco=40000,
            quilometragem=80000,
            combustivel="Flex",
            categoria="Hatch",
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
    def profile(self):
        """Perfil padrão"""
        return UserProfile(
            orcamento_min=30000,
            orcamento_max=160000,
            uso_principal="dia_a_dia",
            tamanho_familia=2,
            renda_mensal=8000
        )

    @pytest.mark.asyncio
    async def test_toyota_high_resale_score(self, resale_agent, toyota_novo, profile):
        """Testa que Toyota novo tem score alto de revenda"""
        score = await resale_agent.calculate_score(toyota_novo, profile)

        # Toyota (0.75) + Novo (0.00 depreciation) + Sedan (0.75) + 0km (0.0 penalty)
        # Score deve ser alto
        assert score > 0.7
        assert score <= 1.0

    @pytest.mark.asyncio
    async def test_peugeot_low_resale_score(self, resale_agent, peugeot_antigo, profile):
        """Testa que Peugeot antigo tem score menor"""
        score = await resale_agent.calculate_score(peugeot_antigo, profile)

        # Peugeot (0.53) + 5 anos (~0.48 dep) + Hatch (0.85) + 80k km (0.10 pen)
        # Score deve ser menor que o Toyota novo
        assert score < 0.70

    @pytest.mark.asyncio
    async def test_brand_retention_difference(self, resale_agent, profile):
        """Testa diferença de retenção entre marcas"""
        # Carros idênticos exceto marca
        current_year = datetime.now().year
        base_car = {
            "id": "test",
            "modelo": "Test",
            "ano": current_year - 2,
            "preco": 80000,
            "quilometragem": 30000,
            "combustivel": "Flex",
            "categoria": "SUV",
            "itens_seguranca": [],
            "itens_conforto": [],
            "dealership_id": "d1",
            "dealership_name": "D1",
            "dealership_city": "SP",
            "dealership_state": "SP",
            "dealership_phone": "11",
            "dealership_whatsapp": "11"
        }

        honda = Car(**{**base_car, "nome": "Honda HR-V", "marca": "Honda"})
        land_rover = Car(**{**base_car, "nome": "Land Rover Evoque", "marca": "Land Rover"})

        score_honda = await resale_agent.calculate_score(honda, profile)
        score_land = await resale_agent.calculate_score(land_rover, profile)

        # Honda tem retenção muito melhor que Land Rover
        assert score_honda > score_land

    @pytest.mark.asyncio
    async def test_mileage_penalty(self, resale_agent, toyota_novo, profile):
        """Testa penalização por quilometragem"""
        # Carro novo com 0km
        score_0km = await resale_agent.calculate_score(toyota_novo, profile)

        # Mesmo carro com 150.000km
        toyota_rodado = toyota_novo.model_copy()
        toyota_rodado.quilometragem = 150000

        score_150k = await resale_agent.calculate_score(toyota_rodado, profile)

        # Score deve cair significativamente (diferença exata é 0.10)
        assert score_0km > score_150k + 0.09

    @pytest.mark.asyncio
    async def test_category_demand_impact(self, resale_agent, profile):
        """Testa impacto da demanda da categoria"""
        current_year = datetime.now().year
        base_car = {
            "id": "test",
            "marca": "Chevrolet",
            "modelo": "Test",
            "ano": current_year - 1,
            "preco": 90000,
            "quilometragem": 10000,
            "combustivel": "Flex",
            "itens_seguranca": [],
            "itens_conforto": [],
            "dealership_id": "d1",
            "dealership_name": "D1",
            "dealership_city": "SP",
            "dealership_state": "SP",
            "dealership_phone": "11",
            "dealership_whatsapp": "11"
        }

        # SUV (alta demanda)
        suv = Car(**{**base_car, "nome": "Tracker", "categoria": "SUV"})
        # Furgão (baixa demanda)
        van = Car(**{**base_car, "nome": "Fiorino", "categoria": "Furgão"})

        score_suv = await resale_agent.calculate_score(suv, profile)
        score_van = await resale_agent.calculate_score(van, profile)

        assert score_suv > score_van

    def test_age_depreciation_interpolation(self, resale_agent):
        """Testa interpolação da curva de depreciação"""
        # Ano 0: 0.0
        # Ano 1: 0.15
        dep_0 = resale_agent._calculate_age_depreciation(0)
        dep_1 = resale_agent._calculate_age_depreciation(1)
        
        # 6 meses deve ser aprox 0.075
        dep_half = resale_agent._calculate_age_depreciation(0.5)

        assert dep_0 == 0.0
        assert dep_1 == 0.15
        assert 0.05 < dep_half < 0.10

    @pytest.mark.asyncio
    async def test_estimate_resale_value_structure(self, resale_agent, toyota_novo):
        """Testa estrutura do retorno de estimate_resale_value"""
        result = resale_agent.estimate_resale_value(toyota_novo)

        assert "valor_estimado" in result
        assert "percentual_retencao" in result
        assert "preco_original" in result
        assert "facilidade_venda" in result
        
        # Como é Toyota novo, facilidade deve ser Alta ou Média
        assert result["facilidade_venda"] in ["Alta", "Média"]

    @pytest.mark.asyncio
    async def test_cache_ttl(self, resale_agent):
        """Testa TTL do cache"""
        ttl = resale_agent._get_cache_ttl()
        assert ttl == 14 * 24 * 3600  # 14 dias

    @pytest.mark.asyncio
    async def test_fallback_score(self, resale_agent, profile):
        """Testa score de fallback"""
        # Carro com marca desconhecida e erro simulado
        car = Car(
            id="unknown",
            nome="Unknown Car",
            marca="Unknown",
            modelo="Model",
            ano=2020,
            preco=50000,
            quilometragem=50000,
            combustivel="Gasolina",
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
        
        # Simular erro no cálculo
        with patch.object(resale_agent, '_get_brand_value_retention', side_effect=Exception("Error")):
            score = await resale_agent.calculate_score(car, profile)
            
            # Deve retornar fallback (0.5 ou retention se conseguir pegar antes do erro)
            # Como mockamos o primeiro passo com erro, deve cair no fallback geral do BaseAgent ou do catch do calculate_score
            # O ResaleAgent._get_fallback_score tenta chamar _get_brand_value_retention de novo.
            # Se mockarmos para falhar sempre, ele deve retornar 0.5.
            assert score == 0.5
