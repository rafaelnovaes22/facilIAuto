"""
Script para testar o sistema de tracking de ML
Simula interações de usuários e verifica se estão sendo salvas
"""
import requests
import json
from datetime import datetime

# Configuração
API_URL = "http://localhost:8000"

def test_ml_tracking():
    print("=" * 80)
    print("TESTE: Sistema de Tracking de ML")
    print("=" * 80)
    
    # 1. Verificar estatísticas iniciais
    print("\n1. Verificando estatísticas iniciais...")
    try:
        response = requests.get(f"{API_URL}/api/ml/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ API respondendo")
            print(f"   📊 Total de interações: {stats['data_collection']['total_interactions']}")
            print(f"   📈 Progresso: {stats['ml_readiness']['progress_percentage']:.1f}%")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro ao conectar: {e}")
        print(f"   💡 Certifique-se de que o backend está rodando em {API_URL}")
        return
    
    # 2. Simular interação de clique
    print("\n2. Simulando interação de CLIQUE...")
    interaction_click = {
        "session_id": f"test_session_{datetime.now().timestamp()}",
        "interaction_type": "click",
        "car_id": "car_test_001",
        "timestamp": datetime.now().isoformat(),
        "user_preferences": {
            "budget_min": 30000,
            "budget_max": 60000,
            "usage": "trabalho",
            "priorities": {
                "economia": 5,
                "espaco": 3,
                "performance": 2,
                "conforto": 3,
                "seguranca": 4
            }
        },
        "car_details": {
            "marca": "Chevrolet",
            "modelo": "Onix",
            "ano": 2017,
            "preco": 45900,
            "categoria": "Hatch"
        },
        "match_score": 0.85
    }
    
    try:
        response = requests.post(f"{API_URL}/api/interactions/track", json=interaction_click)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Interação salva: {result['status']}")
        else:
            print(f"   ❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Simular interação de visualização de detalhes
    print("\n3. Simulando interação de VISUALIZAÇÃO DE DETALHES...")
    interaction_view = {
        "session_id": f"test_session_{datetime.now().timestamp()}",
        "interaction_type": "view_details",
        "car_id": "car_test_002",
        "timestamp": datetime.now().isoformat(),
        "user_preferences": {
            "budget_min": 40000,
            "budget_max": 80000,
            "usage": "familia",
            "priorities": {
                "economia": 3,
                "espaco": 5,
                "performance": 2,
                "conforto": 4,
                "seguranca": 5
            }
        },
        "car_details": {
            "marca": "Volkswagen",
            "modelo": "Tiguan",
            "ano": 2020,
            "preco": 75000,
            "categoria": "SUV"
        },
        "match_score": 0.92,
        "duration_seconds": 45
    }
    
    try:
        response = requests.post(f"{API_URL}/api/interactions/track", json=interaction_view)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Interação salva: {result['status']}")
        else:
            print(f"   ❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Simular interação de WhatsApp (alto interesse)
    print("\n4. Simulando interação de WHATSAPP (alto interesse)...")
    interaction_whatsapp = {
        "session_id": f"test_session_{datetime.now().timestamp()}",
        "interaction_type": "whatsapp_contact",
        "car_id": "car_test_003",
        "timestamp": datetime.now().isoformat(),
        "user_preferences": {
            "budget_min": 50000,
            "budget_max": 100000,
            "usage": "lazer",
            "priorities": {
                "economia": 2,
                "espaco": 4,
                "performance": 5,
                "conforto": 5,
                "seguranca": 4
            }
        },
        "car_details": {
            "marca": "Toyota",
            "modelo": "Hilux",
            "ano": 2021,
            "preco": 95000,
            "categoria": "Pickup"
        },
        "match_score": 0.88
    }
    
    try:
        response = requests.post(f"{API_URL}/api/interactions/track", json=interaction_whatsapp)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Interação salva: {result['status']}")
        else:
            print(f"   ❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 5. Verificar estatísticas finais
    print("\n5. Verificando estatísticas finais...")
    try:
        response = requests.get(f"{API_URL}/api/ml/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Estatísticas atualizadas")
            print(f"   📊 Total de interações: {stats['data_collection']['total_interactions']}")
            print(f"   👆 Cliques: {stats['data_collection']['click_count']}")
            print(f"   👁️  Visualizações: {stats['data_collection']['view_details_count']}")
            print(f"   💬 WhatsApp: {stats['data_collection']['whatsapp_contact_count']}")
            print(f"   📈 Progresso: {stats['ml_readiness']['progress_percentage']:.1f}%")
            print(f"   🎯 Faltam {stats['ml_readiness']['interactions_needed']} interações para treinar")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 6. Exportar dados
    print("\n6. Exportando dados coletados...")
    try:
        response = requests.get(f"{API_URL}/api/ml/export-data?limit=10")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Dados exportados")
            print(f"   📦 Total exportado: {data['total_interactions']} interações")
            
            if data['total_interactions'] > 0:
                print(f"\n   Exemplo de interação:")
                example = data['data']['interactions'][0]
                print(f"      ID: {example.get('id')}")
                print(f"      Tipo: {example.get('interaction_type')}")
                print(f"      Carro: {example.get('car_id')}")
                print(f"      Score: {example.get('match_score')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO")
    print("=" * 80)
    print("\n💡 Próximos passos:")
    print("   1. Verificar arquivo: platform/backend/data/interactions/user_interactions.json")
    print("   2. Testar no frontend: abrir site e clicar em carros")
    print("   3. Monitorar logs do backend para ver interações sendo salvas")

if __name__ == "__main__":
    test_ml_tracking()
