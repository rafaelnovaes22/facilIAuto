"""
Script para verificar dados de ML em PRODUÇÃO
Verifica se o sistema está coletando dados dos usuários reais
"""
import requests
import json
from datetime import datetime

# URL de produção (ajuste se necessário)
PRODUCTION_URL = "https://faciliauto-backend-production.up.railway.app"

def check_production_data():
    print("=" * 80)
    print("VERIFICAÇÃO: Dados de ML em PRODUÇÃO")
    print("=" * 80)
    print(f"\n🌐 URL: {PRODUCTION_URL}")
    
    # 1. Verificar se API está online
    print("\n1. Verificando se API está online...")
    try:
        response = requests.get(f"{PRODUCTION_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API online")
            print(f"   📊 Status: {data.get('status')}")
            print(f"   🏢 Concessionárias: {data.get('dealerships')}")
            print(f"   🚗 Carros: {data.get('cars')}")
        else:
            print(f"   ❌ API retornou erro: {response.status_code}")
            return
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout ao conectar (>10s)")
        print(f"   💡 O servidor pode estar dormindo (Railway free tier)")
        print(f"   💡 Tente novamente em 30 segundos")
        return
    except Exception as e:
        print(f"   ❌ Erro ao conectar: {e}")
        return
    
    # 2. Verificar estatísticas de ML
    print("\n2. Verificando estatísticas de ML...")
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/ml/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            
            total = stats['data_collection']['total_interactions']
            clicks = stats['data_collection']['click_count']
            views = stats['data_collection']['view_details_count']
            whatsapp = stats['data_collection']['whatsapp_contact_count']
            sessions = stats['data_collection']['unique_sessions']
            cars = stats['data_collection']['unique_cars']
            progress = stats['ml_readiness']['progress_percentage']
            needed = stats['ml_readiness']['interactions_needed']
            last = stats['data_collection']['last_interaction']
            
            print(f"   ✅ Estatísticas obtidas")
            print(f"\n   📊 DADOS COLETADOS:")
            print(f"      Total de interações: {total}")
            print(f"      👆 Cliques: {clicks}")
            print(f"      👁️  Visualizações: {views}")
            print(f"      💬 WhatsApp: {whatsapp}")
            print(f"      👥 Sessões únicas: {sessions}")
            print(f"      🚗 Carros únicos: {cars}")
            
            print(f"\n   📈 PROGRESSO PARA ML:")
            print(f"      Progresso: {progress:.1f}%")
            print(f"      Faltam: {needed} interações")
            print(f"      Meta: 500 interações")
            
            if last:
                print(f"\n   🕐 ÚLTIMA INTERAÇÃO:")
                print(f"      {last}")
            else:
                print(f"\n   ⚠️  Nenhuma interação registrada ainda")
            
            # Análise
            print(f"\n   🔍 ANÁLISE:")
            if total == 0:
                print(f"      ❌ NENHUM DADO COLETADO")
                print(f"      💡 Possíveis causas:")
                print(f"         - Usuários não estão clicando nos carros")
                print(f"         - Frontend não está enviando dados")
                print(f"         - Erro de configuração (CORS, URL)")
            elif total < 50:
                print(f"      ⚠️  POUCOS DADOS ({total} interações)")
                print(f"      💡 Continue monitorando")
                print(f"      💡 Promova o site para mais usuários")
            elif total < 500:
                print(f"      ✅ COLETANDO DADOS ({total} interações)")
                print(f"      💡 Faltam {needed} para análise inicial")
            else:
                print(f"      🎉 PRONTO PARA ANÁLISE!")
                print(f"      💡 Você pode exportar os dados e começar a treinar")
            
        else:
            print(f"   ❌ Erro ao obter estatísticas: {response.status_code}")
            print(f"   📄 Resposta: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Tentar exportar amostra de dados
    print("\n3. Exportando amostra de dados (últimas 10 interações)...")
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/ml/export-data?limit=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_exported = data['total_interactions']
            
            print(f"   ✅ Dados exportados")
            print(f"   📦 Total: {total_exported} interações")
            
            if total_exported > 0:
                print(f"\n   📋 EXEMPLO DE INTERAÇÃO:")
                example = data['data']['interactions'][0]
                print(f"      ID: {example.get('id')}")
                print(f"      Tipo: {example.get('interaction_type')}")
                print(f"      Carro: {example.get('car_id')}")
                print(f"      Score: {example.get('match_score')}")
                print(f"      Timestamp: {example.get('timestamp')}")
                
                # Mostrar preferências do usuário
                prefs = example.get('user_preferences', {})
                if prefs:
                    print(f"\n      👤 PREFERÊNCIAS DO USUÁRIO:")
                    print(f"         Orçamento: R$ {prefs.get('budget_min', 0):,.0f} - R$ {prefs.get('budget_max', 0):,.0f}")
                    print(f"         Uso: {prefs.get('usage', 'N/A')}")
                    priorities = prefs.get('priorities', {})
                    if priorities:
                        print(f"         Prioridades:")
                        for key, value in priorities.items():
                            print(f"            - {key}: {value}")
                
                # Mostrar detalhes do carro
                car = example.get('car_details', {})
                if car:
                    print(f"\n      🚗 CARRO:")
                    print(f"         {car.get('marca')} {car.get('modelo')} ({car.get('ano')})")
                    print(f"         Preço: R$ {car.get('preco', 0):,.0f}")
                    print(f"         Categoria: {car.get('categoria')}")
            else:
                print(f"   ⚠️  Nenhuma interação para exportar")
        else:
            print(f"   ❌ Erro ao exportar: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO CONCLUÍDA")
    print("=" * 80)
    
    # Resumo e próximos passos
    print("\n📝 RESUMO:")
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/ml/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            total = stats['data_collection']['total_interactions']
            
            if total == 0:
                print("   ❌ Sistema NÃO está coletando dados")
                print("\n💡 PRÓXIMOS PASSOS:")
                print("   1. Verificar logs do Railway (backend)")
                print("   2. Abrir o site e testar manualmente")
                print("   3. Verificar console do navegador (F12)")
                print("   4. Verificar se VITE_API_URL está correto no frontend")
            elif total < 500:
                print(f"   ✅ Sistema está coletando dados ({total} interações)")
                print("\n💡 PRÓXIMOS PASSOS:")
                print("   1. Continuar monitorando")
                print("   2. Promover o site para mais usuários")
                print(f"   3. Aguardar {stats['ml_readiness']['interactions_needed']} interações para análise")
            else:
                print(f"   🎉 Pronto para análise! ({total} interações)")
                print("\n💡 PRÓXIMOS PASSOS:")
                print("   1. Exportar todos os dados")
                print("   2. Fazer análise exploratória")
                print("   3. Treinar modelo inicial")
    except:
        pass

if __name__ == "__main__":
    check_production_data()
