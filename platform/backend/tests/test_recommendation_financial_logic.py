"""
Testes para lógica financeira do motor de recomendação (Task 7)

Testa as funcionalidades implementadas nas Tasks 2.2, 2.3:
- Avaliação de saúde financeira (assess_financial_health)
- Validação de status de orçamento (validate_budget_status)

Author: FacilIAuto
Date: 2025-11-05
Requirements: 1.1-1.5, 2.1-2.5
"""

import pytest
from models.user_profile import UserProfile, FinancialCapacity, TCOBreakdown
from services.unified_recommendation_engine import UnifiedRecommendationEngine


@pytest.fixture
def engine():
    """Engine de recomendação para testes"""
    return UnifiedRecommendationEngine(data_dir="data")


class TestBudgetValidationLogic:
    """
    Testes para validação de orçamento (Task 7.2)
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    """
    
    def test_within_budget(self, engine):
        """Testa "Dentro do orçamento" para TCO ≤ max_monthly_tco"""
        # Criar perfil com orçamento de R$ 3.000/mês
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000.0,
                is_disclosed=True
            )
        )
        
        # TCO dentro do orçamento
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=200.0,
            ipva_monthly=233.33,
            total_monthly=2183.33
        )
        
        fits, message = engine.validate_budget_status(tco, profile)
        
        assert fits is True
        assert message == "Dentro do orçamento"
    
    def test_above_budget(self, engine):
        """Testa "Acima do orçamento" para TCO > max_monthly_tco"""
        # Criar perfil com orçamento de R$ 2.000/mês
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="trabalho",
            financial_capacity=FinancialCapacity(
                monthly_income_range="5000-8000",
                max_monthly_tco=2000.0,
                is_disclosed=True
            )
        )
        
        # TCO acima do orçamento
        tco = TCOBreakdown(
            financing_monthly=1500.0,
            fuel_monthly=500.0,
            maintenance_monthly=200.0,
            insurance_monthly=250.0,
            ipva_monthly=300.0,
            total_monthly=2750.0
        )
        
        fits, message = engine.validate_budget_status(tco, profile)
        
        assert fits is False
        assert message == "Acima do orçamento"
    
    def test_exactly_at_budget(self, engine):
        """Testa TCO exatamente igual ao orçamento (deve ser "Dentro")"""
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=2500.0,
                is_disclosed=True
            )
        )
        
        # TCO exatamente igual ao orçamento
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=600.0,
            maintenance_monthly=300.0,
            insurance_monthly=250.0,
            ipva_monthly=150.0,
            total_monthly=2500.0
        )
        
        fits, message = engine.validate_budget_status(tco, profile)
        
        assert fits is True
        assert message == "Dentro do orçamento"
    
    def test_missing_financial_capacity(self, engine):
        """Testa handling quando financial_capacity não está presente"""
        # Perfil sem financial_capacity
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="trabalho"
        )
        
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=200.0,
            ipva_monthly=233.33,
            total_monthly=2183.33
        )
        
        fits, message = engine.validate_budget_status(tco, profile)
        
        assert fits is None
        assert message == "Orçamento não informado"
    
    def test_financial_capacity_not_disclosed(self, engine):
        """Testa handling quando is_disclosed é False"""
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000.0,
                is_disclosed=False  # Usuário não quer divulgar
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=200.0,
            ipva_monthly=233.33,
            total_monthly=2183.33
        )
        
        fits, message = engine.validate_budget_status(tco, profile)
        
        assert fits is None
        assert message == "Orçamento não informado"
    
    def test_missing_max_monthly_tco(self, engine):
        """Testa handling quando max_monthly_tco não está definido"""
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=None,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=200.0,
            ipva_monthly=233.33,
            total_monthly=2183.33
        )
        
        fits, message = engine.validate_budget_status(tco, profile)
        
        assert fits is None
        assert message == "Orçamento não informado"


