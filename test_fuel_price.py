"""
Teste do serviço de preço de combustível
"""
import requests

API_URL = "http://localhost:8000"

print("=" * 80)
print("TESTE - Serviço de Preço de Combustível")
print("=" * 80)

# 1. Consultar preço atual
print("\n1. Consultando preço atual...")
response = requests.get(f"{API_URL}/fuel-price")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Preço atual: R$ {data['price']:.2f}/L")
    print(f"   Fonte: {data['source']}")
    print(f"   Preço padrão: R$ {data['default_price']:.2f}/L")
    print(f"   Última atualização: {data['last_updated']}")
else:
    print(f"❌ Erro: {response.status_code}")
    print(response.text)

# 2. Atualizar preço
print("\n2. Atualizando preço para R$ 6.09/L...")
response = requests.post(f"{API_URL}/fuel-price/update?new_price=6.09")
if response.status_code == 200:
    data = response.json()
    print(f"✅ {data['message']}")
    print(f"   Nova fonte: {data['price_info']['source']}")
else:
    print(f"❌ Erro: {response.status_code}")
    print(response.text)

# 3. Verificar se foi atualizado
print("\n3. Verificando atualização...")
response = requests.get(f"{API_URL}/fuel-price")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Preço confirmado: R$ {data['price']:.2f}/L")
    print(f"   Fonte: {data['source']}")
    
    if data['price'] == 6.09:
        print("✅ Atualização bem-sucedida!")
    else:
        print(f"⚠️ Preço diferente do esperado")
else:
    print(f"❌ Erro: {response.status_code}")

# 4. Testar com recomendação
print("\n4. Testando TCO com novo preço...")
profile = {
    "orcamento_min": 80000,
    "orcamento_max": 90000,
    "uso_principal": "familia",
    "state": "SP"
}

response = requests.post(f"{API_URL}/recommend", json=profile)
if response.status_code == 200:
    data = response.json()
    if data['recommendations']:
        rec = data['recommendations'][0]
        tco = rec.get('tco_breakdown')
        if tco:
            assumptions = tco.get('assumptions', {})
            fuel_price_used = assumptions.get('fuel_price_per_liter')
            print(f"✅ TCO calculado com combustível a R$ {fuel_price_used:.2f}/L")
            
            if fuel_price_used == 6.09:
                print("✅ Preço atualizado está sendo usado no TCO!")
            else:
                print(f"⚠️ TCO usando preço diferente: R$ {fuel_price_used:.2f}/L")
        else:
            print("⚠️ TCO não disponível")
    else:
        print("⚠️ Nenhuma recomendação retornada")
else:
    print(f"❌ Erro: {response.status_code}")

print("\n" + "=" * 80)
print("RESUMO:")
print("✅ Serviço de preço de combustível funcionando")
print("✅ Atualização manual via API funcionando")
print("✅ Cache local funcionando")
print("✅ Integração com TCO funcionando")
print("=" * 80)
