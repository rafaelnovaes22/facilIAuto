"""
Test to verify improved response when no dealerships found in region
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_no_dealerships():
    """Test response when no dealerships in region"""
    print("\n=== Testing No Dealerships Response ===\n")
    
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
        "state": "AC",  # Acre - no dealerships
        "city": "Rio Branco"
    }
    
    # Test with /api prefix
    response = requests.post(f"{BASE_URL}/api/recommend", json=profile)
    
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    data = response.json()
    
    # Verify response structure
    assert response.status_code == 200, "Should return 200 OK"
    assert data.get('total_recommendations') == 0, "Should have 0 recommendations"
    assert 'message' in data, "Should have a message field"
    assert 'suggestion' in data, "Should have a suggestion field"
    assert 'profile_summary' in data, "Should have profile_summary"
    assert 'recommendations' in data, "Should have recommendations array"
    assert len(data['recommendations']) == 0, "Recommendations array should be empty"
    
    print("\n✅ All assertions passed!")
    print(f"✅ Message: {data.get('message')}")
    print(f"✅ Suggestion: {data.get('suggestion')}")


if __name__ == "__main__":
    test_no_dealerships()
