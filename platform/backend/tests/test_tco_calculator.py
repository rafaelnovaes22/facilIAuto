"""
Testes para TCOCalculator

Testa todos os cálculos de TCO (Total Cost of Ownership):
- Financiamento (Tabela Price)
- Combustível
- Manutenção
- Seguro
- IPVA
- TCO completo

Author: FacilIAuto
Date: 2025-11-05
"""

import pytest
from services.tco_calculator import TCOCalculator, TCOBreakdown


class TestFinancingCalculation:
    """Testes para cálculo de financiamento"""
    
    def test_calculate_financing_monthly_basic(self):
        """Testa cálculo básico de financiamento"""
        calculator = TCOCalculator(
            down_payment_percent=0.20,
            financing_months=60,
            annual_interest_rate=0.12
        )
        
        result = calculator.calculate_financing_monthly(car_price=70000)
        
        # Valor esperado aproximado para R$ 70k, 20% entrada, 60x, 12% a.a.
        # Financiado: R$ 56.000
        # Parcela esperada: ~R$ 1.245
        assert 1200 <= result <= 1300
    
    def test_calculate_financing_monthly_no_interest(self):
        """Testa financiamento sem juros"""
        calculator = TCOCalculator(
            down_payment_percent=0.20,
            financing_months=60,
            annual_interest_rate=0.0
        )
        
        result = calculator.calculate_financing_monthly(car_price=60000)
        
        # Sem juros: (60000 * 0.80) / 60 = 800
        expected = (60000 * 0.80) / 60
        assert abs(result - expected) < 0.01
    
    def test_calculate_financing_monthly_different_down_payment(self):
        """Testa com entrada diferente"""
        calculator = TCOCalculator(
            down_payment_percent=0.30,  # 30% de entrada
            financing_months=60,
            annual_interest_rate=0.12
        )
        
        result = calculator.calculate_financing_monthly(car_price=70000)
        
        # Com 30% de entrada, parcela deve ser menor
        assert 900 <= result <= 1100
    
    def test_calculate_financing_monthly_different_months(self):
        """Testa com prazo diferente"""
        calculator = TCOCalculator(
            down_payment_percent=0.20,
            financing_months=48,  # 48 meses
            annual_interest_rate=0.12
        )
        
        result = calculator.calculate_financing_monthly(car_price=70000)
        
        # Menos parcelas = parcela maior
        assert 1400 <= result <= 1600


class TestFuelCalculation:
    """Testes para cálculo de combustível"""
    
    def test_calculate_fuel_monthly_basic(self):
        """Testa cálculo básico de combustível"""
        calculator = TCOCalculator(
            monthly_km=1000,
            fuel_price_per_liter=5.20
        )
        
        result = calculator.calculate_fuel_monthly(
            fuel_efficiency_km_per_liter=13.0
        )
        
        # 1000 km / 13 km/L = 76.92 L
        # 76.92 L * R$ 5.20 = R$ 400
        expected = (1000 / 13.0) * 5.20
        assert abs(result - expected) < 0.01
    
    def test_calculate_fuel_monthly_high_consumption(self):
        """Testa carro com consumo alto"""
        calculator = TCOCalculator(
            monthly_km=1000,
            fuel_price_per_liter=5.20
        )
        
        result = calculator.calculate_fuel_monthly(
            fuel_efficiency_km_per_liter=8.0  # Consumo alto
        )
        
        # 1000 km / 8 km/L = 125 L
        # 125 L * R$ 5.20 = R$ 650
        expected = (1000 / 8.0) * 5.20
        assert abs(result - expected) < 0.01
    
    def test_calculate_fuel_monthly_zero_efficiency(self):
        """Testa com eficiência zero (edge case)"""
        calculator = TCOCalculator()
        
        result = calculator.calculate_fuel_monthly(
            fuel_efficiency_km_per_liter=0.0
        )
        
        assert result == 0.0
    
    def test_calculate_fuel_monthly_different_km(self):
        """Testa com quilometragem diferente"""
        calculator = TCOCalculator(
            monthly_km=2000,  # 2000 km/mês
            fuel_price_per_liter=5.20
        )
        
        result = calculator.calculate_fuel_monthly(
            fuel_efficiency_km_per_liter=13.0
        )
        
        # 2000 km / 13 km/L = 153.85 L
        # 153.85 L * R$ 5.20 = R$ 800
        expected = (2000 / 13.0) * 5.20
        assert abs(result - expected) < 0.01


