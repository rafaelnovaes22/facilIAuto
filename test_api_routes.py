"""
Test script to verify /api prefix routes
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_routes():
    """Test health check routes"""
    print("\n=== Testing Health Routes ===")
    
    # Test without prefix
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✓ GET /health: {response.status_code}")
        print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"✗ GET /health: {e}")
    
    # Test with /api prefix
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"✓ GET /api/health: {response.status_code}")
        print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"✗ GET /api/health: {e}")


def test_stats_routes():
    """Test stats routes"""
    print("\n=== Testing Stats Routes ===")
    
    # Test without prefix
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print(f"✓ GET /stats: {response.status_code}")
        data = response.json()
        print(f"  Available cars: {data.get('available_cars')}")
    except Exception as e:
        print(f"✗ GET /stats: {e}")
    
    # Test with /api prefix
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        print(f"✓ GET /api/stats: {response.status_code}")
        data = response.json()
        print(f"  Available cars: {data.get('available_cars')}")
    except Exception as e:
        print(f"✗ GET /api/stats: {e}")


def test_dealerships_routes():
    """Test dealerships routes"""
    print("\n=== Testing Dealerships Routes ===")
    
    # Test without prefix
    try:
        response = requests.get(f"{BASE_URL}/dealerships")
        print(f"✓ GET /dealerships: {response.status_code}")
        data = response.json()
        print(f"  Dealerships: {len(data)}")
    except Exception as e:
        print(f"✗ GET /dealerships: {e}")
    
    # Test with /api prefix
    try:
        response = requests.get(f"{BASE_URL}/api/dealerships")
        print(f"✓ GET /api/dealerships: {response.status_code}")
        data = response.json()
        print(f"  Dealerships: {len(data)}")
    except Exception as e:
        print(f"✗ GET /api/dealerships: {e}")


def test_recommend_routes():
    """Test recommend routes"""
    print("\n=== Testing Recommend Routes ===")
    
    # Sample profile
    profile = {
        "orcamento_min": 50000,
        "orcamento_max": 80000,
        "ano_minimo": 2018,
        "ano_maximo": 2024,
        "uso_principal": "familia",
        "prioridades": {
            "economia": 3,
            "espaco": 5,
            "performance": 2,
            "conforto": 4,
            "seguranca": 5
        },
        "state": "SP",
        "city": "São Paulo"
    }
    
    # Test without prefix
    try:
        response = requests.post(f"{BASE_URL}/recommend", json=profile)
        print(f"✓ POST /recommend: {response.status_code}")
        data = response.json()
        print(f"  Recommendations: {data.get('total_recommendations')}")
        if data.get('message'):
            print(f"  Message: {data.get('message')}")
    except Exception as e:
        print(f"✗ POST /recommend: {e}")
    
    # Test with /api prefix
    try:
        response = requests.post(f"{BASE_URL}/api/recommend", json=profile)
        print(f"✓ POST /api/recommend: {response.status_code}")
        data = response.json()
        print(f"  Recommendations: {data.get('total_recommendations')}")
        if data.get('message'):
            print(f"  Message: {data.get('message')}")
    except Exception as e:
        print(f"✗ POST /api/recommend: {e}")


def test_no_dealerships_response():
    """Test response when no dealerships in region"""
    print("\n=== Testing No Dealerships Response ===")
    
    # Profile with state that has no dealerships
    profile = {
        "orcamento_min": 50000,
        "orcamento_max": 80000,
        "ano_minimo": 2018,
        "ano_maximo": 2024,
        "uso_principal": "familia",
        "prioridades": {
            "economia": 3,
            "espaco": 5,
            "performance": 2,
            "conforto": 4,
            "seguranca": 5
        },
        "state": "AC",  # Acre - likely no dealerships
        "city": "Rio Branco"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/recommend", json=profile)
        print(f"✓ POST /api/recommend (no dealerships): {response.status_code}")
        data = response.json()
        print(f"  Recommendations: {data.get('total_recommendations')}")
        print(f"  Message: {data.get('message')}")
        print(f"  Suggestion: {data.get('suggestion')}")
    except Exception as e:
        print(f"✗ POST /api/recommend (no dealerships): {e}")


if __name__ == "__main__":
    print("Testing API Routes with /api prefix support")
    print("=" * 50)
    
    test_health_routes()
    test_stats_routes()
    test_dealerships_routes()
    test_recommend_routes()
    test_no_dealerships_response()
    
    print("\n" + "=" * 50)
    print("Tests completed!")
