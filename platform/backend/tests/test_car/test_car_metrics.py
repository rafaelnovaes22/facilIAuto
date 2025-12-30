
import pytest
from datetime import datetime
from services.car.car_metrics import CarMetricsCalculator

class TestCarMetricsCalculator:
    
    @pytest.fixture
    def calculator(self):
        return CarMetricsCalculator()
        
    def test_reliability_toyota_new_low_km(self, calculator):
        """Toyota novo e pouco rodado deve ter confiabilidade alta"""
        # Toyota (0.95), Ano atual (0 penalty), Baixa KM (0 penalty)
        score = calculator.calculate_reliability_index(
            marca="Toyota",
            ano=datetime.now().year,
            quilometragem=10000
        )
        assert score == 0.95
        
    def test_reliability_fiat_old_high_km(self, calculator):
        """Fiat antigo e muito rodado deve ter confiabilidade baixa"""
        # Fiat (0.62)
        # Antigo (>10 anos) -> -0.20
        # Alta KM (>100k) -> -0.15
        current_year = datetime.now().year
        score = calculator.calculate_reliability_index(
            marca="Fiat",
            ano=current_year - 11,
            quilometragem=150000
        )
        expected = 0.62 - 0.20 - 0.15
        assert abs(score - expected) < 0.001
        
    def test_resale_index_suv_boost(self, calculator):
        """SUV deve ter boost de revenda"""
        # Honda (0.90) + SUV (0.10) - Idade 0 (0.0) = 1.0 (max)
        score = calculator.calculate_resale_index(
            marca="Honda",
            categoria="SUV",
            ano=datetime.now().year
        )
        assert score == 1.0
        
    def test_depreciation_premium_brand(self, calculator):
        """Marca premium deve depreciar mais"""
        # BMW (+3%)
        # Ano 2-3 (0%)
        # Base Sedan (16%)
        # Total = 19%
        rate = calculator.calculate_depreciation_rate(
            marca="BMW",
            categoria="Sedan",
            ano=datetime.now().year - 2
        )
        assert abs(rate - 0.19) < 0.001
        
    def test_maintenance_cost_increase_with_age(self, calculator):
        """Manutenção deve aumentar com a idade"""
        # Toyota base: 2200
        
        # Novo
        cost_new = calculator.estimate_maintenance_cost(
            marca="Toyota",
            ano=datetime.now().year,
            quilometragem=10000
        )
        assert cost_new == 2200
        
        # Velho (>10 anos -> x1.5)
        cost_old = calculator.estimate_maintenance_cost(
            marca="Toyota",
            ano=datetime.now().year - 11,
            quilometragem=10000
        )
        assert cost_old == 2200 * 1.5
        
    def test_calculate_all_metrics(self, calculator):
        """Deve retornar dicionário com todas as métricas"""
        metrics = calculator.calculate_all_metrics(
            marca="Toyota",
            categoria="Sedan",
            ano=2022,
            quilometragem=30000
        )
        
        assert "indice_confiabilidade" in metrics
        assert "indice_revenda" in metrics
        assert "taxa_depreciacao_anual" in metrics
        assert "custo_manutencao_anual" in metrics
        
    def test_tco_calculation(self, calculator):
        """Cálculo de TCO em 5 anos"""
        result = calculator.get_car_total_cost_5_years(
            preco=100000,
            taxa_depreciacao=0.10,  # 10%
            custo_manutencao=2000   # 2k/ano
        )
        
        # Ano 1: Depr 10k (Valor 90k), Manut 2k
        # Ano 2: Depr 9k (Valor 81k), Manut 2k
        # Ano 3: Depr 8.1k (Valor 72.9k), Manut 2k
        # Ano 4: Depr 7.29k (Valor 65.61k), Manut 2k
        # Ano 5: Depr 6.561k (Valor 59.049k), Manut 2k
        
        # Manut total: 10k
        assert result["manutencao_total"] == 10000
        
        # Valor final aprox 59k
        assert 59000 < result["valor_final"] < 59100