class TestMaintenanceEstimation:
    """Testes para estimativa de manutenção"""
    
    def test_estimate_maintenance_monthly_hatch(self):
        """Testa estimativa para Hatch"""
        calculator = TCOCalculator()
        
        result = calculator.estimate_maintenance_monthly(
            car_category="Hatch",
            car_age=0
        )
        
        # Hatch novo: R$ 1.500/ano = R$ 125/mês
        expected = 1500 / 12
        assert abs(result - expected) < 0.01
    
    def test_estimate_maintenance_monthly_suv(self):
        """Testa estimativa para SUV"""
        calculator = TCOCalculator()
        
        result = calculator.estimate_maintenance_monthly(
            car_category="SUV",
            car_age=0
        )
        
        # SUV novo: R$ 3.000/ano = R$ 250/mês
        expected = 3000 / 12
        assert abs(result - expected) < 0.01
    
    def test_estimate_maintenance_monthly_with_age(self):
        """Testa estimativa com carro usado"""
        calculator = TCOCalculator()
        
        result = calculator.estimate_maintenance_monthly(
            car_category="Hatch",
            car_age=5  # 5 anos
        )
        
        # Hatch 5 anos: R$ 1.500 * 1.5 = R$ 2.250/ano = R$ 187.50/mês
        expected = (1500 * 1.5) / 12
        assert abs(result - expected) < 0.01
    
    def test_estimate_maintenance_monthly_unknown_category(self):
        """Testa categoria desconhecida (usa padrão)"""
        calculator = TCOCalculator()
        
        result = calculator.estimate_maintenance_monthly(
            car_category="Categoria Inexistente",
            car_age=0
        )
        
        # Padrão: R$ 2.000/ano = R$ 166.67/mês
        expected = 2000 / 12
        assert abs(result - expected) < 0.01


class TestInsuranceEstimation:
    """Testes para estimativa de seguro"""
    
    def test_estimate_insurance_monthly_hatch(self):
        """Testa estimativa de seguro para Hatch"""
        calculator = TCOCalculator(user_profile="standard")
        
        result = calculator.estimate_insurance_monthly(
            car_price=70000,
            car_category="Hatch"
        )
        
        # Hatch: 3.5% ao ano
        # R$ 70.000 * 0.035 = R$ 2.450/ano = R$ 204.17/mês
        expected = (70000 * 0.035) / 12
        assert abs(result - expected) < 0.01
    
    def test_estimate_insurance_monthly_suv(self):
        """Testa estimativa de seguro para SUV"""
        calculator = TCOCalculator(user_profile="standard")
        
        result = calculator.estimate_insurance_monthly(
            car_price=100000,
            car_category="SUV"
        )
        
        # SUV: 5.5% ao ano
        # R$ 100.000 * 0.055 = R$ 5.500/ano = R$ 458.33/mês
        expected = (100000 * 0.055) / 12
        assert abs(result - expected) < 0.01
    
    def test_estimate_insurance_monthly_young_driver(self):
        """Testa seguro para motorista jovem"""
        calculator = TCOCalculator(user_profile="young")
        
        result = calculator.estimate_insurance_monthly(
            car_price=70000,
            car_category="Hatch"
        )
        
        # Jovem paga 30% a mais
        # R$ 70.000 * 0.035 * 1.3 = R$ 3.185/ano = R$ 265.42/mês
        expected = (70000 * 0.035 * 1.3) / 12
        assert abs(result - expected) < 0.01
    
    def test_estimate_insurance_monthly_senior_driver(self):
        """Testa seguro para motorista idoso"""
        calculator = TCOCalculator(user_profile="senior")
        
        result = calculator.estimate_insurance_monthly(
            car_price=70000,
            car_category="Hatch"
        )
        
        # Idoso paga 10% a menos
        # R$ 70.000 * 0.035 * 0.9 = R$ 2.205/ano = R$ 183.75/mês
        expected = (70000 * 0.035 * 0.9) / 12
        assert abs(result - expected) < 0.01


