"""
Tech Lead + Data Analyst: Testes para Métricas Avançadas - FASE 3

Testa os novos cálculos implementados:
- Índice de confiabilidade
- Índice de revenda
- Taxa de depreciação
- Custo de manutenção
- TCO (Total Cost of Ownership)

Autor: Tech Lead + Data Analyst
Data: Outubro 2024
"""

import pytest
from datetime import datetime

from models.car import Car
from models.user_profile import UserProfile
from services.car_metrics import CarMetricsCalculator
from services.unified_recommendation_engine import UnifiedRecommendationEngine


class TestCarMetricsCalculatorBasic:
    """Testes básicos para CarMetricsCalculator"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.calculator = CarMetricsCalculator()
    
    def test_calculator_initialization(self):
        """Testar inicialização do calculador"""
        assert self.calculator is not None
        assert hasattr(self.calculator, 'BRAND_RELIABILITY')
        assert hasattr(self.calculator, 'BRAND_RESALE_INDEX')
        assert hasattr(self.calculator, 'DEPRECIATION_BY_CATEGORY')


class TestReliabilityIndex:
    """Testes para cálculo de índice de confiabilidade"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.calculator = CarMetricsCalculator()
        self.current_year = datetime.now().year
    
    def test_reliability_toyota_new_low_km(self):
        """Toyota 2024 com baixa quilometragem - alta confiabilidade"""
        reliability = self.calculator.calculate_reliability_index(
            marca="Toyota",
            ano=2024,
            quilometragem=5000
        )
        
        # Toyota tem base 0.95, carro novo e baixa km = mínima penalidade
        assert 0.92 <= reliability <= 0.95
        assert isinstance(reliability, float)
    
    def test_reliability_fiat_old_high_km(self):
        """Fiat 2015 com alta quilometragem - baixa confiabilidade"""
        reliability = self.calculator.calculate_reliability_index(
            marca="Fiat",
            ano=2015,
            quilometragem=150000
        )
        
        # Fiat tem base 0.62, carro velho e alta km = muita penalidade
        assert 0.30 <= reliability <= 0.50
        assert isinstance(reliability, float)
    
    def test_reliability_honda_medium(self):
        """Honda 2020 com km média - confiabilidade média-alta"""
        reliability = self.calculator.calculate_reliability_index(
            marca="Honda",
            ano=2020,
            quilometragem=60000
        )
        
        # Honda tem base 0.93, alguns anos e km média
        assert 0.75 <= reliability <= 0.88
    
    def test_reliability_unknown_brand(self):
        """Marca desconhecida - usar valor default"""
        reliability = self.calculator.calculate_reliability_index(
            marca="MarcaInexistente",
            ano=2023,
            quilometragem=10000
        )
        
        # Deve usar DEFAULT (0.65)
        assert 0.60 <= reliability <= 0.70
    
    def test_reliability_age_penalty(self):
        """Penalidade por idade - comparar mesmo carro em anos diferentes"""
        rel_2024 = self.calculator.calculate_reliability_index(
            marca="Toyota",
            ano=2024,
            quilometragem=10000
        )
        
        rel_2020 = self.calculator.calculate_reliability_index(
            marca="Toyota",
            ano=2020,
            quilometragem=10000
        )
        
        # Carro mais novo deve ter maior confiabilidade
        assert rel_2024 > rel_2020
    
    def test_reliability_km_penalty(self):
        """Penalidade por quilometragem - comparar mesmo carro com km diferentes"""
        rel_low_km = self.calculator.calculate_reliability_index(
            marca="Toyota",
            ano=2022,
            quilometragem=10000
        )
        
        rel_high_km = self.calculator.calculate_reliability_index(
            marca="Toyota",
            ano=2022,
            quilometragem=100000
        )
        
        # Carro com menos km deve ter maior confiabilidade
        assert rel_low_km > rel_high_km
    
    def test_reliability_bounds(self):
        """Confiabilidade deve estar sempre entre 0 e 1"""
        # Teste extremo: carro muito velho com muita km
        reliability = self.calculator.calculate_reliability_index(
            marca="Fiat",
            ano=2005,
            quilometragem=300000
        )
        
        assert 0.0 <= reliability <= 1.0


