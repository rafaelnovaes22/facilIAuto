"""
Testes de Integração da API (TDD)
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
import json
import tempfile
import shutil

# Setup path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


@pytest.fixture
def temp_data_for_api(sample_dealership, sample_car):
    """Criar dados temporários para a API"""
    temp_dir = tempfile.mkdtemp()
    
    # Criar dealerships.json
    dealerships_data = [sample_dealership.model_dump()]
    with open(os.path.join(temp_dir, "dealerships.json"), 'w', encoding='utf-8') as f:
        json.dump(dealerships_data, f, default=str)
    
    # Criar estoque com múltiplos carros
    cars_data = []
    for i in range(5):
        car_dict = sample_car.model_dump()
        car_dict['id'] = f"test_car_{i:03d}"
        car_dict['preco'] = 50000 + (i * 10000)
        car_dict['nome'] = f"Test Car {i}"
        cars_data.append(car_dict)
    
    with open(os.path.join(temp_dir, f"{sample_dealership.id}_estoque.json"), 'w', encoding='utf-8') as f:
        json.dump(cars_data, f, default=str)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def client(temp_data_for_api, monkeypatch):
    """Cliente de teste da API"""
    # Configurar data_dir antes de importar a API
    monkeypatch.setenv("DATA_DIR", temp_data_for_api)
    
    # Importar após configurar
    from api.main import app, engine
    engine.data_dir = temp_data_for_api
    engine.load_dealerships()
    engine.load_all_cars()
    
    return TestClient(app)


class TestAPIHealth:
    """Testes de health check"""
    
    def test_root_endpoint(self, client):
        """Teste: endpoint raiz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data
    
    def test_health_check(self, client):
        """Teste: health check detalhado"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "dealerships" in data
        assert "cars" in data


class TestDealershipsAPI:
    """Testes dos endpoints de concessionárias"""
    
    def test_list_dealerships(self, client):
        """Teste: listar concessionárias"""
        response = client.get("/dealerships")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_list_dealerships_active_only(self, client):
        """Teste: listar apenas ativas"""
        response = client.get("/dealerships?active_only=true")
        assert response.status_code == 200
        data = response.json()
        for dealer in data:
            assert dealer["active"] is True
    
    def test_get_dealership_by_id(self, client):
        """Teste: obter concessionária específica"""
        response = client.get("/dealerships/test_dealer")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_dealer"
        assert "name" in data
    
    def test_get_dealership_not_found(self, client):
        """Teste: concessionária não encontrada"""
        response = client.get("/dealerships/nonexistent")
        assert response.status_code == 404


class TestCarsAPI:
    """Testes dos endpoints de carros"""
    
    def test_list_cars(self, client):
        """Teste: listar carros"""
        response = client.get("/cars")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_list_cars_with_filters(self, client):
        """Teste: listar com filtros"""
        response = client.get("/cars?preco_min=50000&preco_max=70000")
        assert response.status_code == 200
        data = response.json()
        
        for car in data:
            assert 50000 <= car["preco"] <= 70000
    
    def test_list_cars_by_dealership(self, client):
        """Teste: filtrar por concessionária"""
        response = client.get("/cars?dealership_id=test_dealer")
        assert response.status_code == 200
        data = response.json()
        
        for car in data:
            assert car["dealership_id"] == "test_dealer"
    
    def test_list_cars_limit(self, client):
        """Teste: limitar resultados"""
        response = client.get("/cars?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
    
    def test_get_car_by_id(self, client):
        """Teste: obter carro específico"""
        response = client.get("/cars/test_car_000")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_car_000"
    
    def test_get_car_not_found(self, client):
        """Teste: carro não encontrado"""
        response = client.get("/cars/nonexistent")
        assert response.status_code == 404


class TestRecommendationAPI:
    """Testes do endpoint de recomendação"""
    
    def test_recommend_basic(self, client):
        """Teste: recomendação básica"""
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia"
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        assert "total_recommendations" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
    
    def test_recommend_with_full_profile(self, client):
        """Teste: recomendação com perfil completo"""
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "city": "São Paulo",
            "state": "SP",
            "uso_principal": "familia",
            "tamanho_familia": 4,
            "necessita_espaco": True,
            "tem_criancas": True,
            "prioridades": {
                "economia": 4,
                "espaco": 5,
                "performance": 2,
                "conforto": 4,
                "seguranca": 5
            },
            "tipos_preferidos": ["SUV", "Sedan"]
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Validar estrutura da resposta
        assert "profile_summary" in data
        assert "recommendations" in data
        
        # Validar cada recomendação
        for rec in data["recommendations"]:
            assert "car" in rec
            assert "match_score" in rec
            assert "match_percentage" in rec
            assert "justification" in rec
            assert 0.0 <= rec["match_score"] <= 1.0
    
    def test_recommend_invalid_budget(self, client):
        """Teste: orçamento inválido"""
        profile = {
            "orcamento_min": 100000,
            "orcamento_max": 50000,  # Menor que o mínimo
            "uso_principal": "familia"
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 400
    
    def test_recommend_missing_fields(self, client):
        """Teste: campos obrigatórios faltando"""
        profile = {
            "orcamento_min": 50000
            # Faltando orcamento_max e uso_principal
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 422  # Validation error
    
    def test_recommend_response_structure(self, client):
        """Teste: estrutura da resposta de recomendação"""
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "trabalho"
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Validar estrutura completa
        assert "total_recommendations" in data
        assert "profile_summary" in data
        assert "recommendations" in data
        
        # Profile summary
        summary = data["profile_summary"]
        assert "budget_range" in summary
        assert "usage" in summary
        assert "location" in summary
        
        # Recommendations
        if data["recommendations"]:
            rec = data["recommendations"][0]
            assert "car" in rec
            assert "match_score" in rec
            assert "match_percentage" in rec
            assert "justification" in rec
            
            # Car details
            car = rec["car"]
            assert "id" in car
            assert "nome" in car
            assert "preco" in car
            assert "dealership" in car
            
            # Dealership details
            dealer = car["dealership"]
            assert "id" in dealer
            assert "name" in dealer
            assert "city" in dealer


class TestStatsAPI:
    """Testes do endpoint de estatísticas"""
    
    def test_get_stats(self, client):
        """Teste: obter estatísticas"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "platform" in data
        assert "dealerships_by_state" in data
        assert "cars_by_category" in data
        
        platform = data["platform"]
        assert "total_dealerships" in platform
        assert "active_dealerships" in platform
        assert "total_cars" in platform
        assert "available_cars" in platform
    
    def test_list_categories(self, client):
        """Teste: listar categorias"""
        response = client.get("/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_brands(self, client):
        """Teste: listar marcas"""
        response = client.get("/brands")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

