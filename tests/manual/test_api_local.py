"""
Teste da API local para verificar TCO
"""
import requests
import json

# URL da API local
API_URL = "http://localhost:8000"

# Perfil de teste
profile = {
    "orcamento_min": 50000,
    "orcamento_max": 150000,
    "uso_principal": "familia",
    "state": "SP",
    "prioridades": {
        "economia": 4,
        "espaco": 5,
        "seguranca": 5,
        "conforto": 4,
        "performance": 2
    }
}

print("=" * 80)
print("TESTE API - Recomendações com TCO")
print("=" * 80)

try:
    # Fazer requisição
    response = requests.post(f"{API_URL}/recommend", json=profile, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ API respondeu com sucesso!")
        print(f"Total de recomendações: {data.get('total_recommendations', 0)}")
        
        # Procurar pelo Chery Tiggo
        for rec in data.get('recommendations', []):
            car = rec.get('car', {})
            if 'CHERY' in car.get('nome', '').upper() and 'TIGGO' in car.get('nome', '').upper():
                print("\n" + "=" * 80)
                print(f"🚗 {car.get('nome')}")
                print("=" * 80)
                print(f"Preço: R$ {car.get('preco'):,.2f}")
                print(f"Ano: {car.get('ano')}")
                print(f"Quilometragem: {car.get('quilometragem'):,} km")
                
                tco = rec.get('tco_breakdown')
                if tco:
                    print("\n📊 TCO BREAKDOWN:")
                    print("-" * 80)
                    print(f"Financiamento:  R$ {tco.get('financing_monthly'):>8,.2f}/mês")
                    print(f"Combustível:    R$ {tco.get('fuel_monthly'):>8,.2f}/mês")
                    print(f"Manutenção:     R$ {tco.get('maintenance_monthly'):>8,.2f}/mês")
                    print(f"Seguro:         R$ {tco.get('insurance_monthly'):>8,.2f}/mês")
                    print(f"IPVA:           R$ {tco.get('ipva_monthly'):>8,.2f}/mês")
                    print("-" * 80)
                    print(f"TOTAL:          R$ {tco.get('total_monthly'):>8,.2f}/mês")
                    
                    # Premissas
                    assumptions = tco.get('assumptions', {})
                    print("\n🔍 PREMISSAS:")
                    print("-" * 80)
                    print(f"Entrada: {assumptions.get('down_payment_percent')}%")
                    print(f"Prazo: {assumptions.get('financing_months')}x")
                    print(f"Taxa de juros: {assumptions.get('annual_interest_rate')}% a.a.")
                    print(f"Km/mês: {assumptions.get('monthly_km')} km")
                    print(f"Combustível: R$ {assumptions.get('fuel_price_per_liter')}/L")
                    print(f"Consumo: {assumptions.get('fuel_efficiency')} km/L")
                    
                    # Ajuste de manutenção
                    maint_adj = assumptions.get('maintenance_adjustment')
                    if maint_adj:
                        print(f"\n⚠️ AJUSTE DE MANUTENÇÃO:")
                        print(f"   Fator: {maint_adj.get('factor')}x")
                        print(f"   Razão: {maint_adj.get('reason')}")
                    
                    print("=" * 80)
                    
                    # Validação
                    print("\n✅ VALIDAÇÃO:")
                    if assumptions.get('down_payment_percent') == 20.0:
                        print("✓ Entrada correta: 20%")
                    else:
                        print(f"✗ Entrada incorreta: {assumptions.get('down_payment_percent')}%")
                    
                    if assumptions.get('annual_interest_rate') == 12.0:
                        print("✓ Taxa de juros correta: 12% a.a.")
                    else:
                        print(f"✗ Taxa incorreta: {assumptions.get('annual_interest_rate')}% a.a.")
                    
                    if tco.get('maintenance_monthly') >= 600:
                        print(f"✓ Manutenção com ajuste de alta km: R$ {tco.get('maintenance_monthly'):.2f}")
                    else:
                        print(f"✗ Manutenção sem ajuste: R$ {tco.get('maintenance_monthly'):.2f}")
                    
                    if tco.get('total_monthly') >= 3200:
                        print(f"✓ Total correto: R$ {tco.get('total_monthly'):.2f}")
                    else:
                        print(f"✗ Total incorreto: R$ {tco.get('total_monthly'):.2f}")
                
                break
        else:
            print("\n⚠️ Chery Tiggo não encontrado nas recomendações")
            print("\nCarros encontrados:")
            for rec in data.get('recommendations', [])[:5]:
                car = rec.get('car', {})
                print(f"  - {car.get('nome')} (R$ {car.get('preco'):,.2f})")
    
    else:
        print(f"\n❌ Erro na API: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n❌ Erro: API não está rodando!")
    print("Execute: python platform/backend/api/main.py")
except Exception as e:
    print(f"\n❌ Erro: {e}")

print("\n" + "=" * 80)
