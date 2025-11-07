"""
Testes para modelos de capacidade financeira e TCO
"""

import pytest
from pydantic import ValidationError
from models.user_profile import FinancialCapacity, TCOBreakdown, UserProfile
from models.car import Car, CarRecommendation


class TestFinancialCapacity:
    """Testes para o modelo FinancialCapacity"""
    
    def test_create_financial_capacity_valid(self):
        """Teste: Criar FinancialCapacity válido"""
        fc = FinancialCapacity(
            monthly_income_range="5000-8000",
            max_monthly_tco=2400.0,
            is_disclosed=True
        )
        
        assert fc.monthly_income_range == "5000-8000"
        assert fc.max_monthly_tco == 2400.0
        assert fc.is_disclosed is True
    
    def test_financial_capacity_defaults(self):
        """Teste: Valores padrão de FinancialCapacity"""
        fc = FinancialCapacity()
        
        assert fc.monthly_income_range is None
        assert fc.max_monthly_tco is None
        assert fc.is_disclosed is False
    
    def test_financial_capacity_not_disclosed(self):
        """Teste: Usuário não informou capacidade financeira"""
        fc = FinancialCapacity(is_disclosed=False)
        
        assert fc.monthly_income_range is None
        assert fc.max_monthly_tco is None
        assert fc.is_disclosed is False
    
    def test_financial_capacity_negative_tco(self):
        """Teste: TCO não pode ser negativo"""
        with pytest.raises(ValidationError):
            FinancialCapacity(
                monthly_income_range="5000-8000",
                max_monthly_tco=-100.0,
                is_disclosed=True
            )


class TestTCOBreakdown:
    """Testes para o modelo TCOBreakdown"""
    
    def test_create_tco_breakdown_valid(self):
        """Teste: Criar TCOBreakdown válido"""
        tco = TCOBreakdown(
            financing_monthly=1400.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=200.0,
            ipva_monthly=117.0,
            total_monthly=2267.0
        )
        
        assert tco.financing_monthly == 1400.0
        assert tco.fuel_monthly == 400.0
        assert tco.maintenance_monthly == 150.0
        assert tco.insurance_monthly == 200.0
        assert tco.ipva_monthly == 117.0
        assert tco.total_monthly == 2267.0
    
    def test_tco_breakdown_with_assumptions(self):
        """Teste: TCOBreakdown com premissas customizadas"""
        tco = TCOBreakdown(
            financing_monthly=1400.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=200.0,
            ipva_monthly=117.0,
            total_monthly=2267.0,
            assumptions={
                "down_payment_percent": 30,
                "financing_months": 48,
                "annual_interest_rate": 10.0,
                "monthly_km": 1500,
                "fuel_price_per_liter": 5.50,
                "state": "RJ"
            }
        )
        
        assert tco.assumptions["down_payment_percent"] == 30
        assert tco.assumptions["financing_months"] == 48
        assert tco.assumptions["state"] == "RJ"
    
    def test_tco_breakdown_default_assumptions(self):
        """Teste: TCOBreakdown com premissas padrão"""
        tco = TCOBreakdown(
            financing_monthly=1400.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=200.0,
            ipva_monthly=117.0,
            total_monthly=2267.0
        )
        
        assert tco.assumptions["down_payment_percent"] == 20
        assert tco.assumptions["financing_months"] == 60
        assert tco.assumptions["annual_interest_rate"] == 24.0  # Atualizado para 24% a.a.
        assert tco.assumptions["monthly_km"] == 1000
        assert tco.assumptions["fuel_price_per_liter"] == 5.20
        assert tco.assumptions["state"] == "SP"
    
    def test_tco_breakdown_negative_values(self):
        """Teste: Valores de TCO não podem ser negativos"""
        with pytest.raises(ValidationError):
            TCOBreakdown(
                financing_monthly=-1400.0,
                fuel_monthly=400.0,
                maintenance_monthly=150.0,
                insurance_monthly=200.0,
                ipva_monthly=117.0,
                total_monthly=2267.0
            )


class TestUserProfileWithFinancialCapacity:
    """Testes para UserProfile com FinancialCapacity"""
    
    def test_user_profile_with_financial_capacity(self):
        """Teste: UserProfile com capacidade financeira"""
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=80000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="5000-8000",
                max_monthly_tco=2400.0,
                is_disclosed=True
            )
        )
        
        assert profile.financial_capacity is not None
        assert profile.financial_capacity.monthly_income_range == "5000-8000"
        assert profile.financial_capacity.max_monthly_tco == 2400.0
        assert profile.financial_capacity.is_disclosed is True
    
    def test_user_profile_without_financial_capacity(self):
        """Teste: UserProfile sem capacidade financeira (opcional)"""
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=80000,
            uso_principal="familia"
        )
        
        assert profile.financial_capacity is None


