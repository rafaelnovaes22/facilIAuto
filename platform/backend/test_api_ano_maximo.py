"""
Teste da API: Validar filtro de ano máximo via endpoint /recommend
"""

import requests
import json

# URL da API (ajustar se necessário)
API_URL = "http://localhost:8000"


def test_api_ano_maximo():
    """
    Testar endpoint /recommend com filtro de ano 2020-2020
    """
    print("\n" + "="*80)
    print("TESTE API: POST /recommend com ano 2020-2020")
    print("="*80)
    
    # Payload com filtro de ano
    payload = {
        "orcamento_min": 30000,
        "orcamento_max": 300000,
        "city": "São Paulo",
        "state": "SP",
        "uso_principal": "familia",
        "tamanho_familia": 4,
        "tem_criancas": False,
        "tem_idosos": False,
        "prioridades": {
            "economia": 3,
            "espaco": 4,
            "performance": 3,
            "conforto": 4,
            "seguranca": 5
        },
        "marcas_preferidas": [],
        "marcas_rejeitadas": [],
        "tipos_preferidos": [],
        "ano_minimo": 2020,
        "ano_maximo": 2020,  # 🔥 CRÍTICO: Apenas 2020
        "primeiro_carro": False
    }
    
    print("\nPayload enviado:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        # Fazer requisição
        response = requests.post(
            f"{API_URL}/recommend",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ ERRO: {response.text}")
            return False
        
        # Analisar resposta
        data = response.json()
        
        print(f"\nTotal de recomendações: {data['total_recommendations']}")
        print(f"Perfil: {data['profile_summary']}")
        
        # Verificar anos dos carros
        anos_encontrados = {}
        carros_invalidos = []
        
        for rec in data['recommendations']:
            car = rec['car']
            ano = car['ano']
            
            if ano not in anos_encontrados:
                anos_encontrados[ano] = 0
            anos_encontrados[ano] += 1
            
            if ano != 2020:
                carros_invalidos.append(car)
        
        print("\nDistribuição de anos:")
        for ano in sorted(anos_encontrados.keys()):
            status = "✅" if ano == 2020 else "❌"
            print(f"  {status} {ano}: {anos_encontrados[ano]} carros")
        
        if carros_invalidos:
            print(f"\n❌ ERRO: {len(carros_invalidos)} carros FORA da faixa 2020-2020:")
            for car in carros_invalidos[:5]:
                print(f"  - {car['nome']} ({car['ano']}) - R$ {car['preco']:,.2f}")
            return False
        else:
            print(f"\n✅ SUCESSO: Todos os {data['total_recommendations']} carros são de 2020")
            
            # Mostrar alguns exemplos
            print("\nExemplos de carros retornados:")
            for rec in data['recommendations'][:5]:
                car = rec['car']
                print(f"  - {car['nome']} ({car['ano']}) - R$ {car['preco']:,.2f} - Match: {rec['match_percentage']}%")
            
            return True
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar à API")
        print("Certifique-se de que a API está rodando:")
        print("  cd platform/backend")
        print("  python api/main.py")
        return False
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_health():
    """
    Testar se a API está online
    """
    print("\n" + "="*80)
    print("TESTE: Health Check")
    print("="*80)
    
    try:
        response = requests.get(f"{API_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ API Online")
            print(f"  - Status: {data['status']}")
            print(f"  - Concessionárias: {data['dealerships']}")
            print(f"  - Carros: {data['cars']}")
            return True
        else:
            print(f"\n❌ API retornou status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ API não está rodando")
        print("\nPara iniciar a API:")
        print("  cd platform/backend")
        print("  python api/main.py")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 TESTE DE API: Filtro de Ano Máximo")
    print("="*80)
    
    # Verificar se API está online
    if not test_api_health():
        print("\n⚠️  Inicie a API antes de executar os testes")
        exit(1)
    
    # Executar teste
    success = test_api_ano_maximo()
    
    print("\n" + "="*80)
    if success:
        print("✅ TESTE PASSOU: Filtro de ano máximo funcionando via API")
    else:
        print("❌ TESTE FALHOU: Investigar problema")
    print("="*80)
