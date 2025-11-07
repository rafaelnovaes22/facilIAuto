"""
Teste para validar lógica de localização opcional
"""
import requests
import json

API_URL = "https://faciliauto-backend-production.up.railway.app"

def test_with_state():
    """Teste com estado especificado - deve filtrar por estado"""
    print("\n=== Teste 1: COM estado (SP) ===")
    
    profile = {
        "orcamento_min": 50000,
        "orcamento_max": 80000,
        "ano_minimo": 2018,
        "ano_maximo": 2024,
        "state": "SP",  # Estado especificado
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
    
    response = requests.post(f"{API_URL}/recommend", json=profile)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total recomendações: {data.get('total_recommendations', 0)}")
        print(f"Localização: {data.get('profile_summary', {}).get('location', 'N/A')}")
        if data.get('message'):
            print(f"Mensagem: {data.get('message')}")
        if data.get('recommendations'):
            print(f"Primeiro carro: {data['recommendations'][0]['car']['nome']}")
    else:
        print(f"Erro: {response.text}")

def test_without_state():
    """Teste SEM estado - deve mostrar carros de qualquer lugar"""
    print("\n=== Teste 2: SEM estado (qualquer localização) ===")
    
    profile = {
        "orcamento_min": 50000,
        "orcamento_max": 80000,
        "ano_minimo": 2018,
        "ano_maximo": 2024,
        # state e city não especificados
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
    
    response = requests.post(f"{API_URL}/recommend", json=profile)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total recomendações: {data.get('total_recommendations', 0)}")
        print(f"Localização: {data.get('profile_summary', {}).get('location', 'N/A')}")
        if data.get('message'):
            print(f"Mensagem: {data.get('message')}")
        if data.get('recommendations'):
            print(f"Primeiro carro: {data['recommendations'][0]['car']['nome']}")
            print(f"Estado do carro: {data['recommendations'][0]['car']['dealership_state']}")
    else:
        print(f"Erro: {response.text}")

def test_with_nonexistent_state():
    """Teste com estado que não existe no sistema"""
    print("\n=== Teste 3: COM estado inexistente (AC) ===")
    
    profile = {
        "orcamento_min": 50000,
        "orcamento_max": 80000,
        "ano_minimo": 2018,
        "ano_maximo": 2024,
        "state": "AC",  # Acre - provavelmente não tem concessionárias
        "city": "Rio Branco",
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
    
    response = requests.post(f"{API_URL}/recommend", json=profile)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total recomendações: {data.get('total_recommendations', 0)}")
        print(f"Localização: {data.get('profile_summary', {}).get('location', 'N/A')}")
        if data.get('message'):
            print(f"Mensagem: {data.get('message')}")
        if data.get('suggestion'):
            print(f"Sugestão: {data.get('suggestion')}")
    else:
        print(f"Erro: {response.text}")

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE: Lógica de Localização Opcional")
    print("=" * 60)
    
    test_with_state()
    test_without_state()
    test_with_nonexistent_state()
    
    print("\n" + "=" * 60)
    print("CONCLUSÃO:")
    print("- Teste 1: Deve filtrar por SP e mostrar carros de SP")
    print("- Teste 2: Deve mostrar carros de QUALQUER estado")
    print("- Teste 3: Deve mostrar mensagem específica sobre AC")
    print("=" * 60)
