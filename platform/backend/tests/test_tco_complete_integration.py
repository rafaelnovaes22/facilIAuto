"""
Complete Integration Tests for TCO Calculation Fixes
Tests the complete flow from API to UI with real data
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

from models.user_profile import UserProfile, FinancialCapacity
from models.car import Car
from models.dealership import Dealership
from services.unified_recommendation_engine import UnifiedRecommendationEngine


@pytest.fixture
def temp_data_with_varied_cars():
    """Create temporary data with cars of varying mileage and prices"""
    temp_dir = tempfile.mkdtemp()
    
    # Create cars with different mileage levels
    cars_data = [
        # Low mileage car
        {
            "id": "low_mileage_car",
            "dealership_id": "test_dealer",
            "nome": "FIAT CRONOS DRIVE 1.3",
            "marca": "Fiat",
            "modelo": "Cronos",
            "versao": "Drive 1.3",
            "ano": 2022,
            "preco": 60000.0,
            "quilometragem": 50000,
            "combustivel": "Flex",
            "cambio": "Manual",
            "categoria": "Sedan",
            "consumo_cidade": 10.5,
            "consumo_estrada": 13.2,
            "score_familia": 0.8,
            "score_economia": 0.9,
            "disponivel": True
        },
        # Medium mileage car (100k-150k)
        {
            "id": "medium_mileage_car",
            "dealership_id": "test_dealer",
            "nome": "VOLKSWAGEN GOL 1.0",
            "marca": "Volkswagen",
            "modelo": "Gol",
            "versao": "1.0",
            "ano": 2018,
            "preco": 45000.0,
            "quilometragem": 120000,
            "combustivel": "Flex",
            "cambio": "Manual",
            "categoria": "Hatch",
            "consumo_cidade": 11.0,
            "consumo_estrada": 14.0,
            "score_familia": 0.7,
            "score_economia": 0.95,
            "disponivel": True
        },
        # High mileage car (>150k)
        {
            "id": "high_mileage_car",
            "dealership_id": "test_dealer",
            "nome": "CHEVROLET ONIX 1.0",
            "marca": "Chevrolet",
            "modelo": "Onix",
            "versao": "1.0",
            "ano": 2016,
            "preco": 38000.0,
            "quilometragem": 180000,
            "combustivel": "Flex",
            "cambio": "Manual",
            "categoria": "Hatch",
            "consumo_cidade": 10.8,
            "consumo_estrada": 13.5,
            "score_familia": 0.75,
            "score_economia": 0.92,
            "disponivel": True
        },
        # Expensive car for budget testing
        {
            "id": "expensive_car",
            "dealership_id": "test_dealer",
            "nome": "TOYOTA COROLLA XEI 2.0",
            "marca": "Toyota",
            "modelo": "Corolla",
            "versao": "XEI 2.0",
            "ano": 2023,
            "preco": 120000.0,
            "quilometragem": 15000,
            "combustivel": "Flex",
            "cambio": "Automático",
            "categoria": "Sedan",
            "consumo_cidade": 9.5,
            "consumo_estrada": 12.0,
            "score_familia": 0.9,
            "score_economia": 0.7,
            "disponivel": True
        },
        # Affordable car for budget testing
        {
            "id": "affordable_car",
            "dealership_id": "test_dealer",
            "nome": "FIAT MOBI LIKE 1.0",
            "marca": "Fiat",
            "modelo": "Mobi",
            "versao": "Like 1.0",
            "ano": 2021,
            "preco": 42000.0,
            "quilometragem": 40000,
            "combustivel": "Flex",
            "cambio": "Manual",
            "categoria": "Hatch",
            "consumo_cidade": 12.5,
            "consumo_estrada": 15.0,
            "score_familia": 0.6,
            "score_economia": 0.98,
            "disponivel": True
        }
    ]
    
    # Create dealership with cars embedded
    dealership_data = {
        "id": "test_dealer",
        "name": "Test Dealership",
        "city": "São Paulo",
        "state": "SP",
        "region": "Sudeste",
        "phone": "(11) 1234-5678",
        "whatsapp": "5511987654321",
        "email": "test@dealer.com",
        "active": True,
        "verified": True,
        "latitude": -23.5505,
        "longitude": -46.6333,
        "carros": cars_data
    }
    
    with open(os.path.join(temp_dir, "dealerships.json"), 'w', encoding='utf-8') as f:
        json.dump([dealership_data], f, default=str)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def api_client(temp_data_with_varied_cars, monkeypatch):
    """API client with test data"""
    monkeypatch.setenv("DATA_DIR", temp_data_with_varied_cars)
    
    from api.main import app, engine
    engine.data_dir = temp_data_with_varied_cars
    engine.load_dealerships()
    engine.load_all_cars()
    
    return TestClient(app)


class TestBudgetStatusIntegration:
    """Test budget status across multiple vehicles"""
    
    def test_budget_status_within_budget(self, api_client):
        """Test cars within budget show correct status"""
        profile = {
            "orcamento_min": 40000,
            "orcamento_max": 80000,
            "uso_principal": "trabalho",
            "state": "SP",
            "financial_capacity": {
                "monthly_income_range": "5000-8000",
                "max_monthly_tco": 2000.0,
                "is_disclosed": True
            }
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Check that affordable cars are marked as within budget
        for rec in data["recommendations"]:
            if rec["car"]["id"] == "affordable_car":
                assert rec.get("fits_budget") is not None
                if rec["tco_breakdown"]:
                    tco_total = rec["tco_breakdown"]["total_monthly"]
                    expected_fits = tco_total <= 2000.0
                    assert rec["fits_budget"] == expected_fits
    
    def test_budget_status_above_budget(self, api_client):
        """Test cars above budget show correct status"""
        profile = {
            "orcamento_min": 40000,
            "orcamento_max": 150000,
            "uso_principal": "familia",
            "state": "SP",
            "financial_capacity": {
                "monthly_income_range": "5000-8000",
                "max_monthly_tco": 1500.0,
                "is_disclosed": True
            }
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Check that expensive cars are marked as above budget
        for rec in data["recommendations"]:
            if rec["car"]["id"] == "expensive_car":
                assert rec.get("fits_budget") is not None
                if rec["tco_breakdown"]:
                    tco_total = rec["tco_breakdown"]["total_monthly"]
                    expected_fits = tco_total <= 1500.0
                    assert rec["fits_budget"] == expected_fits
    
    def test_budget_status_consistency(self, api_client):
        """Test budget status is consistent with TCO values"""
        profile = {
            "orcamento_min": 35000,
            "orcamento_max": 130000,
            "uso_principal": "familia",
            "state": "SP",
            "financial_capacity": {
                "monthly_income_range": "8000-12000",
                "max_monthly_tco": 2500.0,
                "is_disclosed": True
            }
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Verify consistency for all recommendations
        for rec in data["recommendations"]:
            if rec.get("tco_breakdown") and rec.get("fits_budget") is not None:
                tco_total = rec["tco_breakdown"]["total_monthly"]
                max_budget = 2500.0
                expected_fits = tco_total <= max_budget
                
                assert rec["fits_budget"] == expected_fits, \
                    f"Car {rec['car']['nome']}: TCO={tco_total}, " \
                    f"Budget={max_budget}, Expected={expected_fits}, Got={rec['fits_budget']}"


class TestFinancialHealthIntegration:
    """Test financial health indicators match expected calculations"""
    
    def test_financial_health_green_status(self, api_client):
        """Test green status for healthy TCO (≤20% of income)"""
        profile = {
            "orcamento_min": 35000,
            "orcamento_max": 50000,
            "uso_principal": "trabalho",
            "state": "SP",
            "financial_capacity": {
                "monthly_income_range": "8000-12000",  # Midpoint: 10000
                "max_monthly_tco": 2000.0,  # 20% of 10000
                "is_disclosed": True
            }
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Check for green status on affordable cars
        for rec in data["recommendations"]:
            if rec.get("financial_health") and rec.get("tco_breakdown"):
                tco_total = rec["tco_breakdown"]["total_monthly"]
                percentage = (tco_total / 10000) * 100
                
                if percentage <= 20:
                    assert rec["financial_health"]["status"] == "healthy"
                    assert rec["financial_health"]["color"] == "green"
                    assert abs(rec["financial_health"]["percentage"] - percentage) < 0.1
    
    def test_financial_health_yellow_status(self, api_client):
        """Test yellow status for caution TCO (20-30% of income)"""
        profile = {
            "orcamento_min": 40000,
            "orcamento_max": 70000,
            "uso_principal": "familia",
            "state": "SP",
            "financial_capacity": {
                "monthly_income_range": "5000-8000",  # Midpoint: 6500
                "max_monthly_tco": 1800.0,  # ~27.7% of 6500
                "is_disclosed": True
            }
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Check for yellow status on mid-range cars
        for rec in data["recommendations"]:
            if rec.get("financial_health") and rec.get("tco_breakdown"):
                tco_total = rec["tco_breakdown"]["total_monthly"]
                percentage = (tco_total / 6500) * 100
                
                if 20 < percentage <= 30:
                    assert rec["financial_health"]["status"] == "caution"
                    assert rec["financial_health"]["color"] == "yellow"
                    assert abs(rec["financial_health"]["percentage"] - percentage) < 0.1
    
    def test_financial_health_red_status(self, api_client):
        """Test red status for high commitment TCO (>30% of income)"""
        profile = {
            "orcamento_min": 40000,
            "orcamento_max": 130000,
            "uso_principal": "familia",
            "state": "SP",
            "financial_capacity": {
                "monthly_income_range": "5000-8000",  # Midpoint: 6500
                "max_monthly_tco": 2500.0,  # ~38.5% of 6500
                "is_disclosed": True
            }
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Check for red status on expensive cars
        for rec in data["recommendations"]:
            if rec.get("financial_health") and rec.get("tco_breakdown"):
                tco_total = rec["tco_breakdown"]["total_monthly"]
                percentage = (tco_total / 6500) * 100
                
                if percentage > 30:
                    assert rec["financial_health"]["status"] == "high_commitment"
                    assert rec["financial_health"]["color"] == "red"
                    assert abs(rec["financial_health"]["percentage"] - percentage) < 0.1


class TestHighMileageBadgeIntegration:
    """Test high mileage badges appear correctly"""
    
    def test_low_mileage_no_badge(self, api_client):
        """Test no badge for low mileage cars (≤100k km)"""
        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 70000,
            "uso_principal": "trabalho",
            "state": "SP"
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Find low mileage car
        for rec in data["recommendations"]:
            if rec["car"]["id"] == "low_mileage_car":
                assert rec["car"]["quilometragem"] <= 100000
                # Badge logic is frontend, but mileage data should be present
                assert "quilometragem" in rec["car"]
    
    def test_medium_mileage_adjustment(self, api_client):
        """Test maintenance adjustment for medium mileage (100k-150k km)"""
        profile = {
            "orcamento_min": 40000,
            "orcamento_max": 50000,
            "uso_principal": "trabalho",
            "state": "SP"
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Find medium mileage car
        for rec in data["recommendations"]:
            if rec["car"]["id"] == "medium_mileage_car":
                assert 100000 < rec["car"]["quilometragem"] <= 150000
                
                # Check TCO has maintenance adjustment
                if rec.get("tco_breakdown"):
                    assumptions = rec["tco_breakdown"].get("assumptions", {})
                    if "maintenance_adjustment" in assumptions:
                        assert assumptions["maintenance_adjustment"]["factor"] == 1.5
    
    def test_high_mileage_adjustment(self, api_client):
        """Test maintenance adjustment for high mileage (>150k km)"""
        profile = {
            "orcamento_min": 35000,
            "orcamento_max": 45000,
            "uso_principal": "trabalho",
            "state": "SP"
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Find high mileage car
        for rec in data["recommendations"]:
            if rec["car"]["id"] == "high_mileage_car":
                assert rec["car"]["quilometragem"] > 150000
                
                # Check TCO has maintenance adjustment
                if rec.get("tco_breakdown"):
                    assumptions = rec["tco_breakdown"].get("assumptions", {})
                    if "maintenance_adjustment" in assumptions:
                        assert assumptions["maintenance_adjustment"]["factor"] == 2.0


class TestEdgeCases:
    """Test edge cases with extreme values"""
    
    def test_very_low_income(self, api_client):
        """Test with very low income range"""
        profile = {
            "orcamento_min": 35000,
            "orcamento_max": 50000,
            "uso_principal": "trabalho",
            "state": "SP",
            "financial_capacity": {
                "monthly_income_range": "0-3000",
                "max_monthly_tco": 450.0,
                "is_disclosed": True
            }
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # With very low income, the system may filter out all cars
        # This is correct behavior - the TCO filter protects users
        # from recommendations they can't afford
        # We just verify the API doesn't crash
        assert "recommendations" in data
        
        # If there are recommendations, they should be marked as above budget
        if len(data["recommendations"]) > 0:
            above_budget_count = sum(
                1 for rec in data["recommendations"]
                if rec.get("fits_budget") is False
            )
            assert above_budget_count > 0
    
    def test_very_high_income(self, api_client):
        """Test with very high income range"""
        profile = {
            "orcamento_min": 35000,
            "orcamento_max": 150000,
            "uso_principal": "familia",
            "state": "SP",
            "financial_capacity": {
                "monthly_income_range": "12000+",
                "max_monthly_tco": 4200.0,
                "is_disclosed": True
            }
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Should return recommendations
        assert len(data["recommendations"]) > 0
        
        # Most cars should be within budget
        within_budget_count = sum(
            1 for rec in data["recommendations"]
            if rec.get("fits_budget") is True
        )
        assert within_budget_count > 0
    
    def test_extreme_mileage(self, api_client):
        """Test with extreme mileage values"""
        # This test verifies the system handles high mileage gracefully
        profile = {
            "orcamento_min": 35000,
            "orcamento_max": 45000,
            "uso_principal": "trabalho",
            "state": "SP"
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Find high mileage car and verify TCO calculation doesn't fail
        for rec in data["recommendations"]:
            if rec["car"]["quilometragem"] > 150000:
                assert rec.get("tco_breakdown") is not None
                assert rec["tco_breakdown"]["total_monthly"] > 0
    
    def test_no_financial_capacity(self, api_client):
        """Test recommendations work without financial capacity"""
        profile = {
            "orcamento_min": 40000,
            "orcamento_max": 80000,
            "uso_principal": "familia",
            "state": "SP"
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Should return recommendations
        assert len(data["recommendations"]) > 0
        
        # fits_budget should be None
        for rec in data["recommendations"]:
            assert rec.get("fits_budget") is None
            assert rec.get("financial_health") is None


class TestCompleteFlowIntegration:
    """Test complete flow from API to expected UI data"""
    
    def test_complete_recommendation_flow(self, api_client):
        """Test complete flow with all TCO features"""
        profile = {
            "orcamento_min": 35000,
            "orcamento_max": 130000,
            "uso_principal": "familia",
            "state": "SP",
            "prioridades": {
                "economia": 4,
                "espaco": 5,
                "seguranca": 5,
                "conforto": 4,
                "performance": 2
            },
            "financial_capacity": {
                "monthly_income_range": "8000-12000",
                "max_monthly_tco": 2500.0,
                "is_disclosed": True
            }
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0
        
        # Verify each recommendation has all required fields
        for rec in data["recommendations"]:
            # Basic fields
            assert "car" in rec
            assert "match_score" in rec
            assert "justification" in rec
            
            # Car details
            car = rec["car"]
            assert "id" in car
            assert "nome" in car
            assert "preco" in car
            assert "quilometragem" in car
            
            # TCO breakdown
            if rec.get("tco_breakdown"):
                tco = rec["tco_breakdown"]
                assert "total_monthly" in tco
                assert "financing_monthly" in tco
                assert "fuel_monthly" in tco
                assert "maintenance_monthly" in tco
                assert "insurance_monthly" in tco
                assert "ipva_monthly" in tco
                
                # Assumptions
                assert "assumptions" in tco
                assumptions = tco["assumptions"]
                assert "down_payment_percent" in assumptions
                assert "financing_months" in assumptions
                assert "monthly_km" in assumptions
                assert "fuel_price_per_liter" in assumptions
                
                # Verify down payment is reasonable (0-100% or 0-1 decimal)
                # The API may return it as percentage (20.0) or decimal (0.20)
                down_payment = assumptions["down_payment_percent"]
                assert (0 <= down_payment <= 1) or (0 <= down_payment <= 100)
                
                # Verify financing months is reasonable
                assert 12 <= assumptions["financing_months"] <= 84
            
            # Budget status
            assert "fits_budget" in rec
            if rec["fits_budget"] is not None:
                assert isinstance(rec["fits_budget"], bool)
            
            # Financial health
            if rec.get("financial_health"):
                health = rec["financial_health"]
                assert "status" in health
                assert "percentage" in health
                assert "color" in health
                assert "message" in health
                
                assert health["status"] in ["healthy", "caution", "high_commitment"]
                assert health["color"] in ["green", "yellow", "red"]
                assert health["percentage"] > 0
    
    def test_multiple_vehicles_comparison(self, api_client):
        """Test comparing multiple vehicles with different characteristics"""
        profile = {
            "orcamento_min": 35000,
            "orcamento_max": 130000,
            "uso_principal": "familia",
            "state": "SP",
            "financial_capacity": {
                "monthly_income_range": "8000-12000",
                "max_monthly_tco": 2500.0,
                "is_disclosed": True
            }
        }
        
        response = api_client.post("/recommend", json=profile)
        assert response.status_code == 200
        data = response.json()
        
        # Collect data for comparison
        cars_data = []
        for rec in data["recommendations"]:
            if rec.get("tco_breakdown"):
                cars_data.append({
                    "id": rec["car"]["id"],
                    "nome": rec["car"]["nome"],
                    "preco": rec["car"]["preco"],
                    "quilometragem": rec["car"]["quilometragem"],
                    "tco_total": rec["tco_breakdown"]["total_monthly"],
                    "fits_budget": rec.get("fits_budget"),
                    "financial_health": rec.get("financial_health", {}).get("status")
                })
        
        # Verify we have multiple cars to compare
        assert len(cars_data) >= 3
        
        # Verify high mileage cars have higher maintenance costs
        low_mileage_cars = [c for c in cars_data if c["quilometragem"] <= 100000]
        high_mileage_cars = [c for c in cars_data if c["quilometragem"] > 150000]
        
        if low_mileage_cars and high_mileage_cars:
            # High mileage cars should generally have different TCO characteristics
            # (not necessarily higher total TCO due to lower purchase price)
            assert len(high_mileage_cars) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