class TestFinancialHealthAssessment:
    """
    Testes para avaliação de saúde financeira (Task 7.3)
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    
    def test_green_status_healthy(self, engine):
        """Testa status verde para ≤20% da renda"""
        # Renda: 8000-12000 (média: 10000)
        # TCO: 2000 (20% da renda)
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1000.0,
            fuel_monthly=400.0,
            maintenance_monthly=200.0,
            insurance_monthly=250.0,
            ipva_monthly=150.0,
            total_monthly=2000.0
        )
        
        health = engine.assess_financial_health(tco, profile)
        
        assert health is not None
        assert health["status"] == "healthy"
        assert health["color"] == "green"
        assert health["message"] == "Saudável"
        assert health["percentage"] == 20.0
    
    def test_green_status_below_20_percent(self, engine):
        """Testa status verde para <20% da renda"""
        # Renda: 8000-12000 (média: 10000)
        # TCO: 1500 (15% da renda)
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="trabalho",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=800.0,
            fuel_monthly=300.0,
            maintenance_monthly=150.0,
            insurance_monthly=150.0,
            ipva_monthly=100.0,
            total_monthly=1500.0
        )
        
        health = engine.assess_financial_health(tco, profile)
        
        assert health["status"] == "healthy"
        assert health["color"] == "green"
        assert health["percentage"] == 15.0
    
    def test_yellow_status_caution(self, engine):
        """Testa status amarelo para 20-30% da renda"""
        # Renda: 8000-12000 (média: 10000)
        # TCO: 2500 (25% da renda)
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1300.0,
            fuel_monthly=500.0,
            maintenance_monthly=250.0,
            insurance_monthly=300.0,
            ipva_monthly=150.0,
            total_monthly=2500.0
        )
        
        health = engine.assess_financial_health(tco, profile)
        
        assert health["status"] == "caution"
        assert health["color"] == "yellow"
        assert health["message"] == "Atenção"
        assert health["percentage"] == 25.0
    
    def test_yellow_status_at_30_percent(self, engine):
        """Testa status amarelo para exatamente 30% da renda"""
        # Renda: 8000-12000 (média: 10000)
        # TCO: 3000 (30% da renda)
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1500.0,
            fuel_monthly=600.0,
            maintenance_monthly=300.0,
            insurance_monthly=400.0,
            ipva_monthly=200.0,
            total_monthly=3000.0
        )
        
        health = engine.assess_financial_health(tco, profile)
        
        assert health["status"] == "caution"
        assert health["color"] == "yellow"
        assert health["percentage"] == 30.0
    
    def test_red_status_high_commitment(self, engine):
        """Testa status vermelho para >30% da renda"""
        # Renda: 8000-12000 (média: 10000)
        # TCO: 3500 (35% da renda)
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=4000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1800.0,
            fuel_monthly=700.0,
            maintenance_monthly=400.0,
            insurance_monthly=400.0,
            ipva_monthly=200.0,
            total_monthly=3500.0
        )
        
        health = engine.assess_financial_health(tco, profile)
        
        assert health["status"] == "high_commitment"
        assert health["color"] == "red"
        assert health["message"] == "Alto comprometimento"
        assert health["percentage"] == 35.0
    
    def test_percentage_calculation_accuracy(self, engine):
        """Testa precisão do cálculo de percentual"""
        # Renda: 5000-8000 (média: 6500)
        # TCO: 1625 (25% da renda)
        profile = UserProfile(
            orcamento_min=40000,
            orcamento_max=70000,
            uso_principal="trabalho",
            financial_capacity=FinancialCapacity(
                monthly_income_range="5000-8000",
                max_monthly_tco=2000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=900.0,
            fuel_monthly=350.0,
            maintenance_monthly=150.0,
            insurance_monthly=150.0,
            ipva_monthly=75.0,
            total_monthly=1625.0
        )
        
        health = engine.assess_financial_health(tco, profile)
        
        # 1625 / 6500 * 100 = 25.0%
        assert health["percentage"] == 25.0
        assert health["status"] == "caution"
    
    def test_missing_financial_capacity(self, engine):
        """Testa retorno None quando não há financial_capacity"""
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="trabalho"
        )
        
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=200.0,
            ipva_monthly=233.33,
            total_monthly=2183.33
        )
        
        health = engine.assess_financial_health(tco, profile)
        
        assert health is None
    
    def test_financial_capacity_not_disclosed(self, engine):
        """Testa retorno None quando is_disclosed é False"""
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000.0,
                is_disclosed=False
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=200.0,
            ipva_monthly=233.33,
            total_monthly=2183.33
        )
        
        health = engine.assess_financial_health(tco, profile)
        
        assert health is None
    
    def test_missing_income_range(self, engine):
        """Testa retorno None quando income_range não está definido"""
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range=None,
                max_monthly_tco=3000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=200.0,
            ipva_monthly=233.33,
            total_monthly=2183.33
        )
        
        health = engine.assess_financial_health(tco, profile)
        
        assert health is None
    
    def test_invalid_income_range(self, engine):
        """Testa retorno None para faixa de renda inválida"""
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="invalid-range",
                max_monthly_tco=3000.0,
                is_disclosed=True
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=400.0,
            maintenance_monthly=150.0,
            insurance_monthly=200.0,
            ipva_monthly=233.33,
            total_monthly=2183.33
        )
        
        health = engine.assess_financial_health(tco, profile)
        
        assert health is None
    
    def test_all_income_ranges(self, engine):
        """Testa cálculo para todas as faixas de renda"""
        income_ranges = {
            "0-3000": 1500,      # Média: 1500
            "3000-5000": 4000,   # Média: 4000
            "5000-8000": 6500,   # Média: 6500
            "8000-12000": 10000, # Média: 10000
            "12000+": 14000      # Média: 14000
        }
        
        for income_range, avg_income in income_ranges.items():
            profile = UserProfile(
                orcamento_min=50000,
                orcamento_max=100000,
                uso_principal="familia",
                financial_capacity=FinancialCapacity(
                    monthly_income_range=income_range,
                    max_monthly_tco=avg_income * 0.30,
                    is_disclosed=True
                )
            )
            
            # TCO de 25% da renda (deve ser amarelo)
            tco_monthly = avg_income * 0.25
            tco = TCOBreakdown(
                financing_monthly=tco_monthly * 0.5,
                fuel_monthly=tco_monthly * 0.2,
                maintenance_monthly=tco_monthly * 0.1,
                insurance_monthly=tco_monthly * 0.1,
                ipva_monthly=tco_monthly * 0.1,
                total_monthly=tco_monthly
            )
            
            health = engine.assess_financial_health(tco, profile)
            
            assert health is not None
            assert health["status"] == "caution"
            assert health["color"] == "yellow"
            assert health["percentage"] == 25.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
