"""
Testes para melhorias do TCO Calculator (Task 1)

Testa as novas funcionalidades:
- Ajuste de manutenção por quilometragem alta
- Validação de termos de financiamento
- Tracking transparente de assumptions

Author: FacilIAuto
Date: 2025-11-05
"""

import pytest
from services.tco_calculator import TCOCalculator, TCOBreakdown


class TestHighMileageAdjustment:
    """Testes para ajuste de manutenção por quilometragem"""
    
    def test_no_adjustment_low_mileage(self):
        """Testa que não há ajuste para quilometragem ≤100k km"""
        calculator = TCOCalculator()
        
        base_maintenance = 150.0
        adjusted, adjustment_info = calculator.adjust_maintenance_for_mileage(
            base_maintenance=base_maintenance,
            mileage=50000
        )
        
        assert adjusted == base_maintenance
        assert adjustment_info is None
    
    def test_no_adjustment_exactly_100k(self):
        """Testa que não há ajuste para exatamente 100k km"""
        calculator = TCOCalculator()
        
        base_maintenance = 150.0
        adjusted, adjustment_info = calculator.adjust_maintenance_for_mileage(
            base_maintenance=base_maintenance,
            mileage=100000
        )
        
        assert adjusted == base_maintenance
        assert adjustment_info is None
    
    def test_50_percent_adjustment_medium_mileage(self):
        """Testa ajuste de +50% para quilometragem 100k-150k km"""
        calculator = TCOCalculator()
        
        base_maintenance = 150.0
        adjusted, adjustment_info = calculator.adjust_maintenance_for_mileage(
            base_maintenance=base_maintenance,
            mileage=120000
        )
        
        assert adjusted == 225.0  # 150 * 1.5
        assert adjustment_info is not None
        assert adjustment_info["factor"] == 1.5
        assert "100k-150k" in adjustment_info["reason"]
    
    def test_50_percent_adjustment_exactly_150k(self):
        """Testa ajuste de +50% para exatamente 150k km"""
        calculator = TCOCalculator()
        
        base_maintenance = 150.0
        adjusted, adjustment_info = calculator.adjust_maintenance_for_mileage(
            base_maintenance=base_maintenance,
            mileage=150000
        )
        
        assert adjusted == 225.0  # 150 * 1.5
        assert adjustment_info["factor"] == 1.5
    
    def test_100_percent_adjustment_high_mileage(self):
        """Testa ajuste de +100% para quilometragem >150k km"""
        calculator = TCOCalculator()
        
        base_maintenance = 150.0
        adjusted, adjustment_info = calculator.adjust_maintenance_for_mileage(
            base_maintenance=base_maintenance,
            mileage=180000
        )
        
        assert adjusted == 300.0  # 150 * 2.0
        assert adjustment_info is not None
        assert adjustment_info["factor"] == 2.0
        assert ">150k" in adjustment_info["reason"]
    
    def test_100_percent_adjustment_very_high_mileage(self):
        """Testa ajuste de +100% para quilometragem muito alta"""
        calculator = TCOCalculator()
        
        base_maintenance = 200.0
        adjusted, adjustment_info = calculator.adjust_maintenance_for_mileage(
            base_maintenance=base_maintenance,
            mileage=250000
        )
        
        assert adjusted == 400.0  # 200 * 2.0
        assert adjustment_info["factor"] == 2.0


class TestFinancingTermsValidation:
    """Testes para validação de termos de financiamento"""
    
    def test_validate_normal_terms(self):
        """Testa que termos normais não são alterados"""
        calculator = TCOCalculator()
        
        down, months, rate = calculator.validate_financing_terms(
            down_payment_percent=0.20,
            financing_months=60,
            annual_interest_rate=0.12
        )
        
        assert down == 0.20
        assert months == 60
        assert rate == 0.12
    
    def test_validate_negative_down_payment(self):
        """Testa correção de entrada negativa"""
        calculator = TCOCalculator()
        
        down, months, rate = calculator.validate_financing_terms(
            down_payment_percent=-0.10,
            financing_months=60,
            annual_interest_rate=0.12
        )
        
        assert down == 0.20  # Default
    
    def test_validate_excessive_down_payment(self):
        """Testa correção de entrada >100%"""
        calculator = TCOCalculator()
        
        down, months, rate = calculator.validate_financing_terms(
            down_payment_percent=20.0,  # 2000% - erro comum
            financing_months=60,
            annual_interest_rate=0.12
        )
        
        assert down == 0.20  # Default
    
    def test_validate_too_few_months(self):
        """Testa correção de prazo muito curto"""
        calculator = TCOCalculator()
        
        down, months, rate = calculator.validate_financing_terms(
            down_payment_percent=0.20,
            financing_months=6,  # Muito curto
            annual_interest_rate=0.12
        )
        
        assert months == 60  # Default
    
    def test_validate_too_many_months(self):
        """Testa correção de prazo muito longo"""
        calculator = TCOCalculator()
        
        down, months, rate = calculator.validate_financing_terms(
            down_payment_percent=0.20,
            financing_months=120,  # Muito longo
            annual_interest_rate=0.12
        )
        
        assert months == 60  # Default
    
    def test_validate_excessive_interest_rate(self):
        """Testa correção de taxa de juros excessiva"""
        calculator = TCOCalculator()
        
        down, months, rate = calculator.validate_financing_terms(
            down_payment_percent=0.20,
            financing_months=60,
            annual_interest_rate=1.0  # 100% ao ano - muito alto
        )
        
        assert rate == 0.12  # Default
    
    def test_validate_zero_interest_rate(self):
        """Testa correção de taxa de juros muito baixa"""
        calculator = TCOCalculator()
        
        down, months, rate = calculator.validate_financing_terms(
            down_payment_percent=0.20,
            financing_months=60,
            annual_interest_rate=0.001  # Muito baixo
        )
        
        assert rate == 0.12  # Default