class TestResaleIndex:
    """Testes para cálculo de índice de revenda"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.calculator = CarMetricsCalculator()
    
    def test_resale_toyota_low_km(self):
        """Toyota com baixa km - excelente revenda"""
        resale = self.calculator.calculate_resale_index(
            marca="Toyota",
            quilometragem=20000
        )
        
        # Toyota tem base 0.92, baixa km = boost
        assert 0.88 <= resale <= 0.95
    
    def test_resale_fiat_high_km(self):
        """Fiat com alta km - revenda prejudicada"""
        resale = self.calculator.calculate_resale_index(
            marca="Fiat",
            quilometragem=120000
        )
        
        # Fiat tem base 0.72, alta km = penalidade
        assert 0.50 <= resale <= 0.68
    
    def test_resale_km_penalty_progression(self):
        """Penalidade aumenta progressivamente com km"""
        resale_30k = self.calculator.calculate_resale_index(
            marca="Honda",
            quilometragem=30000
        )
        
        resale_60k = self.calculator.calculate_resale_index(
            marca="Honda",
            quilometragem=60000
        )
        
        resale_120k = self.calculator.calculate_resale_index(
            marca="Honda",
            quilometragem=120000
        )
        
        # Deve diminuir progressivamente
        assert resale_30k > resale_60k > resale_120k
    
    def test_resale_unknown_brand(self):
        """Marca desconhecida - usar default"""
        resale = self.calculator.calculate_resale_index(
            marca="MarcaDesconhecida",
            quilometragem=50000
        )
        
        # Deve usar DEFAULT (0.70)
        assert 0.60 <= resale <= 0.75
    
    def test_resale_bounds(self):
        """Índice de revenda deve estar entre 0 e 1"""
        resale = self.calculator.calculate_resale_index(
            marca="Fiat",
            quilometragem=250000
        )
        
        assert 0.0 <= resale <= 1.0


class TestDepreciationRate:
    """Testes para cálculo de taxa de depreciação"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.calculator = CarMetricsCalculator()
        self.current_year = datetime.now().year
    
    def test_depreciation_suv_low(self):
        """SUV deprecia menos (12-14% ao ano)"""
        depreciation = self.calculator.calculate_depreciation_rate(
            categoria="SUV",
            ano=2023
        )
        
        # SUV base = 0.14 (14%)
        assert 0.12 <= depreciation <= 0.18
        assert isinstance(depreciation, float)
    
    def test_depreciation_hatch_high(self):
        """Hatch deprecia mais (18-20% ao ano)"""
        depreciation = self.calculator.calculate_depreciation_rate(
            categoria="Hatch",
            ano=2023
        )
        
        # Hatch base = 0.18 (18%)
        assert 0.16 <= depreciation <= 0.22
    
    def test_depreciation_first_year_penalty(self):
        """Primeiro ano tem penalidade extra (20%)"""
        current_year = datetime.now().year
        
        dep_first_year = self.calculator.calculate_depreciation_rate(
            categoria="Sedan",
            ano=current_year  # Ano atual = primeiro ano
        )
        
        dep_second_year = self.calculator.calculate_depreciation_rate(
            categoria="Sedan",
            ano=current_year - 1
        )
        
        # Primeiro ano deve depreciar mais
        assert dep_first_year > dep_second_year
    
    def test_depreciation_category_comparison(self):
        """Comparar depreciação entre categorias (mesmo ano)"""
        dep_suv = self.calculator.calculate_depreciation_rate(
            categoria="SUV",
            ano=2022
        )
        
        dep_sedan = self.calculator.calculate_depreciation_rate(
            categoria="Sedan",
            ano=2022
        )
        
        dep_hatch = self.calculator.calculate_depreciation_rate(
            categoria="Hatch",
            ano=2022
        )
        
        # SUV < Sedan < Hatch
        assert dep_suv < dep_sedan < dep_hatch
    
    def test_depreciation_unknown_category(self):
        """Categoria desconhecida - usar default"""
        depreciation = self.calculator.calculate_depreciation_rate(
            categoria="CategoriaInexistente",
            ano=2023
        )
        
        # Deve usar DEFAULT (0.15 = 15%)
        assert 0.13 <= depreciation <= 0.18
    
    def test_depreciation_bounds(self):
        """Taxa de depreciação deve ser positiva e razoável"""
        depreciation = self.calculator.calculate_depreciation_rate(
            categoria="Hatch",
            ano=datetime.now().year
        )
        
        # Não deve ultrapassar ~25% ao ano
        assert 0.0 < depreciation < 0.30