class TestIPVACalculation:
    """Testes para cálculo de IPVA"""
    
    def test_calculate_ipva_monthly_sp(self):
        """Testa IPVA em São Paulo"""
        calculator = TCOCalculator(state="SP")
        
        result = calculator.calculate_ipva_monthly(car_price=70000)
        
        # SP: 4% ao ano
        # R$ 70.000 * 0.04 = R$ 2.800/ano = R$ 233.33/mês
        expected = (70000 * 0.04) / 12
        assert abs(result - expected) < 0.01
    
    def test_calculate_ipva_monthly_sc(self):
        """Testa IPVA em Santa Catarina"""
        calculator = TCOCalculator(state="SC")
        
        result = calculator.calculate_ipva_monthly(car_price=70000)
        
        # SC: 2% ao ano
        # R$ 70.000 * 0.02 = R$ 1.400/ano = R$ 116.67/mês
        expected = (70000 * 0.02) / 12
        assert abs(result - expected) < 0.01
    
    def test_calculate_ipva_monthly_rs(self):
        """Testa IPVA no Rio Grande do Sul"""
        calculator = TCOCalculator(state="RS")
        
        result = calculator.calculate_ipva_monthly(car_price=70000)
        
        # RS: 3% ao ano
        # R$ 70.000 * 0.03 = R$ 2.100/ano = R$ 175/mês
        expected = (70000 * 0.03) / 12
        assert abs(result - expected) < 0.01
    
    def test_calculate_ipva_monthly_unknown_state(self):
        """Testa IPVA em estado desconhecido (usa padrão)"""
        calculator = TCOCalculator(state="XX")
        
        result = calculator.calculate_ipva_monthly(car_price=70000)
        
        # Padrão: 4% ao ano
        expected = (70000 * 0.04) / 12
        assert abs(result - expected) < 0.01


class TestCompleteTCO:
    """Testes para cálculo completo de TCO"""
    
    def test_calculate_tco_complete(self):
        """Testa cálculo completo de TCO"""
        calculator = TCOCalculator(
            down_payment_percent=0.20,
            financing_months=60,
            annual_interest_rate=0.12,
            monthly_km=1000,
            fuel_price_per_liter=5.20,
            state="SP",
            user_profile="standard"
        )
        
        result = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=0
        )
        
        # Verificar que todos os componentes estão presentes
        assert result.financing_monthly > 0
        assert result.fuel_monthly > 0
        assert result.maintenance_monthly > 0
        assert result.insurance_monthly > 0
        assert result.ipva_monthly > 0
        
        # Verificar que o total é a soma dos componentes
        expected_total = (
            result.financing_monthly +
            result.fuel_monthly +
            result.maintenance_monthly +
            result.insurance_monthly +
            result.ipva_monthly
        )
        assert abs(result.total_monthly - expected_total) < 0.01
        
        # Verificar que assumptions estão presentes
        assert result.assumptions["down_payment_percent"] == 20
        assert result.assumptions["financing_months"] == 60
        assert result.assumptions["monthly_km"] == 1000
        assert result.assumptions["state"] == "SP"
    
    def test_calculate_tco_realistic_values(self):
        """Testa TCO com valores realistas"""
        calculator = TCOCalculator()
        
        result = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=0
        )
        
        # TCO total deve estar em uma faixa realista
        # Para um carro de R$ 70k, esperamos entre R$ 2.000 e R$ 2.500/mês
        assert 2000 <= result.total_monthly <= 2700
    
    def test_calculate_tco_expensive_car(self):
        """Testa TCO para carro mais caro"""
        calculator = TCOCalculator()
        
        result = calculator.calculate_tco(
            car_price=150000,
            car_category="SUV",
            fuel_efficiency_km_per_liter=10.0,
            car_age=0
        )
        
        # TCO deve ser proporcionalmente maior
        assert result.total_monthly > 3500
    
    def test_calculate_tco_used_car(self):
        """Testa TCO para carro usado"""
        calculator = TCOCalculator()
        
        result_new = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=0
        )
        
        result_used = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=5
        )
        
        # Carro usado deve ter manutenção mais cara
        assert result_used.maintenance_monthly > result_new.maintenance_monthly


