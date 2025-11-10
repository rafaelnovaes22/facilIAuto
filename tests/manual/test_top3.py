"""
Teste para verificar que apenas 3 carros são retornados
"""
import requests

API_URL = "http://localhost:8000"

profile = {
    "orcamento_min": 50000,
    "orcamento_max": 100000,
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
print("TESTE - Top 3 Recomendações")
print("=" * 80)

response = requests.post(f"{API_URL}/recommend", json=profile, timeout=10)

if response.status_code == 200:
    data = response.json()
    total = data.get('total_recommendations', 0)
    
    print(f"\n✅ API respondeu com sucesso!")
    print(f"Total de recomendações: {total}")
    
    if total == 3:
        print("✅ Retornando exatamente 3 carros (correto!)")
    elif total < 3:
        print(f"⚠️ Retornando apenas {total} carros (menos que 3)")
    else:
        print(f"❌ Retornando {total} carros (deveria ser 3)")
    
    print("\n📋 Carros recomendados:")
    for i, rec in enumerate(data.get('recommendations', []), 1):
        car = rec.get('car', {})
        score = rec.get('match_percentage', 0)
        print(f"{i}. {car.get('nome')} - {score}% match")
        print(f"   Preço: R$ {car.get('preco'):,.2f}")
        print(f"   Ano: {car.get('ano')}")
        
        tco = rec.get('tco_breakdown')
        if tco:
            print(f"   TCO: R$ {tco.get('total_monthly'):,.2f}/mês")
        print()
else:
    print(f"❌ Erro: {response.status_code}")
    print(response.text)

print("=" * 80)