class TestMaintenanceCost:
    """Testes para estimativa de custo de manutenção"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.calculator = CarMetricsCalculator()
    
    def test_maintenance_toyota_economica(self):
        """Toyota - manutenção econômica"""
        cost = self.calculator.estimate_maintenance_cost(
            marca="Toyota",
            categoria="Sedan",
            ano=2023,
            quilometragem=10000
        )
        
        # Toyota base = R$ 2.200/ano
        assert 2000 <= cost <= 2800
        assert isinstance(cost, float)
    
    def test_maintenance_bmw_premium(self):
        """BMW - manutenção cara"""
        cost = self.calculator.estimate_maintenance_cost(
            marca="BMW",
            categoria="Sedan",
            ano=2023,
            quilometragem=10000
        )
        
        # BMW base = R$ 6.500/ano (premium)
        assert 6000 <= cost <= 7500
    
    def test_maintenance_age_increase(self):
        """Custo aumenta com idade do carro"""
        cost_new = self.calculator.estimate_maintenance_cost(
            marca="Honda",
            categoria="Sedan",
            ano=2024,
            quilometragem=5000
        )
        
        cost_old = self.calculator.estimate_maintenance_cost(
            marca="Honda",
            categoria="Sedan",
            ano=2015,
            quilometragem=5000
        )
        
        # Carro mais velho = maior custo
        assert cost_old > cost_new
    
    def test_maintenance_km_increase(self):
        """Custo aumenta com quilometragem"""
        cost_low_km = self.calculator.estimate_maintenance_cost(
            marca="Honda",
            categoria="Sedan",
            ano=2022,
            quilometragem=10000
        )
        
        cost_high_km = self.calculator.estimate_maintenance_cost(
            marca="Honda",
            categoria="Sedan",
            ano=2022,
            quilometragem=100000
        )
        
        # Alta km = maior custo
        assert cost_high_km > cost_low_km
    
    def test_maintenance_suv_penalty(self):
        """SUV tem custo 15% maior"""
        cost_sedan = self.calculator.estimate_maintenance_cost(
            marca="Toyota",
            categoria="Sedan",
            ano=2023,
            quilometragem=10000
        )
        
        cost_suv = self.calculator.estimate_maintenance_cost(
            marca="Toyota",
            categoria="SUV",
            ano=2023,
            quilometragem=10000
        )
        
        # SUV deve custar ~15% a mais
        assert cost_suv > cost_sedan
        assert cost_suv >= cost_sedan * 1.10
    
    def test_maintenance_unknown_brand(self):
        """Marca desconhecida - usar default"""
        cost = self.calculator.estimate_maintenance_cost(
            marca="MarcaDesconhecida",
            categoria="Sedan",
            ano=2023,
            quilometragem=30000
        )
        
        # Deve usar DEFAULT
        assert cost > 0
        assert isinstance(cost, float)
    
    def test_maintenance_minimum_cost(self):
        """Custo mínimo sempre positivo"""
        cost = self.calculator.estimate_maintenance_cost(
            marca="Hyundai",
            categoria="Hatch",
            ano=2024,
            quilometragem=0
        )
        
        assert cost > 1500  # Mínimo razoável
        assert cost < 10000  # Máximo razoável para econômico


class TestCalculateAllMetrics:
    """Testes para cálculo completo de todas as métricas"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.calculator = CarMetricsCalculator()
    
    def test_calculate_all_metrics_complete(self):
        """Calcular todas as métricas de uma vez"""
        metrics = self.calculator.calculate_all_metrics(
            marca="Toyota",
            categoria="SUV",
            ano=2023,
            quilometragem=15000
        )
        
        # Verificar que todos os campos existem
        assert "indice_confiabilidade" in metrics
        assert "indice_revenda" in metrics
        assert "taxa_depreciacao_anual" in metrics
        assert "custo_manutencao_anual" in metrics
        
        # Verificar tipos e bounds
        assert 0.0 <= metrics["indice_confiabilidade"] <= 1.0
        assert 0.0 <= metrics["indice_revenda"] <= 1.0
        assert 0.0 < metrics["taxa_depreciacao_anual"] < 0.30
        assert metrics["custo_manutencao_anual"] > 0
    
    def test_calculate_all_metrics_consistency(self):
        """Métricas devem ser consistentes"""
        metrics = self.calculator.calculate_all_metrics(
            marca="Honda",
            categoria="Sedan",
            ano=2022,
            quilometragem=30000
        )
        
        # Honda deve ter boa confiabilidade e revenda
        assert metrics["indice_confiabilidade"] >= 0.80
        assert metrics["indice_revenda"] >= 0.75


