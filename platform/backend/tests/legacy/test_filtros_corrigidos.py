"""
Testar filtros após correção dos dados
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.user_profile import UserProfile
from services.unified_recommendation_engine import UnifiedRecommendationEngine


def test_filtro_cambio_automatico():
    """Teste: Filtrar por câmbio automático"""
    print("\n" + "="*80)
    print("TESTE 1: Filtro de Câmbio Automático")
    print("="*80)
    
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=150000,
        uso_principal="familia",
        tamanho_familia=4,
        cambio_preferido="Automático"
    )
    
    print(f"\nFiltro aplicado: cambio_preferido = 'Automático'")
    
    recommendations = engine.recommend(profile, limit=50)
    
    print(f"\nResultados: {len(recommendations)} carros")
    
    if len(recommendations) == 0:
        print("\n❌ FALHOU: Nenhum carro encontrado")
        return False
    
    # Verificar se todos são automáticos
    for rec in recommendations:
        car = rec['car']
        if 'Automático' not in car.cambio:
            print(f"\n❌ FALHOU: {car.nome} tem câmbio {car.cambio}")
            return False
    
    print(f"\n✅ PASSOU: Todos os {len(recommendations)} carros são automáticos")
    print("\nExemplos:")
    for rec in recommendations[:5]:
        car = rec['car']
        print(f"  - {car.nome} ({car.ano}) - {car.cambio} - R$ {car.preco:,.2f}")
    
    return True


def test_filtro_cambio_manual():
    """Teste: Filtrar por câmbio manual"""
    print("\n" + "="*80)
    print("TESTE 2: Filtro de Câmbio Manual")
    print("="*80)
    
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    profile = UserProfile(
        orcamento_min=30000,
        orcamento_max=100000,
        uso_principal="trabalho",
        tamanho_familia=1,
        cambio_preferido="Manual"
    )
    
    print(f"\nFiltro aplicado: cambio_preferido = 'Manual'")
    
    recommendations = engine.recommend(profile, limit=50)
    
    print(f"\nResultados: {len(recommendations)} carros")
    
    if len(recommendations) == 0:
        print("\n❌ FALHOU: Nenhum carro encontrado")
        return False
    
    # Verificar se todos são manuais
    for rec in recommendations:
        car = rec['car']
        if car.cambio != 'Manual':
            print(f"\n❌ FALHOU: {car.nome} tem câmbio {car.cambio}")
            return False
    
    print(f"\n✅ PASSOU: Todos os {len(recommendations)} carros são manuais")
    print("\nExemplos:")
    for rec in recommendations[:5]:
        car = rec['car']
        print(f"  - {car.nome} ({car.ano}) - {car.cambio} - R$ {car.preco:,.2f}")
    
    return True


def test_filtro_km_maxima():
    """Teste: Filtrar por quilometragem máxima"""
    print("\n" + "="*80)
    print("TESTE 3: Filtro de Quilometragem Máxima (50.000 km)")
    print("="*80)
    
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=150000,
        uso_principal="familia",
        tamanho_familia=4,
        km_maxima=50000
    )
    
    print(f"\nFiltro aplicado: km_maxima = 50.000")
    
    recommendations = engine.recommend(profile, limit=50)
    
    print(f"\nResultados: {len(recommendations)} carros")
    
    if len(recommendations) == 0:
        print("\n⚠️  Nenhum carro encontrado (pode ser normal se todos têm mais de 50k km)")
        return True
    
    # Verificar se todos têm <= 50k km
    for rec in recommendations:
        car = rec['car']
        if car.quilometragem > 50000:
            print(f"\n❌ FALHOU: {car.nome} tem {car.quilometragem:,} km")
            return False
    
    print(f"\n✅ PASSOU: Todos os {len(recommendations)} carros têm <= 50.000 km")
    print("\nExemplos:")
    for rec in recommendations[:5]:
        car = rec['car']
        print(f"  - {car.nome} ({car.ano}) - {car.quilometragem:,} km - R$ {car.preco:,.2f}")
    
    return True


def test_filtro_combinado():
    """Teste: Filtros combinados (câmbio + km + ano)"""
    print("\n" + "="*80)
    print("TESTE 4: Filtros Combinados (Automático + <= 60k km + >= 2020)")
    print("="*80)
    
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=150000,
        uso_principal="familia",
        tamanho_familia=4,
        cambio_preferido="Automático",
        km_maxima=60000,
        ano_minimo=2020
    )
    
    print(f"\nFiltros aplicados:")
    print(f"  - cambio_preferido = 'Automático'")
    print(f"  - km_maxima = 60.000")
    print(f"  - ano_minimo = 2020")
    
    recommendations = engine.recommend(profile, limit=50)
    
    print(f"\nResultados: {len(recommendations)} carros")
    
    if len(recommendations) == 0:
        print("\n⚠️  Nenhum carro encontrado (filtros muito restritivos)")
        return True
    
    # Verificar se todos atendem aos critérios
    for rec in recommendations:
        car = rec['car']
        
        if 'Automático' not in car.cambio:
            print(f"\n❌ FALHOU: {car.nome} tem câmbio {car.cambio}")
            return False
        
        if car.quilometragem > 60000:
            print(f"\n❌ FALHOU: {car.nome} tem {car.quilometragem:,} km")
            return False
        
        if car.ano < 2020:
            print(f"\n❌ FALHOU: {car.nome} é de {car.ano}")
            return False
    
    print(f"\n✅ PASSOU: Todos os {len(recommendations)} carros atendem aos critérios")
    print("\nExemplos:")
    for rec in recommendations[:5]:
        car = rec['car']
        print(f"  - {car.nome} ({car.ano}) - {car.cambio} - {car.quilometragem:,} km - R$ {car.preco:,.2f}")
    
    return True


def test_distribuicao_geral():
    """Teste: Verificar distribuição geral dos dados"""
    print("\n" + "="*80)
    print("TESTE 5: Distribuição Geral dos Dados")
    print("="*80)
    
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    # Contar câmbios
    cambios = {}
    for car in engine.all_cars:
        cambio = car.cambio
        cambios[cambio] = cambios.get(cambio, 0) + 1
    
    print("\nDistribuição de Câmbios:")
    for cambio, count in sorted(cambios.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(engine.all_cars)) * 100
        print(f"  {cambio}: {count} carros ({percentage:.1f}%)")
    
    # Contar quilometragem
    km_ranges = {
        '0 km': 0,
        '1-30k': 0,
        '30-60k': 0,
        '60-100k': 0,
        '> 100k': 0
    }
    
    for car in engine.all_cars:
        km = car.quilometragem
        if km == 0:
            km_ranges['0 km'] += 1
        elif km <= 30000:
            km_ranges['1-30k'] += 1
        elif km <= 60000:
            km_ranges['30-60k'] += 1
        elif km <= 100000:
            km_ranges['60-100k'] += 1
        else:
            km_ranges['> 100k'] += 1
    
    print("\nDistribuição de Quilometragem:")
    for range_name, count in km_ranges.items():
        percentage = (count / len(engine.all_cars)) * 100
        print(f"  {range_name}: {count} carros ({percentage:.1f}%)")
    
    # Verificar se há diversidade
    if len(cambios) < 2:
        print("\n⚠️  Pouca diversidade de câmbios")
        return False
    
    if cambios.get('Manual', 0) == len(engine.all_cars):
        print("\n❌ FALHOU: Todos os carros são manuais")
        return False
    
    if km_ranges['0 km'] == len(engine.all_cars):
        print("\n❌ FALHOU: Todos os carros têm 0 km")
        return False
    
    print("\n✅ PASSOU: Dados têm boa diversidade")
    return True


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 TESTES DE FILTROS APÓS CORREÇÃO DOS DADOS")
    print("="*80)
    
    tests = [
        ("Filtro Câmbio Automático", test_filtro_cambio_automatico),
        ("Filtro Câmbio Manual", test_filtro_cambio_manual),
        ("Filtro Quilometragem", test_filtro_km_maxima),
        ("Filtros Combinados", test_filtro_combinado),
        ("Distribuição Geral", test_distribuicao_geral),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ ERRO no teste {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {name}")
    
    print("\n" + "="*80)
    print(f"Resultado: {passed}/{total} testes passaram ({passed/total*100:.0f}%)")
    print("="*80)
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Dados corrigidos com sucesso!")
        print("✅ Filtros funcionando perfeitamente!")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
        print("Revisar correções necessárias")
