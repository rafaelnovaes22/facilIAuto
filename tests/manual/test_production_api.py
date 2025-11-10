"""
Test script to verify production API endpoints
"""
import requests
import json

API_URL = "https://faciliauto-backend-production.up.railway.app"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing /health ===")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_api_health():
    """Test /api/health endpoint"""
    print("\n=== Testing /api/health ===")
    response = requests.get(f"{API_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_recommend():
    """Test /recommend endpoint"""
    print("\n=== Testing POST /recommend ===")
    
    profile = {
        "orcamento_min": 50000,
        "orcamento_max": 80000,
        "ano_minimo": 2018,
        "ano_maximo": 2024,
        "state": "SP",
        "city": "São Paulo",
        "uso_principal": "familia",
        "tamanho_familia": 4,
        "prioridades": {
            "economia": 4,
            "espaco": 5,
            "performance": 3,
            "conforto": 4,
            "seguranca": 5
        }
    }
    
    response = requests.post(
        f"{API_URL}/recommend",
        json=profile,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total recommendations: {data.get('total_recommendations', 0)}")
    else:
        print(f"Error: {response.text}")

def test_api_recommend():
    """Test /api/recommend endpoint"""
    print("\n=== Testing POST /api/recommend ===")
    
    profile = {
        "orcamento_min": 50000,
        "orcamento_max": 80000,
        "ano_minimo": 2018,
        "ano_maximo": 2024,
        "state": "SP",
        "city": "São Paulo",
        "uso_principal": "familia",
        "tamanho_familia": 4,
        "prioridades": {
            "economia": 4,
            "espaco": 5,
            "performance": 3,
            "conforto": 4,
            "seguranca": 5
        }
    }
    
    response = requests.post(
        f"{API_URL}/api/recommend",
        json=profile,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total recommendations: {data.get('total_recommendations', 0)}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_health()
    test_api_health()
    test_recommend()
    test_api_recommend()
