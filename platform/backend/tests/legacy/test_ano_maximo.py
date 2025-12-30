"""
Teste específico para validar filtro de ano máximo
🔥 Bug Report: Filtro de ano máximo não está funcionando
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.user_profile import UserProfile
from services.unified_recommendation_engine import UnifiedRecommendationEngine


def test_ano_maximo_2020():
    """
    Teste: Filtrar carros de 2020 a 2020 (apenas 2020)
    Bug: Retorna carros acima de 2020
    """
    print("\n" + "="*80)
    print("TESTE: Filtro Ano Máximo 2020")
    print("="*80)
    
    # Criar engine com dados reais
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    print(f"\nTotal de carros no sistema: {len(engine.all_cars)}")
    
    # Criar perfil com ano 2020 a 2020
    profile = UserProfile(
        orcamento_min=30000,
        orcamento_max=300000,
        uso_principal="familia",
        tamanho_familia=4,
        ano_minimo=2020,
        ano_maximo=2020  # 🔥 CRÍTICO: Apenas 2020
    )
    
    print(f"\nFiltros aplicados:")
    print(f"  - Orçamento: R$ {profile.orcamento_min:,.2f} - R$ {profile.orcamento_max:,.2f}")
    print(f"  - Ano: {profile.ano_minimo} a {profile.ano_maximo}")
    
    # Gerar recomendações
    recommendations = engine.recommend(profile, limit=50)
    
    print(f"\n{'='*80}")
    print(f"Resultados: {len(recommendations)} carros")
    print(f"{'='*80}\n")
    
    # Verificar anos
    anos_encontrados = {}
    carros_invalidos = []
    
    for rec in recommendations:
        car = rec['car']
        ano = car.ano
        
        if ano not in anos_encontrados:
            anos_encontrados[ano] = 0
        anos_encontrados[ano] += 1
        
        # Verificar se está fora da faixa
        if ano < 2020 or ano > 2020:
            carros_invalidos.append(car)
    
    # Mostrar distribuição de anos
    print("Distribuição de anos nos resultados:")
    for ano in sorted(anos_encontrados.keys()):
        status = "✅" if ano == 2020 else "❌"
        print(f"  {status} {ano}: {anos_encontrados[ano]} carros")
    
    # Mostrar carros inválidos
    if carros_invalidos:
        print(f"\n❌ ERRO: {len(carros_invalidos)} carros FORA da faixa 2020-2020:")
        for car in carros_invalidos[:10]:  # Mostrar apenas os primeiros 10
            print(f"  - {car.nome} ({car.ano}) - R$ {car.preco:,.2f}")
        if len(carros_invalidos) > 10:
            print(f"  ... e mais {len(carros_invalidos) - 10} carros")
        
        print(f"\n{'='*80}")
        print("❌ TESTE FALHOU: Filtro de ano máximo não está funcionando")
        print(f"{'='*80}")
        return False
    else:
        print(f"\n{'='*80}")
        print("✅ TESTE PASSOU: Todos os carros são de 2020")
        print(f"{'='*80}")
        return True


def test_filtro_direto():
    """
    Teste direto do método filter_by_year
    """
    print("\n" + "="*80)
    print("TESTE DIRETO: Método filter_by_year()")
    print("="*80)
    
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    print(f"\nTotal de carros: {len(engine.all_cars)}")
    
    # Aplicar filtro de ano diretamente
    filtered = engine.filter_by_year(engine.all_cars, ano_minimo=2020, ano_maximo=2020)
    
    print(f"Carros após filtro 2020-2020: {len(filtered)}")
    
    # Verificar anos
    anos_invalidos = [car for car in filtered if car.ano != 2020]
    
    if anos_invalidos:
        print(f"\n❌ ERRO: {len(anos_invalidos)} carros com ano diferente de 2020:")
        for car in anos_invalidos[:5]:
            print(f"  - {car.nome} ({car.ano})")
        return False
    else:
        print(f"\n✅ Todos os {len(filtered)} carros são de 2020")
        
        # Mostrar alguns exemplos
        print("\nExemplos de carros 2020:")
        for car in filtered[:5]:
            print(f"  - {car.nome} ({car.ano}) - R$ {car.preco:,.2f}")
        
        return True


def test_filtro_orçamento_e_ano():
    """
    Teste combinado: orçamento + ano
    """
    print("\n" + "="*80)
    print("TESTE COMBINADO: Orçamento + Ano 2020")
    print("="*80)
    
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    # Primeiro filtrar por orçamento
    profile = UserProfile(
        orcamento_min=30000,
        orcamento_max=300000,
        uso_principal="familia",
        tamanho_familia=4
    )
    
    filtered_budget = engine.filter_by_budget(engine.all_cars, profile)
    print(f"\nApós filtro de orçamento: {len(filtered_budget)} carros")
    
    # Depois filtrar por ano
    filtered_year = engine.filter_by_year(filtered_budget, ano_minimo=2020, ano_maximo=2020)
    print(f"Após filtro de ano 2020: {len(filtered_year)} carros")
    
    # Verificar
    anos_invalidos = [car for car in filtered_year if car.ano != 2020]
    
    if anos_invalidos:
        print(f"\n❌ ERRO: {len(anos_invalidos)} carros com ano diferente de 2020")
        return False
    else:
        print(f"\n✅ Todos os carros são de 2020")
        return True


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 DIAGNÓSTICO: Filtro de Ano Máximo")
    print("="*80)
    
    # Executar testes
    test1 = test_filtro_direto()
    test2 = test_filtro_orçamento_e_ano()
    test3 = test_ano_maximo_2020()
    
    print("\n" + "="*80)
    print("RESUMO DOS TESTES")
    print("="*80)
    print(f"Teste 1 (Filtro Direto): {'✅ PASSOU' if test1 else '❌ FALHOU'}")
    print(f"Teste 2 (Orçamento + Ano): {'✅ PASSOU' if test2 else '❌ FALHOU'}")
    print(f"Teste 3 (Recommend Completo): {'✅ PASSOU' if test3 else '❌ FALHOU'}")
    print("="*80)
    
    if test1 and test2 and test3:
        print("\n✅ TODOS OS TESTES PASSARAM - Filtro está funcionando corretamente")
        sys.exit(0)
    else:
        print("\n❌ ALGUNS TESTES FALHARAM - Investigar problema")
        sys.exit(1)
