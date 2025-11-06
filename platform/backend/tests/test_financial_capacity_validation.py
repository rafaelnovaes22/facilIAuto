"""
Testes de Validação de Financial Capacity (Requirements 6.1-6.5)
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


class TestFinancialCapacityValidation:
    """Testes de validação de financial_capacity (Requirements 6.1-6.5)"""
    
    def test_recommend_with_valid_financial_capacity(self, client):
        """
        Teste: Recomendação com financial_capacity válido
        Requirement 6.1: Backend deve validar campos obrigatórios
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "financial_capacity": {
                "monthly_income_range": "5000-8000",
                "max_monthly_tco": 1950.0,
                "is_disclosed": True
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
    
    def test_recommend_with_invalid_income_range(self, client):
        """
        Teste: Rejeitar monthly_income_range inválido
        Requirement 6.2: Validar que monthly_income_range está em lista válida
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "financial_capacity": {
                "monthly_income_range": "invalid-range",
                "max_monthly_tco": 2000.0,
                "is_disclosed": True
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 400
        assert "monthly_income_range inválido" in response.json()["detail"]
        assert "0-3000" in response.json()["detail"]
        assert "3000-5000" in response.json()["detail"]
    
    def test_recommend_with_negative_max_tco(self, client):
        """
        Teste: Rejeitar max_monthly_tco negativo
        Requirement 6.3: Validar que max_monthly_tco é positivo
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "financial_capacity": {
                "monthly_income_range": "5000-8000",
                "max_monthly_tco": -1000.0,
                "is_disclosed": True
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 400
        assert "max_monthly_tco deve ser maior ou igual a zero" in response.json()["detail"]
    
    def test_recommend_with_inconsistent_is_disclosed(self, client):
        """
        Teste: Rejeitar is_disclosed=true sem monthly_income_range
        Requirement 6.4: Validar consistência entre is_disclosed e monthly_income_range
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "financial_capacity": {
                "monthly_income_range": None,
                "max_monthly_tco": 2000.0,
                "is_disclosed": True
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 400
        assert "monthly_income_range é obrigatório quando is_disclosed=true" in response.json()["detail"]
    
    def test_recommend_without_financial_capacity(self, client):
        """
        Teste: Recomendação sem financial_capacity (opcional)
        Requirement 6.5: financial_capacity é opcional
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia"
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
    
    def test_recommend_with_is_disclosed_false(self, client):
        """
        Teste: Aceitar is_disclosed=false sem monthly_income_range
        Requirement 6.4: Consistência só é necessária quando is_disclosed=true
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "financial_capacity": {
                "monthly_income_range": None,
                "max_monthly_tco": None,
                "is_disclosed": False
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
    
    def test_all_valid_income_ranges(self, client):
        """
        Teste: Validar todas as faixas salariais válidas
        Requirement 6.2: Todas as faixas definidas devem ser aceitas
        """
        valid_ranges = ["0-3000", "3000-5000", "5000-8000", "8000-12000", "12000+"]
        
        for income_range in valid_ranges:
            profile = {
                "orcamento_min": 50000,
                "orcamento_max": 100000,
                "uso_principal": "familia",
                "financial_capacity": {
                    "monthly_income_range": income_range,
                    "max_monthly_tco": 1500.0,
                    "is_disclosed": True
                }
            }
            
            response = client.post("/recommend", json=profile)
            assert response.status_code == 200, f"Falhou para faixa: {income_range}"
    
    def test_recommend_with_zero_max_tco(self, client):
        """
        Teste: Aceitar max_monthly_tco = 0 (edge case válido)
        Requirement 6.3: max_monthly_tco >= 0 (zero é válido)
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "financial_capacity": {
                "monthly_income_range": "0-3000",
                "max_monthly_tco": 0.0,
                "is_disclosed": True
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
    
    def test_recommend_with_null_financial_capacity(self, client):
        """
        Teste: Aceitar financial_capacity = null explicitamente
        Requirement 6.5: financial_capacity é opcional
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "financial_capacity": None
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
    
    def test_validation_error_messages_are_descriptive(self, client):
        """
        Teste: Mensagens de erro são descritivas
        Requirement 6.5: Retornar mensagens descritivas para erros
        """
        # Teste 1: Income range inválido
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "financial_capacity": {
                "monthly_income_range": "999-999",
                "max_monthly_tco": 1500.0,
                "is_disclosed": True
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "inválido" in error_detail.lower()
        assert "0-3000" in error_detail  # Lista opções válidas
        
        # Teste 2: TCO negativo
        profile["financial_capacity"]["monthly_income_range"] = "5000-8000"
        profile["financial_capacity"]["max_monthly_tco"] = -500.0
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "maior ou igual a zero" in error_detail.lower()
        
        # Teste 3: Inconsistência is_disclosed
        profile["financial_capacity"]["monthly_income_range"] = None
        profile["financial_capacity"]["max_monthly_tco"] = 1500.0
        profile["financial_capacity"]["is_disclosed"] = True
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "obrigatório" in error_detail.lower()
        assert "is_disclosed=true" in error_detail.lower()


class TestFinancialCapacityEdgeCases:
    """Testes de casos extremos e edge cases"""
    
    def test_recommend_with_very_high_max_tco(self, client):
        """
        Teste: Aceitar valores muito altos de max_monthly_tco
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "financial_capacity": {
                "monthly_income_range": "12000+",
                "max_monthly_tco": 50000.0,  # Valor muito alto mas válido
                "is_disclosed": True
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
    
    def test_recommend_with_partial_financial_capacity(self, client):
        """
        Teste: Aceitar financial_capacity com apenas alguns campos
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "financial_capacity": {
                "is_disclosed": False
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
    
    def test_case_sensitive_income_range(self, client):
        """
        Teste: Validar que income_range é case-sensitive e rejeita variações
        """
        # Testar valor válido
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "financial_capacity": {
                "monthly_income_range": "5000-8000",  # correto
                "max_monthly_tco": 1950.0,
                "is_disclosed": True
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        
        # Testar com espaços extras (deve falhar)
        profile["financial_capacity"]["monthly_income_range"] = " 5000-8000 "
        response = client.post("/recommend", json=profile)
        assert response.status_code == 400
        
        # Testar com formato diferente (deve falhar)
        profile["financial_capacity"]["monthly_income_range"] = "5000 - 8000"
        response = client.post("/recommend", json=profile)
        assert response.status_code == 400
