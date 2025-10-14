"""
🧪 Tech Lead: Testes para Filtros Avançados - FASE 1

Testa os novos filtros implementados:
- Ano mínimo
- Quilometragem máxima
- Must-haves (itens obrigatórios)
- Raio geográfico

Autor: Tech Lead
Data: Outubro 2024
"""

import pytest
from models.car import Car
from models.user_profile import UserProfile
from services.unified_recommendation_engine import UnifiedRecommendationEngine
from utils.geo_distance import (
    haversine_distance, 
    calculate_distance, 
    is_within_radius,
    get_city_coordinates
)


class TestGeoDistance:
    """Testes para cálculo de distância geográfica"""
    
    def test_haversine_sao_paulo_rio(self):
        """Testar distância São Paulo -> Rio de Janeiro"""
        # São Paulo
        lat1, lon1 = -23.5505, -46.6333
        # Rio de Janeiro
        lat2, lon2 = -22.9068, -43.1729
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        # Distância real é ~357 km
        assert 350 <= distance <= 365, f"Distância incorreta: {distance} km"
    
    def test_haversine_contagem_bh(self):
        """Testar distância Contagem -> Belo Horizonte"""
        # Contagem
        lat1, lon1 = -19.9320, -44.0540
        # Belo Horizonte
        lat2, lon2 = -19.9167, -43.9345
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        # Distância real é ~13 km
        assert 10 <= distance <= 15, f"Distância incorreta: {distance} km"
    
    def test_calculate_distance_valid(self):
        """Testar cálculo com coordenadas válidas"""
        sp = (-23.5505, -46.6333)
        rj = (-22.9068, -43.1729)
        
        distance = calculate_distance(sp, rj)
        
        assert distance is not None
        assert 350 <= distance <= 365
    
    def test_calculate_distance_invalid(self):
        """Testar cálculo com coordenadas inválidas"""
        assert calculate_distance(None, (-22.9, -43.1)) is None
        assert calculate_distance((-23.5, -46.6), None) is None
        assert calculate_distance((200, -46.6), (-22.9, -43.1)) is None  # lat inválida
    
    def test_is_within_radius_true(self):
        """Testar se está dentro do raio"""
        contagem = (-19.9320, -44.0540)
        bh = (-19.9167, -43.9345)
        
        # ~13 km, dentro de 30 km
        assert is_within_radius(contagem, bh, 30) is True
    
    def test_is_within_radius_false(self):
        """Testar se está fora do raio"""
        sp = (-23.5505, -46.6333)
        rj = (-22.9068, -43.1729)
        
        # ~357 km, fora de 100 km
        assert is_within_radius(sp, rj, 100) is False
    
    def test_get_city_coordinates(self):
        """Testar obtenção de coordenadas de cidades"""
        sp_coords = get_city_coordinates("São Paulo")
        assert sp_coords == (-23.5505, -46.6333)
        
        # Case insensitive
        rj_coords = get_city_coordinates("rio de janeiro")
        assert rj_coords is not None
        
        # Cidade não encontrada
        assert get_city_coordinates("Cidade Inexistente") is None


class TestFilterByYear:
    """Testes para filtro de ano mínimo"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.cars = [
            Car(
                id="car_2024", dealership_id="d1", nome="Carro Novo", marca="Fiat",
                modelo="Cronos", ano=2024, preco=90000, quilometragem=0,
                combustivel="Flex", categoria="Sedan",
                dealership_name="Test", dealership_city="SP", 
                dealership_state="SP", dealership_phone="111", dealership_whatsapp="111"
            ),
            Car(
                id="car_2020", dealership_id="d1", nome="Carro Semi-Novo", marca="Fiat",
                modelo="Cronos", ano=2020, preco=70000, quilometragem=30000,
                combustivel="Flex", categoria="Sedan",
                dealership_name="Test", dealership_city="SP", 
                dealership_state="SP", dealership_phone="111", dealership_whatsapp="111"
            ),
            Car(
                id="car_2015", dealership_id="d1", nome="Carro Usado", marca="Fiat",
                modelo="Cronos", ano=2015, preco=50000, quilometragem=80000,
                combustivel="Flex", categoria="Sedan",
                dealership_name="Test", dealership_city="SP", 
                dealership_state="SP", dealership_phone="111", dealership_whatsapp="111"
            ),
        ]
    
    def test_filter_by_year_2020(self):
        """Filtrar carros >= 2020"""
        from services.unified_recommendation_engine import UnifiedRecommendationEngine
        engine = UnifiedRecommendationEngine.__new__(UnifiedRecommendationEngine)
        
        filtered = engine.filter_by_year(self.cars, 2020)
        
        assert len(filtered) == 2
        assert all(car.ano >= 2020 for car in filtered)
    
    def test_filter_by_year_none(self):
        """Sem filtro de ano (None)"""
        from services.unified_recommendation_engine import UnifiedRecommendationEngine
        engine = UnifiedRecommendationEngine.__new__(UnifiedRecommendationEngine)
        
        filtered = engine.filter_by_year(self.cars, None)
        
        assert len(filtered) == 3


class TestFilterByKm:
    """Testes para filtro de quilometragem máxima"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.cars = [
            Car(
                id="car_low_km", dealership_id="d1", nome="Baixa KM", marca="Fiat",
                modelo="Cronos", ano=2023, preco=85000, quilometragem=10000,
                combustivel="Flex", categoria="Sedan",
                dealership_name="Test", dealership_city="SP", 
                dealership_state="SP", dealership_phone="111", dealership_whatsapp="111"
            ),
            Car(
                id="car_medium_km", dealership_id="d1", nome="Média KM", marca="Fiat",
                modelo="Cronos", ano=2021, preco=75000, quilometragem=50000,
                combustivel="Flex", categoria="Sedan",
                dealership_name="Test", dealership_city="SP", 
                dealership_state="SP", dealership_phone="111", dealership_whatsapp="111"
            ),
            Car(
                id="car_high_km", dealership_id="d1", nome="Alta KM", marca="Fiat",
                modelo="Cronos", ano=2018, preco=60000, quilometragem=120000,
                combustivel="Flex", categoria="Sedan",
                dealership_name="Test", dealership_city="SP", 
                dealership_state="SP", dealership_phone="111", dealership_whatsapp="111"
            ),
        ]
    
    def test_filter_by_km_80000(self):
        """Filtrar carros <= 80000 km"""
        from services.unified_recommendation_engine import UnifiedRecommendationEngine
        engine = UnifiedRecommendationEngine.__new__(UnifiedRecommendationEngine)
        
        filtered = engine.filter_by_km(self.cars, 80000)
        
        assert len(filtered) == 2
        assert all(car.quilometragem <= 80000 for car in filtered)
    
    def test_filter_by_km_none(self):
        """Sem filtro de km (None)"""
        from services.unified_recommendation_engine import UnifiedRecommendationEngine
        engine = UnifiedRecommendationEngine.__new__(UnifiedRecommendationEngine)
        
        filtered = engine.filter_by_km(self.cars, None)
        
        assert len(filtered) == 3


