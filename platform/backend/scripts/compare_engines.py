"""
📊 Data Analyst: Comparação de Engines

Compara engine original vs otimizado para medir impacto

Autor: Data Analyst + AI Engineer
Data: Outubro 2024
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.unified_recommendation_engine import UnifiedRecommendationEngine
from services.optimized_recommendation_engine import OptimizedRecommendationEngine
from models.user_profile import UserProfile
import time
import statistics


def create_test_profile() -> UserProfile:
    """Perfil de teste padrão"""
    return UserProfile(
        orcamento_min=50000,
        orcamento_max=80000,
        uso_principal="familia",
        tamanho_familia=4,
        tem_criancas=True,
        city="São Paulo",
        state="SP",
        priorizar_proximas=True,
        prioridades={
            "economia": 4,
            "espaco": 5,
            "performance": 2,
            "conforto": 4,
            "seguranca": 5
        },
        marcas_preferidas=["Toyota", "Honda"],
        primeiro_carro=False
    )


def compare_engines():
    """Comparar engines"""
    
    print("="*60)
    print("📊 COMPARAÇÃO: Engine Original vs Otimizado")
    print("="*60)
    
    # Carregar engines
    print("\nCarregando engines...")
    original = UnifiedRecommendationEngine()
    optimized = OptimizedRecommendationEngine()
    
    print(f"✅ Original carregado: {len(original.all_cars)} carros")
    print(f"✅ Otimizado carregado: {len(optimized.all_cars)} carros")
    
    # Perfil de teste
    profile = create_test_profile()
    
    print("\n" + "="*60)
    print("👤 PERFIL DE TESTE")
    print("="*60)
    print(f"Orçamento: R$ {profile.orcamento_min:,} - R$ {profile.orcamento_max:,}")
    print(f"Uso: {profile.uso_principal}")
    print(f"Família: {profile.tamanho_familia} pessoas")
    print(f"Crianças: {'Sim' if profile.tem_criancas else 'Não'}")
    print(f"Localização: {profile.city}, {profile.state}")
    print(f"Prioridades: {profile.prioridades}")
    
    # Executar recomendações
    print("\n" + "="*60)
    print("⚡ PERFORMANCE")
    print("="*60)
    
    # Original
    start = time.time()
    original_results = original.recommend(profile, limit=20)
    original_time = time.time() - start
    
    # Otimizado
    start = time.time()
    optimized_results = optimized.recommend(profile, limit=20)
    optimized_time = time.time() - start
    
    print(f"Original:   {original_time*1000:.2f}ms  ({len(original_results)} resultados)")
    print(f"Otimizado:  {optimized_time*1000:.2f}ms  ({len(optimized_results)} resultados)")
    
    speedup = original_time / optimized_time if optimized_time > 0 else 1
    print(f"\nSpeedup: {speedup:.2f}x ", end="")
    if speedup > 1:
        print("✅ MAIS RÁPIDO")
    elif speedup < 1:
        print("⚠️ MAIS LENTO")
    else:
        print("➖ IGUAL")
    
    # Scores
    print("\n" + "="*60)
    print("📈 QUALIDADE DOS SCORES")
    print("="*60)
    
    original_scores = [r['score'] for r in original_results]
    optimized_scores = [r['score'] for r in optimized_results]
    
    print(f"\nOriginal:")
    print(f"  Média:   {statistics.mean(original_scores):.3f} ({int(statistics.mean(original_scores)*100)}%)")
    print(f"  Mediana: {statistics.median(original_scores):.3f}")
    print(f"  Min/Max: {min(original_scores):.3f} / {max(original_scores):.3f}")
    
    print(f"\nOtimizado:")
    print(f"  Média:   {statistics.mean(optimized_scores):.3f} ({int(statistics.mean(optimized_scores)*100)}%)")
    print(f"  Mediana: {statistics.median(optimized_scores):.3f}")
    print(f"  Min/Max: {min(optimized_scores):.3f} / {max(optimized_scores):.3f}")
    
    score_improvement = (statistics.mean(optimized_scores) - statistics.mean(original_scores)) / statistics.mean(original_scores) * 100
    print(f"\n🎯 Melhoria no score médio: {score_improvement:+.1f}%")
    
    # Diversidade
    print("\n" + "="*60)
    print("🎨 DIVERSIDADE")
    print("="*60)
    
    def analyze_diversity(results):
        brands = [r['car'].marca for r in results]
        categories = [r['car'].categoria for r in results]
        dealers = [r['car'].dealership_id for r in results]
        
        return {
            'unique_brands': len(set(brands)),
            'unique_categories': len(set(categories)),
            'unique_dealers': len(set(dealers)),
            'most_common_brand': max(set(brands), key=brands.count) if brands else "N/A",
            'most_common_brand_pct': brands.count(max(set(brands), key=brands.count)) / len(brands) * 100 if brands else 0
        }
    
    orig_div = analyze_diversity(original_results)
    opt_div = analyze_diversity(optimized_results)
    
    print(f"\nOriginal:")
    print(f"  Marcas únicas:      {orig_div['unique_brands']}")
    print(f"  Categorias únicas:  {orig_div['unique_categories']}")
    print(f"  Concessionárias:    {orig_div['unique_dealers']}")
    print(f"  Marca dominante:    {orig_div['most_common_brand']} ({orig_div['most_common_brand_pct']:.0f}%)")
    
    print(f"\nOtimizado:")
    print(f"  Marcas únicas:      {opt_div['unique_brands']}")
    print(f"  Categorias únicas:  {opt_div['unique_categories']}")
    print(f"  Concessionárias:    {opt_div['unique_dealers']}")
    print(f"  Marca dominante:    {opt_div['most_common_brand']} ({opt_div['most_common_brand_pct']:.0f}%)")
    
    # Top 5 resultados
    print("\n" + "="*60)
    print("🏆 TOP 5 RESULTADOS - ORIGINAL")
    print("="*60)
    for i, rec in enumerate(original_results[:5], 1):
        car = rec['car']
        print(f"\n{i}. {car.marca} {car.modelo} - R$ {car.preco:,}")
        print(f"   Score: {rec['score']:.3f} ({rec['match_percentage']}%)")
        print(f"   {rec['justificativa']}")
    
    print("\n" + "="*60)
    print("🏆 TOP 5 RESULTADOS - OTIMIZADO")
    print("="*60)
    for i, rec in enumerate(optimized_results[:5], 1):
        car = rec['car']
        print(f"\n{i}. {car.marca} {car.modelo} - R$ {car.preco:,}")
        print(f"   Score: {rec['score']:.3f} ({rec['match_percentage']}%)")
        print(f"   Boost: {rec.get('location_boost', 1.0):.2f}x | Penalties: {rec.get('penalties', 0.0):.3f}")
        print(f"   {rec['justificativa']}")
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO FINAL")
    print("="*60)
    
    improvements = []
    
    if speedup > 1:
        improvements.append(f"✅ {speedup:.1f}x mais rápido")
    
    if score_improvement > 0:
        improvements.append(f"✅ +{score_improvement:.1f}% no score médio")
    
    if opt_div['unique_brands'] > orig_div['unique_brands']:
        improvements.append(f"✅ +{opt_div['unique_brands'] - orig_div['unique_brands']} marcas únicas")
    
    if opt_div['most_common_brand_pct'] < orig_div['most_common_brand_pct']:
        improvements.append(f"✅ Melhor balanceamento (marca dominante {opt_div['most_common_brand_pct']:.0f}% vs {orig_div['most_common_brand_pct']:.0f}%)")
    
    if improvements:
        print("\n🎉 MELHORIAS:")
        for imp in improvements:
            print(f"   {imp}")
    else:
        print("\n⚠️ Nenhuma melhoria significativa detectada")
    
    print("\n" + "="*60)
    print("✅ Comparação completa!")
    print("="*60)


if __name__ == "__main__":
    compare_engines()

