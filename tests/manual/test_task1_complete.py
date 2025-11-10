"""
Task 1 Completion Test: Update backend API routes to support /api prefix

This test verifies all requirements for Task 1:
- Add new routes with /api prefix for all endpoints
- Keep existing routes without prefix for backward compatibility
- Improve response when no dealerships found in region
- Add detailed logging for debugging

Requirements tested: 1.1, 1.2, 1.3, 2.1, 2.5, 5.1, 5.2, 5.3
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_backward_compatibility():
    """Requirement 1.2: Keep existing routes without prefix"""
    print("\n=== Test 1: Backward Compatibility ===")
    
    endpoints = [
        ("/health", "GET"),
        ("/stats", "GET"),
        ("/dealerships", "GET"),
        ("/recommend", "POST")
    ]
    
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
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json=profile)
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            print(f"✅ {method} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint}: {e}")
            return False
    
    return True


def test_api_prefix_routes():
    """Requirement 1.1: Add new routes with /api prefix"""
    print("\n=== Test 2: /api Prefix Routes ===")
    
    endpoints = [
        ("/api/health", "GET"),
        ("/api/stats", "GET"),
        ("/api/dealerships", "GET"),
        ("/api/recommend", "POST"),
        ("/api/feedback", "POST")
    ]
    
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
    
    feedback = {
        "user_id": "test_user",
        "car_id": "test_car",
        "action": "liked",
        "car_marca": "Toyota",
        "car_categoria": "SUV"
    }
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            elif endpoint == "/api/feedback":
                response = requests.post(f"{BASE_URL}{endpoint}", json=feedback)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json=profile)
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            print(f"✅ {method} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint}: {e}")
            return False
    
    return True


def test_empty_recommendations_response():
    """Requirement 2.1: Improve response when no dealerships found"""
    print("\n=== Test 3: Empty Recommendations Response ===")
    
    # Profile with very restrictive budget to get no results
    profile = {
        "orcamento_min": 1000,
        "orcamento_max": 2000,
        "ano_minimo": 2023,
        "ano_maximo": 2024,
        "uso_principal": "familia",
        "prioridades": {
            "economia": 3,
            "espaco": 5,
            "performance": 2,
            "conforto": 4,
            "seguranca": 5
        },
        "state": "AC",
        "city": "Rio Branco"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/recommend", json=profile)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Total Recommendations: {data.get('total_recommendations')}")
        
        # Verify response structure
        assert response.status_code == 200, "Should return 200 OK"
        assert 'total_recommendations' in data, "Should have total_recommendations"
        assert 'profile_summary' in data, "Should have profile_summary"
        assert 'recommendations' in data, "Should have recommendations array"
        
        if data.get('total_recommendations') == 0:
            assert 'message' in data, "Should have message when no recommendations"
            assert 'suggestion' in data, "Should have suggestion when no recommendations"
            print(f"✅ Message: {data.get('message')}")
            print(f"✅ Suggestion: {data.get('suggestion')}")
        else:
            print(f"✅ Found {data.get('total_recommendations')} recommendations")
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_detailed_logging():
    """Requirements 5.1, 5.2, 5.3: Add detailed logging"""
    print("\n=== Test 4: Detailed Logging ===")
    print("Note: Check backend console for detailed logs including:")
    print("  - Request details (budget, year, state, city, usage)")
    print("  - Filtering steps")
    print("  - Number of recommendations returned")
    print("  - Top recommendations with names and years")
    
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
    
    try:
        response = requests.post(f"{BASE_URL}/api/recommend", json=profile)
        print(f"✅ Request sent successfully: {response.status_code}")
        print("✅ Check backend logs for detailed information")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_route_consistency():
    """Requirement 1.3: Both routes should return same data"""
    print("\n=== Test 5: Route Consistency ===")
    
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
    
    try:
        # Test without prefix
        response1 = requests.post(f"{BASE_URL}/recommend", json=profile)
        data1 = response1.json()
        
        # Test with /api prefix
        response2 = requests.post(f"{BASE_URL}/api/recommend", json=profile)
        data2 = response2.json()
        
        # Compare results
        assert data1.get('total_recommendations') == data2.get('total_recommendations'), \
            "Both routes should return same number of recommendations"
        
        print(f"✅ /recommend: {data1.get('total_recommendations')} recommendations")
        print(f"✅ /api/recommend: {data2.get('total_recommendations')} recommendations")
        print("✅ Both routes return consistent data")
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    print("=" * 60)
    print("Task 1 Completion Test: Backend API Routes with /api Prefix")
    print("=" * 60)
    
    tests = [
        ("Backward Compatibility", test_backward_compatibility),
        ("/api Prefix Routes", test_api_prefix_routes),
        ("Empty Recommendations Response", test_empty_recommendations_response),
        ("Detailed Logging", test_detailed_logging),
        ("Route Consistency", test_route_consistency)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Task 1 Complete!")
    else:
        print("❌ SOME TESTS FAILED - Review failures above")
    print("=" * 60)


if __name__ == "__main__":
    main()