class TestMaxTCOCalculation:
    """Testes para cálculo de TCO máximo por faixa de renda"""
    
    def test_calculate_max_monthly_tco_low_income(self):
        """Testa TCO máximo para renda baixa"""
        result = TCOCalculator.calculate_max_monthly_tco("0-3000")
        
        # Média: R$ 1.500, 30% = R$ 450
        expected = 1500 * 0.30
        assert result == expected
    
    def test_calculate_max_monthly_tco_medium_income(self):
        """Testa TCO máximo para renda média"""
        result = TCOCalculator.calculate_max_monthly_tco("5000-8000")
        
        # Média: R$ 6.500, 30% = R$ 1.950
        expected = 6500 * 0.30
        assert result == expected
    
    def test_calculate_max_monthly_tco_high_income(self):
        """Testa TCO máximo para renda alta"""
        result = TCOCalculator.calculate_max_monthly_tco("12000+")
        
        # Média: R$ 14.000, 30% = R$ 4.200
        expected = 14000 * 0.30
        assert result == expected
    
    def test_calculate_max_monthly_tco_invalid_range(self):
        """Testa faixa de renda inválida"""
        result = TCOCalculator.calculate_max_monthly_tco("invalid")
        
        assert result == 0.0


class TestFinancingTermsValidation:
    """Testes para validação de termos de financiamento"""
    
    def test_validate_down_payment_within_range(self):
        """Testa validação de entrada dentro do range válido (0-100%)"""
        calculator = TCOCalculator()
        
        # Testar valores válidos
        valid_values = [0.0, 0.10, 0.20, 0.50, 0.80, 1.0]
        
        for value in valid_values:
            validated_down, _, _ = calculator.validate_financing_terms(
                down_payment_percent=value,
                financing_months=60,
                annual_interest_rate=0.12
            )
            assert validated_down == value
    
    def test_validate_down_payment_below_zero(self):
        """Testa validação de entrada negativa (deve usar default 20%)"""
        calculator = TCOCalculator()
        
        validated_down, _, _ = calculator.validate_financing_terms(
            down_payment_percent=-0.10,
            financing_months=60,
            annual_interest_rate=0.12
        )
        
        assert validated_down == 0.20  # Default
    
    def test_validate_down_payment_above_100(self):
        """Testa validação de entrada acima de 100% (deve usar default 20%)"""
        calculator = TCOCalculator()
        
        validated_down, _, _ = calculator.validate_financing_terms(
            down_payment_percent=1.5,  # 150%
            financing_months=60,
            annual_interest_rate=0.12
        )
        
        assert validated_down == 0.20  # Default
    
    def test_validate_months_within_range(self):
        """Testa validação de prazo dentro do range válido (12-84 meses)"""
        calculator = TCOCalculator()
        
        # Testar valores válidos
        valid_values = [12, 24, 36, 48, 60, 72, 84]
        
        for value in valid_values:
            _, validated_months, _ = calculator.validate_financing_terms(
                down_payment_percent=0.20,
                financing_months=value,
                annual_interest_rate=0.12
            )
            assert validated_months == value
    
    def test_validate_months_below_minimum(self):
        """Testa validação de prazo abaixo do mínimo (deve usar default 60)"""
        calculator = TCOCalculator()
        
        _, validated_months, _ = calculator.validate_financing_terms(
            down_payment_percent=0.20,
            financing_months=6,  # Abaixo de 12
            annual_interest_rate=0.12
        )
        
        assert validated_months == 60  # Default
    
    def test_validate_months_above_maximum(self):
        """Testa validação de prazo acima do máximo (deve usar default 60)"""
        calculator = TCOCalculator()
        
        _, validated_months, _ = calculator.validate_financing_terms(
            down_payment_percent=0.20,
            financing_months=120,  # Acima de 84
            annual_interest_rate=0.12
        )
        
        assert validated_months == 60  # Default
    
    def test_validate_interest_rate_within_range(self):
        """Testa validação de taxa de juros dentro do range válido"""
        calculator = TCOCalculator()
        
        # Testar valores válidos (6-60% ao ano = 0.5-5% ao mês)
        valid_values = [0.06, 0.12, 0.18, 0.24, 0.36, 0.48, 0.60]
        
        for value in valid_values:
            _, _, validated_rate = calculator.validate_financing_terms(
                down_payment_percent=0.20,
                financing_months=60,
                annual_interest_rate=value
            )
            assert validated_rate == value
    
    def test_validate_interest_rate_too_low(self):
        """Testa validação de taxa de juros muito baixa (deve usar default 12%)"""
        calculator = TCOCalculator()
        
        _, _, validated_rate = calculator.validate_financing_terms(
            down_payment_percent=0.20,
            financing_months=60,
            annual_interest_rate=0.03  # 3% ao ano = 0.25% ao mês (abaixo de 0.5%)
        )
        
        assert validated_rate == 0.24  # Default
    
    def test_validate_interest_rate_too_high(self):
        """Testa validação de taxa de juros muito alta (deve usar default 12%)"""
        calculator = TCOCalculator()
        
        _, _, validated_rate = calculator.validate_financing_terms(
            down_payment_percent=0.20,
            financing_months=60,
            annual_interest_rate=0.72  # 72% ao ano = 6% ao mês (acima de 5%)
        )
        
        assert validated_rate == 0.24  # Default
    
    def test_validate_all_terms_invalid(self):
        """Testa validação quando todos os termos são inválidos"""
        calculator = TCOCalculator()
        
        validated_down, validated_months, validated_rate = calculator.validate_financing_terms(
            down_payment_percent=2.0,  # Inválido
            financing_months=200,      # Inválido
            annual_interest_rate=1.0   # Inválido
        )
        
        # Todos devem usar defaults
        assert validated_down == 0.20
        assert validated_months == 60
        assert validated_rate == 0.24
    
    def test_validate_terms_used_in_tco_calculation(self):
        """Testa que termos validados são usados no cálculo de TCO"""
        calculator = TCOCalculator(
            down_payment_percent=2.0,  # Inválido
            financing_months=200,      # Inválido
            annual_interest_rate=1.0   # Inválido
        )
        
        result = calculator.calculate_tco(
            car_price=70000,
            car_category="Hatch",
            fuel_efficiency_km_per_liter=13.0,
            car_age=0,
            car_mileage=0
        )
        
        # Verificar que assumptions usam valores validados (defaults)
        assert result.assumptions["down_payment_percent"] == 20  # 0.20 * 100
        assert result.assumptions["financing_months"] == 60
        assert result.assumptions["annual_interest_rate"] == 24.0  # 0.24 * 100


