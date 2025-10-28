#!/usr/bin/env python3
"""Smoke tests para validar funcionalidade básica do backend"""

from fastapi.testclient import TestClient
from api.main import app
import json

client = TestClient(app)

def test_health():
    """Teste 1: Health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dealerships"] >= 1
    assert data["cars"] >= 1
    print("✓ Health check passou")
    return True

def test_stats():
    """Teste 2: Stats endpoint"""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_cars" in data
    assert "total_dealerships" in data
    print("✓ Stats endpoint passou")
    return True

def test_dealerships():
    """Teste 3: Listar concessionárias"""
    response = client.get("/dealerships")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    print(f"✓ Dealerships endpoint passou ({len(data)} concessionárias)")
    return True

def test_cars():
    """Teste 4: Listar carros"""
    response = client.get("/cars")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    print(f"✓ Cars endpoint passou ({len(data)} carros)")
    return True

def test_recommend():
    """Teste 5: Recomendações"""
    payload = {
        "orcamento_min": 30000,
        "orcamento_max": 80000,
        "uso_principal": "familia",
        "prioridades": {
            "economia": 3,
            "espaco": 5,
            "performance": 2,
            "conforto": 4,
            "seguranca": 5
        },
        "preferencias": {
            "tipo_combustivel": "flex",
            "tipo_cambio": "automatico"
        },
        "localizacao": {
            "estado": "SP",
            "cidade": "São Paulo"
        }
    }
    
    response = client.post("/recommend", json=payload)
    if response.status_code != 200:
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    print(f"✓ Recommend endpoint passou ({len(data['recommendations'])} recomendações)")
    return True

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SMOKE TESTS - BACKEND")
    print("="*60 + "\n")
    
    tests = [
        test_health,
        test_stats,
        test_dealerships,
        test_cars,
        test_recommend
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            import traceback
            print(f"✗ {test.__name__} falhou: {e}")
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTADO: {passed} passou, {failed} falhou")
    print("="*60 + "\n")
    
    exit(0 if failed == 0 else 1)
