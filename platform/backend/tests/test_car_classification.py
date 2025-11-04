"""
Testes para o sistema de classificação de veículos
Garante que motos não sejam classificadas como carros e vice-versa
"""

import pytest
from services.car_classifier import CarClassifier


class TestCarClassification:
    """Testes de classificação de veículos"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.classifier = CarClassifier()
    
    # ========== TESTES DE MOTOS ==========
    
    def test_yamaha_xtz_250_is_moto(self):
        """Yamaha XTZ 250 deve ser classificada como Moto"""
        result = self.classifier.classify(
            nome="Yamaha Xtz 250",
            modelo="Xtz 250",
            ano=2024,
            marca="YAMAHA"
        )
        assert result == 'Moto', "Yamaha XTZ 250 deve ser Moto"
    
    def test_yamaha_neo_is_moto(self):
        """Yamaha Neo Automatic (scooter) deve ser classificada como Moto"""
        result = self.classifier.classify(
            nome="Yamaha Neo Automatic",
            modelo="Neo Automatic",
            ano=2024,
            marca="YAMAHA"
        )
        assert result == 'Moto', "Yamaha Neo deve ser Moto (scooter)"
    
    def test_honda_cb_is_moto(self):
        """Honda CB deve ser classificada como Moto"""
        result = self.classifier.classify(
            nome="Honda CB 500",
            modelo="CB 500",
            ano=2024,
            marca="Honda"
        )
        assert result == 'Moto', "Honda CB deve ser Moto"
    
    def test_kawasaki_ninja_is_moto(self):
        """Kawasaki Ninja deve ser classificada como Moto"""
        result = self.classifier.classify(
            nome="Kawasaki Ninja 400",
            modelo="Ninja 400",
            ano=2024,
            marca="Kawasaki"
        )
        assert result == 'Moto', "Kawasaki Ninja deve ser Moto"
    
    def test_yamaha_brand_always_moto(self):
        """Qualquer Yamaha deve ser Moto (no Brasil, Yamaha só faz motos)"""
        result = self.classifier.classify(
            nome="Yamaha Fazer 250",
            modelo="Fazer 250",
            ano=2024,
            marca="YAMAHA"
        )
        assert result == 'Moto', "Yamaha só fabrica motos no Brasil"
    
    # ========== TESTES DE CARROS (NÃO MOTOS) ==========
    
    def test_chevrolet_onix_is_hatch(self):
        """Chevrolet Onix deve ser classificado como Hatch (não Moto)"""
        result = self.classifier.classify(
            nome="Chevrolet Onix Mt",
            modelo="Chevrolet Onix Mt",
            ano=2024,
            marca="Chevrolet"
        )
        assert result == 'Hatch', "Chevrolet Onix deve ser Hatch"
    
    def test_toyota_prius_is_hatch(self):
        """Toyota Prius deve ser classificado como Hatch (não Moto)"""
        result = self.classifier.classify(
            nome="Toyota Prius Hybrid",
            modelo="Toyota Prius Hybrid",
            ano=2024,
            marca="Toyota"
        )
        assert result == 'Hatch', "Toyota Prius deve ser Hatch"
    
    def test_mitsubishi_asx_is_suv(self):
        """Mitsubishi ASX deve ser classificado como SUV (não Moto)"""
        result = self.classifier.classify(
            nome="Mitsubishi Asx Cvt",
            modelo="Mitsubishi Asx Cvt",
            ano=2024,
            marca="Mitsubishi"
        )
        assert result == 'SUV', "Mitsubishi ASX deve ser SUV"
    
    def test_honda_civic_is_sedan(self):
        """Honda Civic deve ser classificado como Sedan (não confundir com Honda motos)"""
        result = self.classifier.classify(
            nome="Honda Civic 2.0 EX",
            modelo="Civic",
            ano=2024,
            marca="Honda"
        )
        assert result == 'Sedan', "Honda Civic deve ser Sedan"
    
    def test_honda_fit_is_hatch(self):
        """Honda Fit deve ser classificado como Hatch (não confundir com Honda motos)"""
        result = self.classifier.classify(
            nome="Honda Fit 1.5",
            modelo="Fit",
            ano=2024,
            marca="Honda"
        )
        assert result == 'Hatch', "Honda Fit deve ser Hatch"
    
    # ========== TESTES DE CATEGORIAS DE CARROS ==========
    
    def test_tracker_is_suv(self):
        """Chevrolet Tracker deve ser SUV"""
        result = self.classifier.classify(
            nome="Chevrolet Tracker T",
            modelo="Chevrolet Tracker T",
            ano=2025,
            marca="Chevrolet"
        )
        assert result == 'SUV', "Tracker deve ser SUV"
    
    def test_corolla_is_sedan(self):
        """Toyota Corolla deve ser Sedan"""
        result = self.classifier.classify(
            nome="Toyota Corolla Gli",
            modelo="Toyota Corolla Gli",
            ano=2022,
            marca="Toyota"
        )
        assert result == 'Sedan', "Corolla deve ser Sedan"
    
    def test_strada_is_pickup(self):
        """Fiat Strada deve ser Pickup"""
        result = self.classifier.classify(
            nome="Fiat Strada Volcano",
            modelo="Fiat Strada Volcano",
            ano=2025,
            marca="Fiat"
        )
        assert result == 'Pickup', "Strada deve ser Pickup"
    
    def test_gol_is_hatch(self):
        """Volkswagen Gol deve ser Hatch"""
        result = self.classifier.classify(
            nome="Volkswagen Gol 1.0",
            modelo="Gol",
            ano=2020,
            marca="Volkswagen"
        )
        assert result == 'Hatch', "Gol deve ser Hatch"
    
    def test_kwid_is_compacto(self):
        """Renault Kwid deve ser Compacto"""
        result = self.classifier.classify(
            nome="Renault Kwid Zen",
            modelo="Renault Kwid Zen",
            ano=2025,
            marca="Renault"
        )
        assert result == 'Compacto', "Kwid deve ser Compacto"
    
    # ========== TESTES DE EDGE CASES ==========
    
    def test_mt_in_model_name_not_always_moto(self):
        """'MT' no nome não significa necessariamente moto (pode ser Manual Transmission)"""
        result = self.classifier.classify(
            nome="Chevrolet Onix MT",
            modelo="Onix MT",
            ano=2024,
            marca="Chevrolet"
        )
        assert result == 'Hatch', "Onix MT deve ser Hatch (MT = Manual Transmission)"
    
    def test_cvt_in_model_name_is_car(self):
        """CVT no nome indica transmissão automática (carro, não moto)"""
        result = self.classifier.classify(
            nome="Nissan Kicks CVT",
            modelo="Kicks CVT",
            ano=2024,
            marca="Nissan"
        )
        assert result == 'SUV', "Kicks CVT deve ser SUV"
    
    def test_hybrid_is_car(self):
        """Hybrid no nome indica carro híbrido"""
        result = self.classifier.classify(
            nome="Toyota Prius Hybrid",
            modelo="Prius Hybrid",
            ano=2024,
            marca="Toyota"
        )
        assert result == 'Hatch', "Prius Hybrid deve ser Hatch"
    
    # ========== TESTES DE REGRESSÃO (BUGS ENCONTRADOS) ==========
    
    def test_regression_yamaha_neo_not_hatch(self):
        """
        REGRESSÃO: Yamaha Neo foi classificada como Hatch
        Deve ser Moto (scooter)
        """
        result = self.classifier.classify(
            nome="Yamaha Neo Automatic",
            modelo="Neo Automatic",
            ano=2024,
            marca="YAMAHA"
        )
        assert result == 'Moto', "BUG: Yamaha Neo foi classificada como Hatch"
    
    def test_regression_onix_not_moto(self):
        """
        REGRESSÃO: Chevrolet Onix foi classificado como Moto
        Deve ser Hatch
        """
        result = self.classifier.classify(
            nome="Chevrolet Onix Mt",
            modelo="Chevrolet Onix Mt",
            ano=2024,
            marca="Chevrolet"
        )
        assert result == 'Hatch', "BUG: Onix foi classificado como Moto"
    
    def test_price_range_10k_15k_no_motos(self):
        """
        REGRESSÃO: Busca por faixa de preço R$ 10k-15k retornou moto
        Motos devem ter disponivel=False para não aparecer em buscas de carros
        """
        # Este teste verifica a lógica, não o classificador diretamente
        # Mas documenta o requisito: motos devem ter disponivel=False
        pass


class TestCarClassifierFeatures:
    """Testes para características típicas de veículos"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.classifier = CarClassifier()
    
    def test_safety_items_2024_suv(self):
        """SUV 2024 deve ter itens de segurança modernos"""
        items = self.classifier.get_typical_safety_items(
            ano=2024,
            categoria='SUV',
            modelo='Tracker Premier'
        )
        assert 'ABS' in items
        assert 'airbag' in items
        assert '6_airbags' in items
        assert 'ISOFIX' in items
    
    def test_comfort_items_suv(self):
        """SUV deve ter mais itens de conforto"""
        items = self.classifier.get_typical_comfort_items(
            categoria='SUV',
            ano=2024,
            modelo='Tracker Premier'
        )
        assert 'ar_condicionado' in items
        assert 'direcao_eletrica' in items
        assert 'vidro_eletrico' in items
    
    def test_premium_version_detection(self):
        """Detectar versões premium"""
        assert self.classifier.is_premium_version('Tracker Premier')
        assert self.classifier.is_premium_version('Onix LTZ')
        assert not self.classifier.is_premium_version('Gol 1.0')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