class TestIncomeRangeInfo:
    """Testes para informações de faixa de renda"""
    
    def test_get_income_range_info_complete(self):
        """Testa informações completas de faixa de renda"""
        result = TCOCalculator.get_income_range_info("5000-8000")
        
        assert result["income_range"] == "5000-8000"
        assert result["max_monthly_tco"] > 0
        assert result["estimated_max_car_price"] > 0
        assert result["recommended_percentage"] == 30
    
    def test_get_income_range_info_all_ranges(self):
        """Testa todas as faixas de renda"""
        ranges = ["0-3000", "3000-5000", "5000-8000", "8000-12000", "12000+"]
        
        for income_range in ranges:
            result = TCOCalculator.get_income_range_info(income_range)
            
            assert result["income_range"] == income_range
            assert result["max_monthly_tco"] > 0
            assert result["estimated_max_car_price"] > 0


class TestTCOBreakdownModel:
    """Testes para modelo TCOBreakdown"""
    
    def test_tco_breakdown_creation(self):
        """Testa criação de TCOBreakdown"""
        breakdown = TCOBreakdown(
            financing_monthly=1200.00,
            fuel_monthly=400.00,
            maintenance_monthly=150.00,
            insurance_monthly=200.00,
            ipva_monthly=233.33,
            total_monthly=2183.33
        )
        
        assert breakdown.financing_monthly == 1200.00
        assert breakdown.fuel_monthly == 400.00
        assert breakdown.maintenance_monthly == 150.00
        assert breakdown.insurance_monthly == 200.00
        assert breakdown.ipva_monthly == 233.33
        assert breakdown.total_monthly == 2183.33
    
    def test_tco_breakdown_with_assumptions(self):
        """Testa TCOBreakdown com assumptions customizados"""
        breakdown = TCOBreakdown(
            financing_monthly=1200.00,
            fuel_monthly=400.00,
            maintenance_monthly=150.00,
            insurance_monthly=200.00,
            ipva_monthly=233.33,
            total_monthly=2183.33,
            assumptions={
                "down_payment_percent": 30,
                "financing_months": 48,
                "monthly_km": 2000,
                "fuel_price_per_liter": 6.00,
                "state": "RJ"
            }
        )
        
        assert breakdown.assumptions["down_payment_percent"] == 30
        assert breakdown.assumptions["financing_months"] == 48
        assert breakdown.assumptions["monthly_km"] == 2000
