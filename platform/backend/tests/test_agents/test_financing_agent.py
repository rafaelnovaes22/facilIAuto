
import pytest
from services.agents.financing_agent import FinancingAgent
from models.user_profile import UserProfile, FinancialCapacity
from models.car import Car

class TestFinancingAgent:
    
    @pytest.fixture
    def financing_agent(self):
        return FinancingAgent()
        
    @pytest.fixture
    def high_income_profile(self):
        return UserProfile(
            orcamento_min=100000,
            orcamento_max=150000,
            uso_principal="comercial",
            financial_capacity=FinancialCapacity(
                monthly_income_range="12000+",
                is_disclosed=True
            )
        )

    @pytest.fixture
    def low_income_profile(self):
        return UserProfile(
            orcamento_min=30000,
            orcamento_max=40000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="0-3000",
                is_disclosed=True
            ),
            tem_criancas=True
        )

    @pytest.fixture
    def unknown_profile(self):
        return UserProfile(
            orcamento_min=50000,
            orcamento_max=60000,
            uso_principal="lazer"
        )
        
    @pytest.fixture
    def sample_car(self):
        return Car(
            id="car_1",
            dealership_id="dealership_1",
            nome="Toyota Corolla Altis",
            marca="Toyota",
            modelo="Corolla",
            versao="Altis",
            ano=2022,
            preco=120000.0,
            quilometragem=15000,
            combustivel="Flex",
            cambio="Automático",
            categoria="Sedan",
            dealership_name="Dealership Test",
            dealership_city="São Paulo",
            dealership_state="SP",
            dealership_phone="(11) 99999-9999",
            dealership_whatsapp="5511999999999"
        )

    @pytest.mark.asyncio
    async def test_high_income_terms(self, financing_agent, high_income_profile, sample_car):
        """Testa termos para perfil de alta renda (deve ter taxa baixa)"""
        terms = financing_agent.predict_terms(high_income_profile)
        
        assert terms['risk_level'] == "low"
        assert terms['monthly_interest_rate'] < 0.02  # Menor que 2%
        assert terms['max_months'] >= 72
        
        score = await financing_agent.calculate_score(sample_car, high_income_profile)
        assert score > 0.8  # Score alto

    @pytest.mark.asyncio
    async def test_low_income_terms(self, financing_agent, low_income_profile, sample_car):
        """Testa termos para perfil de baixa renda"""
        terms = financing_agent.predict_terms(low_income_profile)
        
        # Pode ser medium ou high dependendo dos modificadores
        assert terms['monthly_interest_rate'] > 0.02
        
        score = await financing_agent.calculate_score(sample_car, low_income_profile)
        assert score < 0.8

    @pytest.mark.asyncio
    async def test_undisclosed_income_terms(self, financing_agent, unknown_profile):
        """Testa perfil sem renda declarada (risco neutro/alto)"""
        terms = financing_agent.predict_terms(unknown_profile)
        
        # Risco base é 0.5 -> Medium risk
        assert terms['risk_level'] in ["medium", "high"]
        assert 0.02 <= terms['monthly_interest_rate'] <= 0.03

    def test_metrics_initialization(self, financing_agent):
        assert financing_agent.name == "financing"
        metrics = financing_agent.get_metrics()
        assert metrics['total_calls'] == 0
