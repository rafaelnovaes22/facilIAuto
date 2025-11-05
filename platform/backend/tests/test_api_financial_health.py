"""
Test API endpoint response format for financial health indicator
Requirements: 1.1-1.5, 2.1-2.5
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Setup path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from api.main import app


@pytest.fixture
def client():
    """Cliente de teste da API"""
    return TestClient(app)


class TestFinancialHealthAPI:
    """Testes do endpoint /recommend com financial_health"""
    
    def test_recommend_includes_financial_health(self, client):
        """
        Teste: Endpoint /recommend inclui financial_health quando disponível
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "city": "São Paulo",
            "state": "SP",
            "prioridades": {
                "economia": 4,
                "espaco": 5,
                "performance": 2,
                "conforto": 4,
                "seguranca": 5
            },
            "financial_capacity": {
                "monthly_income_range": "8000-12000",
                "max_monthly_tco": 3000,
                "is_disclosed": True
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estrutura da resposta
        assert "recommendations" in data
        
        # Se houver recomendações, verificar financial_health
        if data["recommendations"]:
            rec = data["recommendations"][0]
            
            # Verificar campos obrigatórios
            assert "car" in rec
            assert "match_score" in rec
            assert "match_percentage" in rec
            assert "justification" in rec
            assert "tco_breakdown" in rec
            assert "fits_budget" in rec
            assert "budget_percentage" in rec
            
            # Verificar financial_health (pode ser None se não houver TCO)
            assert "financial_health" in rec
            
            # Se financial_health existe, verificar estrutura
            if rec["financial_health"]:
                fh = rec["financial_health"]
                assert "status" in fh
                assert "percentage" in fh
                assert "color" in fh
                assert "message" in fh
                
                # Verificar valores válidos
                assert fh["status"] in ["healthy", "caution", "high_commitment"]
                assert fh["color"] in ["green", "yellow", "red"]
                assert isinstance(fh["percentage"], (int, float))
                assert fh["percentage"] >= 0
    
    def test_recommend_without_financial_capacity(self, client):
        """
        Teste: Endpoint /recommend funciona sem financial_capacity
        Requirements: 1.1, 2.1
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "trabalho",
            "prioridades": {
                "economia": 5,
                "espaco": 3,
                "performance": 2,
                "conforto": 3,
                "seguranca": 4
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que funciona sem financial_capacity
        assert "recommendations" in data
        
        # Se houver recomendações, financial_health deve ser None
        if data["recommendations"]:
            rec = data["recommendations"][0]
            assert "financial_health" in rec
            # Sem financial_capacity, financial_health deve ser None
            assert rec["financial_health"] is None
            assert rec["fits_budget"] is None
    
    def test_recommend_budget_percentage_calculation(self, client):
        """
        Teste: budget_percentage usa midpoint da renda
        Requirements: 1.4, 2.1, 2.2
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "familia",
            "city": "São Paulo",
            "state": "SP",
            "prioridades": {
                "economia": 4,
                "espaco": 5,
                "performance": 2,
                "conforto": 4,
                "seguranca": 5
            },
            "financial_capacity": {
                "monthly_income_range": "8000-12000",  # Midpoint: 10000
                "max_monthly_tco": 3000,
                "is_disclosed": True
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Se houver recomendações com TCO
        if data["recommendations"]:
            rec = data["recommendations"][0]
            
            if rec["tco_breakdown"] and rec["budget_percentage"]:
                # Verificar que budget_percentage está calculado
                assert isinstance(rec["budget_percentage"], (int, float))
                assert rec["budget_percentage"] > 0
                
                # Verificar que está usando midpoint (10000)
                # budget_percentage = (tco_monthly / 10000) * 100
                tco_monthly = rec["tco_breakdown"]["total_monthly"]
                expected_percentage = (tco_monthly / 10000) * 100
                
                # Permitir pequena diferença por arredondamento
                assert abs(rec["budget_percentage"] - expected_percentage) < 0.5
    
    def test_recommend_fits_budget_validation(self, client):
        """
        Teste: fits_budget usa validação correta
        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
        """
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 100000,
            "uso_principal": "trabalho",
            "city": "São Paulo",
            "state": "SP",
            "prioridades": {
                "economia": 5,
                "espaco": 3,
                "performance": 2,
                "conforto": 3,
                "seguranca": 4
            },
            "financial_capacity": {
                "monthly_income_range": "8000-12000",
                "max_monthly_tco": 2000,  # Limite baixo para testar
                "is_disclosed": True
            }
        }
        
        response = client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Se houver recomendações
        if data["recommendations"]:
            for rec in data["recommendations"]:
                if rec["tco_breakdown"] and rec["fits_budget"] is not None:
                    tco_monthly = rec["tco_breakdown"]["total_monthly"]
                    max_tco = 2000
                    
                    # Verificar lógica correta
                    if tco_monthly <= max_tco:
                        assert rec["fits_budget"] is True
                    else:
                        assert rec["fits_budget"] is False
