"""
Testes para filtro de ano mínimo
Garante que apenas carros do ano especificado ou mais recentes sejam retornados
"""

import pytest
from models.user_profile import UserProfile
from models.car import Car
from services.unified_recommendation_engine import UnifiedRecommendationEngine


def test_filter_by_year_basic():
    """Teste básico: filtrar carros por ano mínimo"""
    engine = UnifiedRecommendationEngine()
    
    # Criar carros de teste
    cars = [
        Car(
            id="1", dealership_id="test", nome="Carro 2020", marca="Test", modelo="Model",
            ano=2020, preco=50000, quilometragem=30000, combustivel="Flex",
            categoria="Sedan", score_familia=0.8, score_economia=0.7,
            score_performance=0.6, score_conforto=0.7, score_seguranca=0.8,
            imagens=[], disponivel=True, destaque=False,
            dealership_name="Test", dealership_city="São Paulo",
            dealership_state="SP", dealership_phone="11999999999",
            dealership_whatsapp="11999999999"
        ),
        Car(
            id="2", dealership_id="test", nome="Carro 2018", marca="Test", modelo="Model",
            ano=2018, preco=40000, quilometragem=50000, combustivel="Flex",
            categoria="Sedan", score_familia=0.8, score_economia=0.7,
            score_performance=0.6, score_conforto=0.7, score_seguranca=0.8,
            imagens=[], disponivel=True, destaque=False,
            dealership_name="Test", dealership_city="São Paulo",
            dealership_state="SP", dealership_phone="11999999999",
            dealership_whatsapp="11999999999"
        ),
        Car(
            id="3", dealership_id="test", nome="Carro 2015", marca="Test", modelo="Model",
            ano=2015, preco=30000, quilometragem=80000, combustivel="Flex",
            categoria="Sedan", score_familia=0.8, score_economia=0.7,
            score_performance=0.6, score_conforto=0.7, score_seguranca=0.8,
            imagens=[], disponivel=True, destaque=False,
            dealership_name="Test", dealership_city="São Paulo",
            dealership_state="SP", dealership_phone="11999999999",
            dealership_whatsapp="11999999999"
        ),
    ]
    
    # Filtrar por ano >= 2018
    filtered = engine.filter_by_year(cars, 2018)
    
    assert len(filtered) == 2
    assert all(car.ano >= 2018 for car in filtered)
    assert filtered[0].id == "1"
    assert filtered[1].id == "2"


def test_filter_by_year_none():
    """Teste: sem filtro de ano (None) retorna todos os carros"""
    engine = UnifiedRecommendationEngine()
    
    cars = [
        Car(
            id="1", dealership_id="test", nome="Carro 2020", marca="Test", modelo="Model",
            ano=2020, preco=50000, quilometragem=30000, combustivel="Flex",
            categoria="Sedan", score_familia=0.8, score_economia=0.7,
            score_performance=0.6, score_conforto=0.7, score_seguranca=0.8,
            imagens=[], disponivel=True, destaque=False,
            dealership_name="Test", dealership_city="São Paulo",
            dealership_state="SP", dealership_phone="11999999999",
            dealership_whatsapp="11999999999"
        ),
        Car(
            id="2", dealership_id="test", nome="Carro 2010", marca="Test", modelo="Model",
            ano=2010, preco=20000, quilometragem=100000, combustivel="Flex",
            categoria="Sedan", score_familia=0.8, score_economia=0.7,
            score_performance=0.6, score_conforto=0.7, score_seguranca=0.8,
            imagens=[], disponivel=True, destaque=False,
            dealership_name="Test", dealership_city="São Paulo",
            dealership_state="SP", dealership_phone="11999999999",
            dealership_whatsapp="11999999999"
        ),
    ]
    
    # Sem filtro de ano
    filtered = engine.filter_by_year(cars, None)
    
    assert len(filtered) == 2


def test_filter_by_year_no_matches():
    """Teste: ano muito recente não retorna nenhum carro"""
    engine = UnifiedRecommendationEngine()
    
    cars = [
        Car(
            id="1", dealership_id="test", nome="Carro 2015", marca="Test", modelo="Model",
            ano=2015, preco=30000, quilometragem=50000, combustivel="Flex",
            categoria="Sedan", score_familia=0.8, score_economia=0.7,
            score_performance=0.6, score_conforto=0.7, score_seguranca=0.8,
            imagens=[], disponivel=True, destaque=False,
            dealership_name="Test", dealership_city="São Paulo",
            dealership_state="SP", dealership_phone="11999999999",
            dealership_whatsapp="11999999999"
        ),
    ]
    
    # Filtrar por ano >= 2023 (nenhum carro atende)
    filtered = engine.filter_by_year(cars, 2023)
    
    assert len(filtered) == 0


def test_recommend_with_year_filter():
    """Teste integrado: recomendação com filtro de ano"""
    engine = UnifiedRecommendationEngine()
    
    # Criar perfil com ano mínimo
    profile = UserProfile(
        orcamento_min=20000,
        orcamento_max=60000,
        uso_principal="familia",
        tamanho_familia=4,
        tem_criancas=True,
        prioridades={
            "economia": 4,
            "espaco": 5,
            "performance": 2,
            "conforto": 4,
            "seguranca": 5
        },
        ano_minimo=2018  # Filtro de ano
    )
    
    # Executar recomendação
    recommendations = engine.recommend(profile, limit=10)
    
    # Verificar que todos os carros recomendados são >= 2018
    for rec in recommendations:
        assert rec['car'].ano >= 2018, f"Carro {rec['car'].nome} tem ano {rec['car'].ano} < 2018"


def test_recommend_without_year_filter():
    """Teste: recomendação sem filtro de ano retorna carros de qualquer ano"""
    engine = UnifiedRecommendationEngine()
    
    # Criar perfil SEM ano mínimo
    profile = UserProfile(
        orcamento_min=20000,
        orcamento_max=60000,
        uso_principal="familia",
        tamanho_familia=4,
        prioridades={
            "economia": 4,
            "espaco": 5,
            "performance": 2,
            "conforto": 4,
            "seguranca": 5
        }
        # ano_minimo não especificado
    )
    
    # Executar recomendação
    recommendations = engine.recommend(profile, limit=10)
    
    # Deve retornar carros (sem restrição de ano)
    assert len(recommendations) > 0
