"""
Testes para o sistema de classificação de carros
"""

import pytest
from services.car_classifier import classifier


class TestCarClassifier:
    """Testes do classificador de carros"""
    
    def test_ford_focus_2009_2013_is_sedan(self):
        """Ford Focus 2009-2013 deve ser classificado como Sedan"""
        assert classifier.classify("Ford Focus", "Ford Focus", 2009) == "Sedan"
        assert classifier.classify("Ford Focus", "Ford Focus", 2010) == "Sedan"
        assert classifier.classify("Ford Focus", "Ford Focus", 2013) == "Sedan"
    
    def test_ford_focus_2014_plus_is_hatch(self):
        """Ford Focus 2014+ deve ser classificado como Hatch"""
        assert classifier.classify("Ford Focus", "Ford Focus", 2014) == "Hatch"
        assert classifier.classify("Ford Focus", "Ford Focus", 2015) == "Hatch"
        assert classifier.classify("Ford Focus", "Ford Focus", 2020) == "Hatch"
    
    def test_ford_focus_sedan_explicit(self):
        """Ford Focus com 'Sedan' no nome sempre é Sedan"""
        assert classifier.classify("Ford Focus Sedan", "Ford Focus Sedan", 2015) == "Sedan"
        assert classifier.classify("Ford Focus Sedan", "Ford Focus Sedan", 2020) == "Sedan"
    
    def test_motorcycles_detected(self):
        """Motos devem ser detectadas corretamente"""
        # Honda
        assert classifier.classify("Honda CB 500", "Honda CB 500", 2020) == "Moto"
        assert classifier.classify("Honda CBR 600", "Honda CBR 600", 2021) == "Moto"
        
        # Yamaha
        assert classifier.classify("Yamaha MT-07", "Yamaha MT-07", 2021) == "Moto"
        assert classifier.classify("Yamaha Xtz 250", "Yamaha Xtz 250", 2024) == "Moto"
        assert classifier.classify("Yamaha Fazer 250", "Yamaha Fazer 250", 2020) == "Moto"
        
        # Kawasaki
        assert classifier.classify("Kawasaki Ninja 300", "Kawasaki Ninja 300", 2020) == "Moto"
    
    def test_cars_not_confused_with_motorcycles(self):
        """Carros não devem ser confundidos com motos"""
        # Onix MT (MT = Manual Transmission, não moto)
        assert classifier.classify("Chevrolet Onix Mt", "Chevrolet Onix Mt", 2019) == "Hatch"
        assert classifier.classify("Chevrolet Onix MT", "Chevrolet Onix MT", 2020) == "Hatch"
    
    def test_suv_classification(self):
        """SUVs devem ser classificados corretamente"""
        assert classifier.classify("Chevrolet Tracker", "Chevrolet Tracker", 2021) == "SUV"
        assert classifier.classify("Hyundai Creta", "Hyundai Creta", 2020) == "SUV"
        assert classifier.classify("Nissan Kicks", "Nissan Kicks", 2021) == "SUV"
    
    def test_sedan_classification(self):
        """Sedans devem ser classificados corretamente"""
        assert classifier.classify("Toyota Corolla", "Toyota Corolla", 2020) == "Sedan"
        assert classifier.classify("Honda Civic", "Honda Civic", 2021) == "Sedan"
        assert classifier.classify("Volkswagen Virtus", "Volkswagen Virtus", 2022) == "Sedan"
    
    def test_hatch_classification(self):
        """Hatchbacks devem ser classificados corretamente"""
        assert classifier.classify("Chevrolet Onix", "Chevrolet Onix", 2020) == "Hatch"
        assert classifier.classify("Volkswagen Gol", "Volkswagen Gol", 2019) == "Hatch"
        assert classifier.classify("Fiat Uno", "Fiat Uno", 2018) == "Hatch"
    
    def test_pickup_classification(self):
        """Pickups devem ser classificadas corretamente"""
        assert classifier.classify("Toyota Hilux", "Toyota Hilux", 2021) == "Pickup"
        assert classifier.classify("Ford Ranger", "Ford Ranger", 2020) == "Pickup"
        assert classifier.classify("Chevrolet S10", "Chevrolet S10", 2019) == "Pickup"
    
    def test_classification_without_year(self):
        """Classificação deve funcionar sem ano (exceto casos especiais)"""
        # Casos normais funcionam sem ano
        assert classifier.classify("Chevrolet Onix", "Chevrolet Onix") == "Hatch"
        assert classifier.classify("Toyota Corolla", "Toyota Corolla") == "Sedan"
        
        # Focus sem ano vai para Hatch (padrão atual)
        assert classifier.classify("Ford Focus", "Ford Focus") == "Hatch"
    
    def test_case_insensitive(self):
        """Classificação deve ser case-insensitive"""
        assert classifier.classify("FORD FOCUS", "FORD FOCUS", 2009) == "Sedan"
        assert classifier.classify("ford focus", "ford focus", 2009) == "Sedan"
        assert classifier.classify("Ford Focus", "Ford Focus", 2009) == "Sedan"


class TestCarClassifierFeatures:
    """Testes para inferência de características"""
    
    def test_safety_items_by_year(self):
        """Itens de segurança devem variar por ano"""
        # 2024 tem mais itens
        items_2024 = classifier.get_typical_safety_items(2024, "SUV")
        assert '6_airbags' in items_2024
        assert 'ISOFIX' in items_2024
        
        # 2010 tem menos itens
        items_2010 = classifier.get_typical_safety_items(2010, "Hatch")
        assert 'ABS' in items_2010
        assert '6_airbags' not in items_2010
    
    def test_comfort_items_by_category(self):
        """Itens de conforto devem variar por categoria"""
        # SUV tem mais conforto
        items_suv = classifier.get_typical_comfort_items("SUV", 2020)
        assert 'sensor_estacionamento' in items_suv
        
        # Compacto tem menos
        items_compacto = classifier.get_typical_comfort_items("Compacto", 2020)
        assert 'ar_condicionado' in items_compacto
        assert 'sensor_estacionamento' not in items_compacto
    
    def test_premium_version_detection(self):
        """Versões premium devem ser detectadas"""
        assert classifier.is_premium_version("Chevrolet Tracker Premier") == True
        assert classifier.is_premium_version("Honda Civic LTZ") == True
        assert classifier.is_premium_version("Volkswagen Polo Highline") == True
        assert classifier.is_premium_version("Chevrolet Onix LT") == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