class TestTCOWithMileage:
    """Testes para cálculo de TCO com quilometragem"""
    
    def test_tco_with_low_mileage(self):
        """Testa TCO para carro com baixa quilometragem"""
        calculator = TCOCalculator()
        
        result = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=3,
            car_mileage=50000
        )
        
        # Não deve ter ajuste de manutenção
        assert "maintenance_adjustment" not in result.assumptions
        assert result.maintenance_monthly > 0
    
    def test_tco_with_medium_mileage(self):
        """Testa TCO para carro com quilometragem média-alta"""
        calculator = TCOCalculator()
        
        result = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=5,
            car_mileage=120000
        )
        
        # Deve ter ajuste de +50%
        assert "maintenance_adjustment" in result.assumptions
        assert result.assumptions["maintenance_adjustment"]["factor"] == 1.5
        assert result.maintenance_monthly > 0
    
    def test_tco_with_high_mileage(self):
        """Testa TCO para carro com quilometragem alta"""
        calculator = TCOCalculator()
        
        result = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=8,
            car_mileage=180000
        )
        
        # Deve ter ajuste de +100%
        assert "maintenance_adjustment" in result.assumptions
        assert result.assumptions["maintenance_adjustment"]["factor"] == 2.0
        assert result.maintenance_monthly > 0
    
    def test_tco_mileage_increases_maintenance(self):
        """Testa que quilometragem alta aumenta custo de manutenção"""
        calculator = TCOCalculator()
        
        result_low = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=5,
            car_mileage=50000
        )
        
        result_high = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=5,
            car_mileage=180000
        )
        
        # Quilometragem alta deve ter manutenção mais cara
        assert result_high.maintenance_monthly > result_low.maintenance_monthly


class TestTransparentAssumptions:
    """Testes para tracking transparente de assumptions"""
    
    def test_assumptions_include_all_parameters(self):
        """Testa que assumptions incluem todos os parâmetros"""
        calculator = TCOCalculator(
            down_payment_percent=0.30,
            financing_months=48,
            annual_interest_rate=0.15,
            monthly_km=1500,
            fuel_price_per_liter=6.00,
            state="RJ"
        )
        
        result = calculator.calculate_tco(
            car_price=80000,
            car_category="SUV",
            fuel_efficiency_km_per_liter=10.0,
            car_age=2,
            car_mileage=40000
        )
        
        # Verificar que todos os assumptions estão presentes
        assert "down_payment_percent" in result.assumptions
        assert "financing_months" in result.assumptions
        assert "annual_interest_rate" in result.assumptions
        assert "monthly_km" in result.assumptions
        assert "fuel_price_per_liter" in result.assumptions
        assert "fuel_efficiency" in result.assumptions
        assert "state" in result.assumptions
        
        # Verificar valores
        assert result.assumptions["down_payment_percent"] == 30.0
        assert result.assumptions["financing_months"] == 48
        assert result.assumptions["annual_interest_rate"] == 15.0
        assert result.assumptions["monthly_km"] == 1500
        assert result.assumptions["fuel_price_per_liter"] == 6.00
        assert result.assumptions["fuel_efficiency"] == 10.0
        assert result.assumptions["state"] == "RJ"
    
    def test_assumptions_include_mileage_adjustment(self):
        """Testa que assumptions incluem ajuste de quilometragem quando aplicável"""
        calculator = TCOCalculator()
        
        result = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=5,
            car_mileage=137842  # Exemplo do design doc
        )
        
        # Deve ter ajuste de manutenção
        assert "maintenance_adjustment" in result.assumptions
        assert result.assumptions["maintenance_adjustment"]["factor"] == 1.5
        assert "reason" in result.assumptions["maintenance_adjustment"]
    
    def test_assumptions_no_mileage_adjustment_when_not_needed(self):
        """Testa que assumptions não incluem ajuste quando não necessário"""
        calculator = TCOCalculator()
        
        result = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=2,
            car_mileage=30000
        )
        
        # Não deve ter ajuste de manutenção
        assert "maintenance_adjustment" not in result.assumptions


class TestBackwardCompatibility:
    """Testes para garantir compatibilidade com código existente"""
    
    def test_tco_without_mileage_parameter(self):
        """Testa que TCO funciona sem passar mileage (backward compatibility)"""
        calculator = TCOCalculator()
        
        # Chamar sem car_mileage (usa default 0)
        result = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=3
        )
        
        # Deve funcionar normalmente
        assert result.total_monthly > 0
        assert "maintenance_adjustment" not in result.assumptions
    
    def test_tco_with_zero_mileage(self):
        """Testa TCO com mileage explicitamente zero"""
        calculator = TCOCalculator()
        
        result = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=0,
            car_mileage=0
        )
        
        # Deve funcionar como carro novo
        assert result.total_monthly > 0
        assert "maintenance_adjustment" not in result.assumptions