class TestCarRecommendation:
    """Testes para o modelo CarRecommendation"""
    
    def test_create_car_recommendation_basic(self):
        """Teste: Criar CarRecommendation básico (sem TCO)"""
        car = Car(
            id="test_001",
            dealership_id="test_dealer",
            nome="Test Car",
            marca="Test",
            modelo="Model",
            ano=2022,
            preco=80000.0,
            quilometragem=30000,
            combustivel="Flex",
            categoria="Sedan",
            dealership_name="Test Dealer",
            dealership_city="São Paulo",
            dealership_state="SP",
            dealership_phone="11-1234-5678",
            dealership_whatsapp="5511987654321"
        )
        
        recommendation = CarRecommendation(
            car=car,
            score=0.85,
            match_percentage=85,
            justifications=["✅ Ótima economia", "✅ Espaço adequado"]
        )
        
        assert recommendation.car.id == "test_001"
        assert recommendation.score == 0.85
        assert recommendation.match_percentage == 85
        assert len(recommendation.justifications) == 2
        assert recommendation.tco_breakdown is None
        assert recommendation.fits_budget is None
        assert recommendation.budget_percentage is None
    
    def test_create_car_recommendation_with_tco(self):
        """Teste: Criar CarRecommendation com TCO"""
        car = Car(
            id="test_001",
            dealership_id="test_dealer",
            nome="Test Car",
            marca="Test",
            modelo="Model",
            ano=2022,
            preco=80000.0,
            quilometragem=30000,
            combustivel="Flex",
            categoria="Sedan",
            dealership_name="Test Dealer",
            dealership_city="São Paulo",
            dealership_state="SP",
            dealership_phone="11-1234-5678",
            dealership_whatsapp="5511987654321"
        )
        
        tco = TCOBreakdown(
            financing_monthly=1400.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=200.0,
            ipva_monthly=117.0,
            total_monthly=2267.0
        )
        
        recommendation = CarRecommendation(
            car=car,
            score=0.85,
            match_percentage=85,
            justifications=["✅ Ótima economia", "✅ Cabe no orçamento"],
            tco_breakdown=tco,
            fits_budget=True,
            budget_percentage=30.0
        )
        
        assert recommendation.tco_breakdown is not None
        assert recommendation.tco_breakdown.total_monthly == 2267.0
        assert recommendation.fits_budget is True
        assert recommendation.budget_percentage == 30.0
    
    def test_car_recommendation_score_validation(self):
        """Teste: Score deve estar entre 0.0 e 1.0"""
        car = Car(
            id="test_001",
            dealership_id="test_dealer",
            nome="Test Car",
            marca="Test",
            modelo="Model",
            ano=2022,
            preco=80000.0,
            quilometragem=30000,
            combustivel="Flex",
            categoria="Sedan",
            dealership_name="Test Dealer",
            dealership_city="São Paulo",
            dealership_state="SP",
            dealership_phone="11-1234-5678",
            dealership_whatsapp="5511987654321"
        )
        
        # Score > 1.0 deve falhar
        with pytest.raises(ValidationError):
            CarRecommendation(
                car=car,
                score=1.5,
                match_percentage=150,
                justifications=[]
            )
        
        # Score < 0.0 deve falhar
        with pytest.raises(ValidationError):
            CarRecommendation(
                car=car,
                score=-0.5,
                match_percentage=-50,
                justifications=[]
            )
    
    def test_car_recommendation_match_percentage_validation(self):
        """Teste: Match percentage deve estar entre 0 e 100"""
        car = Car(
            id="test_001",
            dealership_id="test_dealer",
            nome="Test Car",
            marca="Test",
            modelo="Model",
            ano=2022,
            preco=80000.0,
            quilometragem=30000,
            combustivel="Flex",
            categoria="Sedan",
            dealership_name="Test Dealer",
            dealership_city="São Paulo",
            dealership_state="SP",
            dealership_phone="11-1234-5678",
            dealership_whatsapp="5511987654321"
        )
        
        # Match percentage > 100 deve falhar
        with pytest.raises(ValidationError):
            CarRecommendation(
                car=car,
                score=0.85,
                match_percentage=150,
                justifications=[]
            )
