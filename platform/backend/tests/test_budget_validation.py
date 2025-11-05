"""
Testes para validação de orçamento (Budget Validation Logic)

Testa a lógica de validação de orçamento que determina se um veículo
está "Dentro do orçamento" ou "Acima do orçamento" baseado no TCO.

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5

Author: FacilIAuto
Date: 2025-11-05
"""

import pytest
from models.user_profile import UserProfile, FinancialCapacity, TCOBreakdown
from services.unified_recommendation_engine import UnifiedRecommendationEngine


class TestBudgetValidation:
    """Testes para lógica de validação de orçamento"""
    
    def test_dentro_do_orcamento_when_tco_equals_max(self):
        """
        Testa "Dentro do orçamento" quando TCO = max_monthly_tco
        
        Requirement 1.2: WHEN a vehicle's monthly TCO is less than or equal 
        to the user's budget, THE TCO System SHALL display "Dentro do orçamento" status
        """
        # Arrange
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1800.0,
            fuel_monthly=600.0,
            maintenance_monthly=200.0,
            insurance_monthly=250.0,
            ipva_monthly=150.0,
            total_monthly=3000.0  # Exatamente igual ao max_monthly_tco
        )
        
        engine = UnifiedRecommendationEngine(data_dir="data")
        
        # Act
        fits_budget, status_message = engine.validate_budget_status(tco, profile)
        
        # Assert
        assert fits_budget is True
        assert status_message == "Dentro do orçamento"
    
    def test_dentro_do_orcamento_when_tco_below_max(self):
        """
        Testa "Dentro do orçamento" quando TCO < max_monthly_tco
        
        Requirement 1.2: WHEN a vehicle's monthly TCO is less than or equal 
        to the user's budget, THE TCO System SHALL display "Dentro do orçamento" status
        """
        # Arrange
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1500.0,
            fuel_monthly=500.0,
            maintenance_monthly=180.0,
            insurance_monthly=220.0,
            ipva_monthly=130.0,
            total_monthly=2530.0  # Abaixo do max_monthly_tco
        )
        
        engine = UnifiedRecommendationEngine(data_dir="data")
        
        # Act
        fits_budget, status_message = engine.validate_budget_status(tco, profile)
        
        # Assert
        assert fits_budget is True
        assert status_message == "Dentro do orçamento"
    
    def test_acima_do_orcamento_when_tco_above_max(self):
        """
        Testa "Acima do orçamento" quando TCO > max_monthly_tco
        
        Requirement 1.3: WHEN a vehicle's monthly TCO exceeds the user's budget, 
        THE TCO System SHALL display "Acima do orçamento" status
        """
        # Arrange
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=2000.0,
            fuel_monthly=700.0,
            maintenance_monthly=250.0,
            insurance_monthly=300.0,
            ipva_monthly=180.0,
            total_monthly=3430.0  # Acima do max_monthly_tco
        )
        
        engine = UnifiedRecommendationEngine(data_dir="data")
        
        # Act
        fits_budget, status_message = engine.validate_budget_status(tco, profile)
        
        # Assert
        assert fits_budget is False
        assert status_message == "Acima do orçamento"
    
    def test_acima_do_orcamento_slightly_above(self):
        """
        Testa "Acima do orçamento" quando TCO está apenas R$1 acima
        
        Requirement 1.3: WHEN a vehicle's monthly TCO exceeds the user's budget, 
        THE TCO System SHALL display "Acima do orçamento" status
        """
        # Arrange
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="trabalho",
            tamanho_familia=1,
            financial_capacity=FinancialCapacity(
                monthly_income_range="5000-8000",
                max_monthly_tco=2000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=180.0,
            ipva_monthly=71.0,
            total_monthly=2001.0  # Apenas R$1 acima
        )
        
        engine = UnifiedRecommendationEngine(data_dir="data")
        
        # Act
        fits_budget, status_message = engine.validate_budget_status(tco, profile)
        
        # Assert
        assert fits_budget is False
        assert status_message == "Acima do orçamento"
    
    def test_missing_financial_capacity(self):
        """
        Testa tratamento quando financial_capacity não está presente
        
        Requirement 1.4: THE Budget Validator SHALL use the complete monthly TCO 
        (financing + fuel + insurance + maintenance) for comparison
        
        Note: Quando não há financial_capacity, não é possível validar orçamento
        """
        # Arrange
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            financial_capacity=None  # Usuário não informou capacidade financeira
        )
        
        tco = TCOBreakdown(
            financing_monthly=1500.0,
            fuel_monthly=500.0,
            maintenance_monthly=180.0,
            insurance_monthly=220.0,
            ipva_monthly=130.0,
            total_monthly=2530.0
        )
        
        engine = UnifiedRecommendationEngine(data_dir="data")
        
        # Act
        fits_budget, status_message = engine.validate_budget_status(tco, profile)
        
        # Assert
        assert fits_budget is None
        assert status_message == "Orçamento não informado"
    
    def test_missing_max_monthly_tco(self):
        """
        Testa tratamento quando max_monthly_tco não está presente
        
        Requirement 1.4: THE Budget Validator SHALL use the complete monthly TCO 
        (financing + fuel + insurance + maintenance) for comparison
        """
        # Arrange
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=None,  # Não calculado
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1500.0,
            fuel_monthly=500.0,
            maintenance_monthly=180.0,
            insurance_monthly=220.0,
            ipva_monthly=130.0,
            total_monthly=2530.0
        )
        
        engine = UnifiedRecommendationEngine(data_dir="data")
        
        # Act
        fits_budget, status_message = engine.validate_budget_status(tco, profile)
        
        # Assert
        assert fits_budget is None
        assert status_message == "Orçamento não informado"
    
    def test_financial_capacity_not_disclosed(self):
        """
        Testa quando usuário optou por não informar capacidade financeira
        
        Requirement 1.4: THE Budget Validator SHALL use the complete monthly TCO 
        (financing + fuel + insurance + maintenance) for comparison
        """
        # Arrange
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            financial_capacity=FinancialCapacity(
                monthly_income_range=None,
                max_monthly_tco=None,
                is_disclosed=False  # Usuário pulou a pergunta
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1500.0,
            fuel_monthly=500.0,
            maintenance_monthly=180.0,
            insurance_monthly=220.0,
            ipva_monthly=130.0,
            total_monthly=2530.0
        )
        
        engine = UnifiedRecommendationEngine(data_dir="data")
        
        # Act
        fits_budget, status_message = engine.validate_budget_status(tco, profile)
        
        # Assert
        assert fits_budget is None
        assert status_message == "Orçamento não informado"
    
    def test_uses_complete_monthly_tco(self):
        """
        Testa que a validação usa o TCO mensal completo
        
        Requirement 1.4: THE Budget Validator SHALL use the complete monthly TCO 
        (financing + fuel + insurance + maintenance) for comparison
        """
        # Arrange
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=2500.0,
                is_disclosed=True
            )
        )
        
        # TCO com todos os componentes
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=450.0,
            maintenance_monthly=200.0,
            insurance_monthly=250.0,
            ipva_monthly=150.0,
            total_monthly=2250.0  # Soma de todos os componentes
        )
        
        engine = UnifiedRecommendationEngine(data_dir="data")
        
        # Act
        fits_budget, status_message = engine.validate_budget_status(tco, profile)
        
        # Assert
        # Deve usar total_monthly (2250) vs max_monthly_tco (2500)
        assert fits_budget is True
        assert status_message == "Dentro do orçamento"
        
        # Verificar que total_monthly é realmente a soma
        expected_total = (
            tco.financing_monthly +
            tco.fuel_monthly +
            tco.maintenance_monthly +
            tco.insurance_monthly +
            tco.ipva_monthly
        )
        assert tco.total_monthly == expected_total
    
    def test_different_income_ranges(self):
        """
        Testa validação com diferentes faixas de renda
        
        Requirement 1.5: THE TCO System SHALL display the exact monthly cost value 
        alongside the budget status
        """
        engine = UnifiedRecommendationEngine(data_dir="data")
        
        # Renda baixa
        profile_low = UserProfile(
            orcamento_min=30000,
            orcamento_max=50000,
            uso_principal="primeiro_carro",
            tamanho_familia=1,
            financial_capacity=FinancialCapacity(
                monthly_income_range="3000-5000",
                max_monthly_tco=1200.0,  # 30% de 4000
                is_disclosed=True
            )
        )
        
        tco_low = TCOBreakdown(
            financing_monthly=700.0,
            fuel_monthly=300.0,
            maintenance_monthly=100.0,
            insurance_monthly=80.0,
            ipva_monthly=50.0,
            total_monthly=1230.0
        )
        
        fits_low, msg_low = engine.validate_budget_status(tco_low, profile_low)
        assert fits_low is False  # 1230 > 1200
        assert msg_low == "Acima do orçamento"
        
        # Renda alta
        profile_high = UserProfile(
            orcamento_min=80000,
            orcamento_max=150000,
            uso_principal="lazer",
            tamanho_familia=2,
            financial_capacity=FinancialCapacity(
                monthly_income_range="12000+",
                max_monthly_tco=4200.0,  # 30% de 14000
                is_disclosed=True
            )
        )
        
        tco_high = TCOBreakdown(
            financing_monthly=2500.0,
            fuel_monthly=800.0,
            maintenance_monthly=350.0,
            insurance_monthly=450.0,
            ipva_monthly=200.0,
            total_monthly=4300.0
        )
        
        fits_high, msg_high = engine.validate_budget_status(tco_high, profile_high)
        assert fits_high is False  # 4300 > 4200
        assert msg_high == "Acima do orçamento"
    
    def test_edge_case_zero_tco(self):
        """
        Testa caso extremo com TCO zero (não deveria acontecer, mas testar robustez)
        """
        # Arrange
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=0.0,
            fuel_monthly=0.0,
            maintenance_monthly=0.0,
            insurance_monthly=0.0,
            ipva_monthly=0.0,
            total_monthly=0.0
        )
        
        engine = UnifiedRecommendationEngine(data_dir="data")
        
        # Act
        fits_budget, status_message = engine.validate_budget_status(tco, profile)
        
        # Assert
        # TCO zero está dentro de qualquer orçamento
        assert fits_budget is True
        assert status_message == "Dentro do orçamento"
    
    def test_edge_case_very_high_tco(self):
        """
        Testa caso extremo com TCO muito alto
        """
        # Arrange
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            financial_capacity=FinancialCapacity(
                monthly_income_range="5000-8000",
                max_monthly_tco=2000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=5000.0,
            fuel_monthly=1500.0,
            maintenance_monthly=800.0,
            insurance_monthly=1000.0,
            ipva_monthly=500.0,
            total_monthly=8800.0  # Muito acima do orçamento
        )
        
        engine = UnifiedRecommendationEngine(data_dir="data")
        
        # Act
        fits_budget, status_message = engine.validate_budget_status(tco, profile)
        
        # Assert
        assert fits_budget is False
        assert status_message == "Acima do orçamento"
