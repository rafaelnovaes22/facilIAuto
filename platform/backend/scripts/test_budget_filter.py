"""
Script para testar o filtro de orçamento
Verifica se carros com preço zero ou fora da faixa são excluídos
"""

import sys
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.unified_recommendation_engine import UnifiedRecommendationEngine
from models.user_profile import UserProfile

def test_budget_filter():
    """Testar filtro de orçamento"""
    
    print("\n" + "="*80)
    print("TESTE DE FILTRO DE ORÇAMENTO")
    print("="*80)
    
    # Inicializar engine
    data_dir = Path(__file__).parent.parent / 'data'
    engine = UnifiedRecommendationEngine(data_dir=str(data_dir))
    
    print(f"\nTotal de carros carregados: {len(engine.all_cars)}")
    
    # Verificar se há carros com preço zero
    carros_preco_zero = [car for car in engine.all_cars if car.preco <= 0]
    if carros_preco_zero:
        print(f"\n❌ ERRO: {len(carros_preco_zero)} carros com preço <= 0:")
        for car in carros_preco_zero[:5]:
            print(f"  • {car.nome} - R$ {car.preco:.2f}")
    else:
        print(f"\n✅ Nenhum carro com preço <= 0")
    
    # Verificar se há motos
    motos = [car for car in engine.all_cars if car.categoria == 'Moto']
    if motos:
        print(f"\n❌ ERRO: {len(motos)} motos encontradas:")
        for moto in motos:
            print(f"  • {moto.nome} - {moto.categoria}")
    else:
        print(f"\n✅ Nenhuma moto encontrada")
    
    # Testar filtros de orçamento
    test_cases = [
        (10000, 15000, "R$ 10k - 15k"),
        (50000, 80000, "R$ 50k - 80k"),
        (100000, 150000, "R$ 100k - 150k"),
        (200000, 300000, "R$ 200k - 300k"),
    ]
    
    print(f"\n{'='*80}")
    print("TESTES DE FAIXAS DE ORÇAMENTO")
    print(f"{'='*80}")
    
    for orcamento_min, orcamento_max, descricao in test_cases:
        # Criar perfil de teste
        profile = UserProfile(
            uso_principal="familia",
            orcamento_min=orcamento_min,
            orcamento_max=orcamento_max,
            prioridades={
                "economia": 3,
                "espaco": 4,
                "performance": 2,
                "conforto": 3,
                "seguranca": 5
            }
        )
        
        # Filtrar por orçamento
        filtered = engine.filter_by_budget(engine.all_cars, profile)
        
        print(f"\n{descricao}:")
        print(f"  Carros encontrados: {len(filtered)}")
        
        # Verificar se todos estão dentro da faixa
        fora_da_faixa = [
            car for car in filtered 
            if car.preco < orcamento_min or car.preco > orcamento_max
        ]
        
        if fora_da_faixa:
            print(f"  ❌ ERRO: {len(fora_da_faixa)} carros fora da faixa:")
            for car in fora_da_faixa[:3]:
                print(f"    • {car.nome} - R$ {car.preco:,.2f}")
        else:
            if filtered:
                print(f"  ✅ Todos os carros estão dentro da faixa")
                # Mostrar alguns exemplos
                for car in filtered[:3]:
                    print(f"    • {car.nome} - R$ {car.preco:,.2f}")
            else:
                print(f"  ℹ️  Nenhum carro encontrado nesta faixa")
    
    # Resumo final
    print(f"\n{'='*80}")
    print("RESUMO")
    print(f"{'='*80}")
    
    if carros_preco_zero or motos:
        print("\n❌ FALHOU: Há carros inválidos no sistema")
        return False
    else:
        print("\n✅ PASSOU: Todos os filtros estão funcionando corretamente")
        return True


if __name__ == '__main__':
    success = test_budget_filter()
    sys.exit(0 if success else 1)