class TestFilterByMustHaves:
    """Testes para filtro de must-haves (itens obrigatórios)"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.cars = [
            Car(
                id="car_full_safety", dealership_id="d1", nome="Segurança Completa", 
                marca="Fiat", modelo="Cronos", ano=2023, preco=90000, quilometragem=10000,
                combustivel="Flex", categoria="Sedan",
                itens_seguranca=["ISOFIX", "6_airbags", "controle_estabilidade", "ABS", "camera_re"],
                itens_conforto=["ar_condicionado", "direcao_eletrica"],
                dealership_name="Test", dealership_city="SP", 
                dealership_state="SP", dealership_phone="111", dealership_whatsapp="111"
            ),
            Car(
                id="car_partial_safety", dealership_id="d1", nome="Segurança Parcial", 
                marca="Fiat", modelo="Cronos", ano=2021, preco=75000, quilometragem=30000,
                combustivel="Flex", categoria="Sedan",
                itens_seguranca=["ABS", "camera_re"],
                itens_conforto=["ar_condicionado"],
                dealership_name="Test", dealership_city="SP", 
                dealership_state="SP", dealership_phone="111", dealership_whatsapp="111"
            ),
            Car(
                id="car_basic", dealership_id="d1", nome="Básico", 
                marca="Fiat", modelo="Cronos", ano=2018, preco=60000, quilometragem=80000,
                combustivel="Flex", categoria="Sedan",
                itens_seguranca=[],
                itens_conforto=[],
                dealership_name="Test", dealership_city="SP", 
                dealership_state="SP", dealership_phone="111", dealership_whatsapp="111"
            ),
        ]
    
    def test_filter_must_haves_isofix_airbags(self):
        """Filtrar carros com ISOFIX e 6 airbags"""
        from services.unified_recommendation_engine import UnifiedRecommendationEngine
        engine = UnifiedRecommendationEngine.__new__(UnifiedRecommendationEngine)
        
        must_haves = ["ISOFIX", "6_airbags"]
        filtered = engine.filter_by_must_haves(self.cars, must_haves)
        
        assert len(filtered) == 1
        assert filtered[0].id == "car_full_safety"
    
    def test_filter_must_haves_camera(self):
        """Filtrar carros com câmera de ré"""
        from services.unified_recommendation_engine import UnifiedRecommendationEngine
        engine = UnifiedRecommendationEngine.__new__(UnifiedRecommendationEngine)
        
        must_haves = ["camera_re"]
        filtered = engine.filter_by_must_haves(self.cars, must_haves)
        
        assert len(filtered) == 2
        assert all("camera_re" in car.itens_seguranca for car in filtered)
    
    def test_filter_must_haves_none(self):
        """Sem must-haves (lista vazia)"""
        from services.unified_recommendation_engine import UnifiedRecommendationEngine
        engine = UnifiedRecommendationEngine.__new__(UnifiedRecommendationEngine)
        
        filtered = engine.filter_by_must_haves(self.cars, [])
        
        assert len(filtered) == 3


class TestUserProfileFase1:
    """Testes para validar novo UserProfile com filtros FASE 1"""
    
    def test_user_profile_with_all_filters(self):
        """Criar perfil com todos os filtros FASE 1"""
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            city="São Paulo",
            state="SP",
            uso_principal="familia",
            ano_minimo=2020,
            km_maxima=50000,
            must_haves=["ISOFIX", "6_airbags"],
            raio_maximo_km=30
        )
        
        assert profile.ano_minimo == 2020
        assert profile.km_maxima == 50000
        assert "ISOFIX" in profile.must_haves
        assert profile.raio_maximo_km == 30
    
    def test_user_profile_optional_filters(self):
        """Filtros FASE 1 são opcionais"""
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="trabalho"
        )
        
        assert profile.ano_minimo is None
        assert profile.km_maxima is None
        assert profile.must_haves == []
        assert profile.raio_maximo_km is None


if __name__ == "__main__":
    print("🧪 Tech Lead: Executando testes FASE 1")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "--tb=short"])

