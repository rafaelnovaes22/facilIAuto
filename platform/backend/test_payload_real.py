"""
Teste com o payload REAL enviado pelo frontend
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.user_profile import UserProfile
from services.unified_recommendation_engine import UnifiedRecommendationEngine


def test_payload_real():
    """
    Testar com o payload EXATO enviado pelo frontend
    """
    print("\n" + "="*80)
    print("TESTE: Payload Real do Frontend")
    print("="*80)
    
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
    
    print("\nPayload recebido:")
    print(f"  - Orçamento: R$ {payload['orcamento_min']:,.2f} - R$ {payload['orcamento_max']:,.2f}")
    print(f"  - Ano: {payload['ano_minimo']} a {payload['ano_maximo']}")
    print(f"  - Uso: {payload['uso_principal']}")
    
    # Criar perfil
    profile = UserProfile(**payload)
    
    print(f"\nPerfil criado:")
    print(f"  - ano_minimo: {profile.ano_minimo}")
    print(f"  - ano_maximo: {profile.ano_maximo}")
    
    # Criar engine
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    print(f"\nTotal de carros no sistema: {len(engine.all_cars)}")
    
    # Gerar recomendações
    print("\n" + "-"*80)
    print("APLICANDO FILTROS:")
    print("-"*80)
    
    recommendations = engine.recommend(profile, limit=50)
    
    print("\n" + "="*80)
    print(f"RESULTADOS: {len(recommendations)} carros")
    print("="*80)
    
    if not recommendations:
        print("\n⚠️  Nenhum carro encontrado com esses critérios")
        return
    
    # Analisar anos
    anos_encontrados = {}
    carros_invalidos = []
    
    for rec in recommendations:
        car = rec['car']
        ano = car.ano
        
        if ano not in anos_encontrados:
            anos_encontrados[ano] = []
        anos_encontrados[ano].append(car)
        
        if ano < 2020 or ano > 2020:
            carros_invalidos.append(car)
    
    # Mostrar distribuição
    print("\nDistribuição de anos:")
    for ano in sorted(anos_encontrados.keys()):
        carros = anos_encontrados[ano]
        status = "✅" if ano == 2020 else "❌"
        print(f"  {status} {ano}: {len(carros)} carros")
        
        # Mostrar alguns exemplos
        for car in carros[:3]:
            print(f"      - {car.nome} - R$ {car.preco:,.2f}")
    
    # Verificar se há carros inválidos
    if carros_invalidos:
        print(f"\n{'='*80}")
        print(f"❌ PROBLEMA ENCONTRADO: {len(carros_invalidos)} carros FORA da faixa 2020-2020")
        print(f"{'='*80}")
        
        print("\nCarros inválidos (primeiros 10):")
        for car in carros_invalidos[:10]:
            print(f"  ❌ {car.nome} ({car.ano}) - R$ {car.preco:,.2f}")
            print(f"      Concessionária: {car.dealership_name}")
            print(f"      ID: {car.id}")
        
        # Verificar se o filtro foi aplicado
        print("\n" + "="*80)
        print("DIAGNÓSTICO:")
        print("="*80)
        print("O filtro de ano NÃO está sendo aplicado corretamente!")
        print("Possíveis causas:")
        print("  1. Bug no método filter_by_year()")
        print("  2. Filtro sendo ignorado em algum ponto")
        print("  3. Carros sendo adicionados após o filtro")
        
        return False
    else:
        print(f"\n{'='*80}")
        print(f"✅ SUCESSO: Todos os {len(recommendations)} carros são de 2020")
        print(f"{'='*80}")
        
        print("\nExemplos de carros retornados:")
        for rec in recommendations[:5]:
            car = rec['car']
            print(f"  ✅ {car.nome} ({car.ano}) - R$ {car.preco:,.2f} - Match: {rec['match_percentage']}%")
        
        return True


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 TESTE COM PAYLOAD REAL DO FRONTEND")
    print("="*80)
    
    success = test_payload_real()
    
    print("\n" + "="*80)
    if success:
        print("✅ TESTE PASSOU: Filtro funcionando corretamente")
    else:
        print("❌ TESTE FALHOU: Bug encontrado no filtro")
    print("="*80)
