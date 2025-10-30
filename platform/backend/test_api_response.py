"""
Capturar a resposta REAL da API e analisar
"""

import requests
import json

API_URL = "http://localhost:8000"

# Payload EXATO do frontend
payload = {
    "orcamento_min": 50000,
    "orcamento_max": 100000,
    "priorizar_proximas": False,
    "uso_principal": "familia",
    "ano_maximo": 2020,
    "ano_minimo": 2020,
    "frequencia_uso": "diaria",
    "marcas_preferidas": [],
    "marcas_rejeitadas": [],
    "necessita_espaco": False,
    "primeiro_carro": False,
    "prioridades": {
        "economia": 3,
        "espaco": 3,
        "performance": 3,
        "conforto": 3,
        "seguranca": 3
    },
    "tamanho_familia": 1,
    "tem_criancas": False,
    "tem_idosos": False,
    "tipos_preferidos": []
}

print("\n" + "="*80)
print("🔍 CAPTURANDO RESPOSTA REAL DA API")
print("="*80)

print("\nPayload enviado:")
print(json.dumps(payload, indent=2))

try:
    response = requests.post(
        f"{API_URL}/recommend",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\nTotal de recomendações: {data['total_recommendations']}")
        
        print("\n" + "="*80)
        print("CARROS RETORNADOS PELA API:")
        print("="*80)
        
        anos_encontrados = {}
        carros_invalidos = []
        
        for i, rec in enumerate(data['recommendations'], 1):
            car = rec['car']
            ano = car['ano']
            
            if ano not in anos_encontrados:
                anos_encontrados[ano] = []
            anos_encontrados[ano].append(car)
            
            status = "✅" if ano == 2020 else "❌"
            print(f"\n{i}. {status} {car['nome']}")
            print(f"   Ano: {ano}")
            print(f"   Preço: R$ {car['preco']:,.2f}")
            print(f"   Match: {rec['match_percentage']}%")
            
            if ano != 2020:
                carros_invalidos.append(car)
        
        print("\n" + "="*80)
        print("RESUMO:")
        print("="*80)
        
        for ano in sorted(anos_encontrados.keys()):
            carros = anos_encontrados[ano]
            status = "✅" if ano == 2020 else "❌"
            print(f"{status} {ano}: {len(carros)} carros")
        
        if carros_invalidos:
            print(f"\n❌ PROBLEMA: {len(carros_invalidos)} carros FORA da faixa 2020-2020")
            print("\nCarros inválidos:")
            for car in carros_invalidos:
                print(f"  - {car['nome']} ({car['ano']})")
            
            print("\n" + "="*80)
            print("🐛 BUG CONFIRMADO NA API!")
            print("="*80)
        else:
            print(f"\n✅ Todos os carros são de 2020")
            
    else:
        print(f"❌ Erro: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ API não está rodando")
    print("Inicie com: python api/main.py")
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