class TestTotalCostOfOwnership:
    """Testes para cálculo de TCO (Total Cost of Ownership)"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.calculator = CarMetricsCalculator()
    
    def test_tco_5_years_basic(self):
        """TCO básico para 5 anos"""
        tco = self.calculator.get_car_total_cost_5_years(
            preco_compra=100000,
            marca="Toyota",
            categoria="Sedan",
            ano=2023,
            quilometragem=10000
        )
        
        # TCO deve incluir depreciação + manutenção
        assert tco > 100000  # Maior que preço de compra
        assert isinstance(tco, float)
    
    def test_tco_premium_higher(self):
        """TCO de carro premium deve ser maior"""
        tco_economico = self.calculator.get_car_total_cost_5_years(
            preco_compra=80000,
            marca="Fiat",
            categoria="Hatch",
            ano=2023,
            quilometragem=10000
        )
        
        tco_premium = self.calculator.get_car_total_cost_5_years(
            preco_compra=80000,
            marca="BMW",
            categoria="Sedan",
            ano=2023,
            quilometragem=10000
        )
        
        # Premium tem maior custo de manutenção
        assert tco_premium > tco_economico
    
    def test_tco_depreciation_included(self):
        """TCO deve incluir depreciação"""
        preco = 120000
        tco = self.calculator.get_car_total_cost_5_years(
            preco_compra=preco,
            marca="Honda",
            categoria="SUV",
            ano=2024,
            quilometragem=0
        )
        
        # Valor residual será menor devido à depreciação
        # TCO = depreciação acumulada + manutenção
        assert tco < preco  # Pois considera valor residual


class TestMetricsIntegration:
    """Testes de integração das métricas com UserProfile e Car"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.calculator = CarMetricsCalculator()
    
    def test_car_model_has_metrics_fields(self):
        """Modelo Car deve ter campos de métricas"""
        car = Car(
            id="test_car",
            dealership_id="d1",
            nome="Corolla 2024",
            marca="Toyota",
            modelo="Corolla",
            ano=2024,
            preco=135990,
            quilometragem=0,
            combustivel="Flex",
            categoria="Sedan",
            dealership_name="Test",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="111",
            dealership_whatsapp="111",
            indice_confiabilidade=0.93,
            indice_revenda=0.90,
            taxa_depreciacao_anual=0.16,
            custo_manutencao_anual=2200.0
        )
        
        assert hasattr(car, 'indice_confiabilidade')
        assert hasattr(car, 'indice_revenda')
        assert hasattr(car, 'taxa_depreciacao_anual')
        assert hasattr(car, 'custo_manutencao_anual')
        
        assert car.indice_confiabilidade == 0.93
        assert car.indice_revenda == 0.90
    
    def test_user_profile_has_new_priorities(self):
        """UserProfile deve ter novas prioridades FASE 3"""
        profile = UserProfile(
            orcamento_min=80000,
            orcamento_max=150000,
            uso_principal="trabalho",
            prioridades={
                "economia": 3,
                "espaco": 3,
                "performance": 3,
                "conforto": 3,
                "seguranca": 3,
                "revenda": 5,           # FASE 3
                "confiabilidade": 5,    # FASE 3
                "custo_manutencao": 4   # FASE 3
            }
        )
        
        assert profile.prioridades["revenda"] == 5
        assert profile.prioridades["confiabilidade"] == 5
        assert profile.prioridades["custo_manutencao"] == 4


class TestMetricsEdgeCases:
    """Testes de casos extremos e edge cases"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.calculator = CarMetricsCalculator()
    
    def test_very_old_car(self):
        """Carro muito antigo (>15 anos)"""
        metrics = self.calculator.calculate_all_metrics(
            marca="Fiat",
            categoria="Hatch",
            ano=2005,
            quilometragem=250000
        )
        
        # Confiabilidade deve ser muito baixa
        assert metrics["indice_confiabilidade"] < 0.40
        # Revenda muito prejudicada
        assert metrics["indice_revenda"] < 0.50
        # Custo de manutenção alto
        assert metrics["custo_manutencao_anual"] > 3000
    
    def test_brand_new_car(self):
        """Carro zero km"""
        metrics = self.calculator.calculate_all_metrics(
            marca="Toyota",
            categoria="SUV",
            ano=datetime.now().year,
            quilometragem=0
        )
        
        # Máxima confiabilidade
        assert metrics["indice_confiabilidade"] >= 0.92
        # Boa revenda
        assert metrics["indice_revenda"] >= 0.88
        # Depreciação maior no primeiro ano
        assert metrics["taxa_depreciacao_anual"] >= 0.14
    
    def test_extreme_mileage(self):
        """Quilometragem extremamente alta"""
        resale = self.calculator.calculate_resale_index(
            marca="Toyota",
            quilometragem=300000
        )
        
        # Revenda muito prejudicada, mas não zero
        assert 0.30 <= resale <= 0.60
    
    def test_zero_mileage(self):
        """Quilometragem zero"""
        resale = self.calculator.calculate_resale_index(
            marca="Honda",
            quilometragem=0
        )
        
        # Máxima revenda
        assert resale >= 0.85


if __name__ == "__main__":
    print("Tech Lead: Executando testes FASE 3 - Metricas Avancadas")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "--tb=short"])

