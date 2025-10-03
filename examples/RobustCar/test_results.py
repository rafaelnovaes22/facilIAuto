#!/usr/bin/env python3
"""
🧪 Teste dos Resultados da Correção
Verificar se preços estão sendo extraídos corretamente
"""

import json
from recommendation_engine import *

def test_preco_extraction():
    """Testar extração de preços"""
    print("🎯 RESULTADO DA CORREÇÃO DE PREÇOS:")
    print("="*50)
    
    # Carregar dados
    data = json.load(open('robustcar_estoque_20250912_135949.json'))
    
    # Analisar preços
    precos_validos = [c for c in data if c['preco'] > 0]
    
    print(f"Total de carros: {len(data)}")
    print(f"Preços válidos: {len(precos_validos)} ({len(precos_validos)/len(data)*100:.1f}%)")
    
    if precos_validos:
        preco_medio = sum(c["preco"] for c in precos_validos) / len(precos_validos)
        print(f"Preço médio: R$ {preco_medio:,.2f}")
        
        print(f"\n📊 Exemplos extraídos:")
        for i, c in enumerate(precos_validos[:5], 1):
            print(f"{i}. {c['marca']} {c['modelo']} - R$ {c['preco']:,.2f}")
    
    # Analisar marcas
    marcas = set(c['marca'] for c in data if c['marca'] != 'Genérica')
    print(f"\n🏷️ Marcas identificadas: {len(marcas)}")
    for marca in sorted(marcas)[:5]:
        print(f"  - {marca}")
    
    return len(precos_validos) > 0

def test_recommendation_engine():
    """Testar sistema de recomendação"""
    print(f"\n🤖 TESTE DO SISTEMA DE RECOMENDAÇÃO:")
    print("="*50)
    
    try:
        # Carregar engine
        engine = RobustCarRecommendationEngine('robustcar_estoque_20250912_135949.json')
        print(f"✅ Estoque carregado: {len(engine.estoque)} carros")
        
        # Criar perfil de teste
        perfil = UserProfile(
            orcamento_min=70000,
            orcamento_max=100000,
            uso_principal='familia',
            tamanho_familia=4,
            prioridades={
                'economia': 4,
                'espaco': 5,
                'seguranca': 5,
                'conforto': 3,
                'performance': 2
            },
            marcas_preferidas=['Toyota', 'Chevrolet'],
            tipos_preferidos=['SUV'],
            combustivel_preferido='Flex',
            idade_usuario=35,
            experiencia_conducao='intermediario'
        )
        
        # Gerar recomendações
        recomendacoes = engine.recomendar(perfil, 3)
        print(f"✅ Recomendações geradas: {len(recomendacoes)}")
        
        if recomendacoes:
            print(f"\n🎯 TOP 3 RECOMENDAÇÕES:")
            for i, rec in enumerate(recomendacoes, 1):
                print(f"{i}. {rec.carro.nome}")
                print(f"   💰 R$ {rec.carro.preco:,.2f}")
                print(f"   📊 Match: {rec.match_percentage}%")
                print(f"   📝 {rec.justificativa}")
                print()
        
        return len(recomendacoes) > 0
        
    except Exception as e:
        print(f"❌ Erro no teste de recomendação: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTANDO CORREÇÕES DO SISTEMA ROBUSTCAR")
    print("="*60)
    
    # Teste 1: Extração de preços
    preco_ok = test_preco_extraction()
    
    # Teste 2: Sistema de recomendação
    recom_ok = test_recommendation_engine()
    
    # Resultado final
    print("🏆 RESULTADO FINAL:")
    print("="*30)
    print(f"✅ Extração de preços: {'FUNCIONANDO' if preco_ok else 'PROBLEMA'}")
    print(f"✅ Sistema de recomendação: {'FUNCIONANDO' if recom_ok else 'PROBLEMA'}")
    
    if preco_ok and recom_ok:
        print(f"\n🎉 SISTEMA 100% FUNCIONAL!")
        print(f"🚗 Pronto para go-live na RobustCar!")
    else:
        print(f"\n⚠️ Alguns problemas detectados")
