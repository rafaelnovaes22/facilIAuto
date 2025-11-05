"""
Testes de integração do TCO no motor de recomendação
"""

import pytest
from models.user_profile import UserProfile, FinancialCapacity
from models.car import Car
from services.unified_recommendation_engine import UnifiedRecommendationEngine
from services.tco_calculator import TCOCalculator


def test_tco_calculation_for_car():
    """Testa cálculo de TCO para um carro específico"""
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    # Criar perfil de teste
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=80000,
        uso_principal="familia",
        state="SP",
        prioridades={
            "economia": 4,
            "espaco": 5,
            "seguranca": 5
        }
    )
    
    # Pegar um carro de teste
    if engine.all_cars:
        car = engine.all_cars[0]
        tco = engine.calculate_tco_for_car(car, profile)
        
        assert tco is not None
        assert tco.total_monthly > 0
        assert tco.financing_monthly > 0
        assert tco.fuel_monthly > 0
        assert tco.maintenance_monthly > 0
        assert tco.insurance_monthly > 0
        assert tco.ipva_monthly > 0


def test_financial_capacity_filtering():
    """Testa filtragem por capacidade financeira"""
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    # Criar perfil com capacidade financeira
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=80000,
        uso_principal="familia",
        state="SP",
        prioridades={
            "economia": 4,
            "espaco": 5,
            "seguranca": 5
        },
        financial_capacity=FinancialCapacity(
            monthly_income_range="5000-8000",
            max_monthly_tco=2400.0,
            is_disclosed=True
        )
    )
    
    # Gerar recomendações
    recommendations = engine.recommend(profile, limit=10)
    
    # Verificar que todas as recomendações têm TCO
    for rec in recommendations:
        assert 'tco_breakdown' in rec
        if rec['tco_breakdown']:
            # Verificar que TCO está dentro do orçamento (com 10% tolerância)
            assert rec['tco_breakdown'].total_monthly <= 2400 * 1.10


def test_financial_bonus_application():
    """Testa aplicação de bonus financeiro no score"""
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    # Criar perfil com capacidade financeira
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=80000,
        uso_principal="familia",
        state="SP",
        prioridades={
            "economia": 4,
            "espaco": 5,
            "seguranca": 5
        },
        financial_capacity=FinancialCapacity(
            monthly_income_range="5000-8000",
            max_monthly_tco=2400.0,
            is_disclosed=True
        )
    )
    
    # Gerar recomendações
    recommendations = engine.recommend(profile, limit=10)
    
    # Verificar que recomendações têm informações de orçamento
    for rec in recommendations:
        if rec.get('fits_budget') is not None:
            assert isinstance(rec['fits_budget'], bool)
        if rec.get('budget_percentage') is not None:
            assert rec['budget_percentage'] > 0


def test_recommendations_without_financial_capacity():
    """Testa que recomendações funcionam sem capacidade financeira informada"""
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    # Criar perfil SEM capacidade financeira
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=80000,
        uso_principal="familia",
        state="SP",
        prioridades={
            "economia": 4,
            "espaco": 5,
            "seguranca": 5
        }
    )
    
    # Gerar recomendações
    recommendations = engine.recommend(profile, limit=10)
    
    # Deve retornar recomendações normalmente
    assert len(recommendations) > 0
    
    # TCO pode estar presente mas não deve filtrar
    for rec in recommendations:
        # fits_budget deve ser None quando não há capacidade financeira
        assert rec.get('fits_budget') is None


def test_max_monthly_tco_calculation():
    """Testa cálculo de TCO máximo baseado em faixa de renda"""
    
    # Testar diferentes faixas
    assert TCOCalculator.calculate_max_monthly_tco("0-3000") == 450.0
    assert TCOCalculator.calculate_max_monthly_tco("3000-5000") == 1200.0
    assert TCOCalculator.calculate_max_monthly_tco("5000-8000") == 1950.0
    assert TCOCalculator.calculate_max_monthly_tco("8000-12000") == 3000.0
    assert TCOCalculator.calculate_max_monthly_tco("12000+") == 4200.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
