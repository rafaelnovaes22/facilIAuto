"""
📊 Data Analyst: Script de Análise de Métricas

Analisa dados do sistema e gera relatório de performance

Autor: Data Analyst  
Data: Outubro 2024
"""

import json
import os
from collections import Counter, defaultdict
from typing import Dict, List
import statistics


def load_all_cars(data_dir: str) -> List[Dict]:
    """Carrega todos os carros de todas as concessionárias"""
    all_cars = []
    
    dealership_files = [
        'robustcar_cars.json',
        'autocenter_cars.json',
        'carplus_cars.json',
    ]
    
    for filename in dealership_files:
        file_path = os.path.join(data_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                cars = json.load(f)
                all_cars.extend(cars)
    
    return all_cars


def analyze_inventory(cars: List[Dict]) -> Dict:
    """Análise completa do inventário"""
    
    # Contadores
    categories = Counter([car.get('categoria', 'N/A') for car in cars])
    brands = Counter([car.get('marca', 'N/A') for car in cars])
    dealerships = Counter([car.get('dealership_id', 'N/A') for car in cars])
    
    # Preços
    prices = [car.get('preco', 0) for car in cars]
    
    # Scores médios
    avg_scores = {
        'familia': statistics.mean([car.get('score_familia', 0.5) for car in cars]),
        'economia': statistics.mean([car.get('score_economia', 0.5) for car in cars]),
        'performance': statistics.mean([car.get('score_performance', 0.5) for car in cars]),
        'conforto': statistics.mean([car.get('score_conforto', 0.5) for car in cars]),
        'seguranca': statistics.mean([car.get('score_seguranca', 0.5) for car in cars]),
    }
    
    # Faixas de preço
    price_ranges = {
        '< 50k': len([p for p in prices if p < 50000]),
        '50-70k': len([p for p in prices if 50000 <= p < 70000]),
        '70-90k': len([p for p in prices if 70000 <= p < 90000]),
        '90-110k': len([p for p in prices if 90000 <= p < 110000]),
        '> 110k': len([p for p in prices if p >= 110000]),
    }
    
    return {
        'total_cars': len(cars),
        'categories': dict(categories),
        'brands': dict(brands),
        'dealerships': dict(dealerships),
        'price_stats': {
            'min': min(prices) if prices else 0,
            'max': max(prices) if prices else 0,
            'avg': statistics.mean(prices) if prices else 0,
            'median': statistics.median(prices) if prices else 0,
        },
        'price_ranges': price_ranges,
        'avg_scores': avg_scores,
    }


def calculate_diversity_score(analysis: Dict) -> float:
    """
    Calcula score de diversidade (0-1)
    1.0 = perfeitamente diverso
    0.0 = sem diversidade
    """
    categories = analysis['categories']
    brands = analysis['brands']
    total = analysis['total_cars']
    
    if total == 0:
        return 0.0
    
    # Diversidade de categorias (ideal: 5 categorias balanceadas)
    cat_diversity = len(categories) / 5.0  # 5 categorias ideais
    
    # Diversidade de marcas (ideal: 10+ marcas)
    brand_diversity = min(1.0, len(brands) / 10.0)
    
    # Balanceamento (nenhuma marca deve ter > 30%)
    max_brand_pct = max(brands.values()) / total
    balance_score = 1.0 - max(0, (max_brand_pct - 0.30) * 2)  # Penaliza > 30%
    
    # Score combinado
    diversity_score = (cat_diversity * 0.4 + 
                      brand_diversity * 0.3 + 
                      balance_score * 0.3)
    
    return round(diversity_score, 2)


def print_report(analysis: Dict, diversity: float):
    """Imprime relatório formatado"""
    
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE ANÁLISE - FacilIAuto")
    print("="*60)
    
    # Overview
    print(f"\n📦 INVENTÁRIO")
    print(f"   Total de Carros: {analysis['total_cars']}")
    print(f"   Concessionárias: {len(analysis['dealerships'])}")
    print(f"   Diversidade: {diversity*100:.0f}% ", end="")
    
    if diversity >= 0.7:
        print("✅ EXCELENTE")
    elif diversity >= 0.5:
        print("⚠️ BOM")
    else:
        print("❌ PRECISA MELHORAR")
    
    # Categorias
    print(f"\n📊 CATEGORIAS")
    for cat, count in sorted(analysis['categories'].items(), 
                             key=lambda x: x[1], reverse=True):
        pct = count / analysis['total_cars'] * 100
        bar = "█" * int(pct / 5)  # Barra visual
        print(f"   {cat:12} {count:3} ({pct:5.1f}%) {bar}")
    
    # Top Marcas
    print(f"\n🏷️  TOP 5 MARCAS")
    top_brands = sorted(analysis['brands'].items(), 
                       key=lambda x: x[1], reverse=True)[:5]
    for brand, count in top_brands:
        pct = count / analysis['total_cars'] * 100
        bar = "█" * int(pct / 5)
        print(f"   {brand:15} {count:3} ({pct:5.1f}%) {bar}")
    
    # Preços
    stats = analysis['price_stats']
    print(f"\n💰 PREÇOS")
    print(f"   Mínimo:  R$ {stats['min']:,.0f}")
    print(f"   Médio:   R$ {stats['avg']:,.0f}")
    print(f"   Mediana: R$ {stats['median']:,.0f}")
    print(f"   Máximo:  R$ {stats['max']:,.0f}")
    
    # Faixas de preço
    print(f"\n📈 DISTRIBUIÇÃO POR FAIXA")
    total = analysis['total_cars']
    for range_name, count in analysis['price_ranges'].items():
        pct = count / total * 100 if total > 0 else 0
        bar = "█" * int(pct / 5)
        print(f"   {range_name:10} {count:3} ({pct:5.1f}%) {bar}")
    
    # Scores médios
    print(f"\n⭐ SCORES MÉDIOS")
    for score_name, value in analysis['avg_scores'].items():
        pct = value * 100
        bar = "█" * int(pct / 10)
        status = "✅" if value >= 0.6 else "⚠️" if value >= 0.5 else "❌"
        print(f"   {score_name:12} {value:.2f} ({pct:5.1f}%) {bar} {status}")
    
    # Insights
    print(f"\n💡 INSIGHTS")
    
    # Categoria dominante
    top_cat = max(analysis['categories'].items(), key=lambda x: x[1])
    top_cat_pct = top_cat[1] / total * 100
    if top_cat_pct > 40:
        print(f"   ⚠️  Categoria '{top_cat[0]}' domina ({top_cat_pct:.0f}%)")
        print(f"      Ação: Diversificar categorias")
    
    # Marca dominante
    top_brand = max(analysis['brands'].items(), key=lambda x: x[1])
    top_brand_pct = top_brand[1] / total * 100
    if top_brand_pct > 30:
        print(f"   ⚠️  Marca '{top_brand[0]}' domina ({top_brand_pct:.0f}%)")
        print(f"      Ação: Aplicar regra de max 30% por marca")
    
    # Scores genéricos
    if all(0.49 <= v <= 0.51 for v in analysis['avg_scores'].values()):
        print(f"   ❌ Scores genéricos (todos ~0.5)")
        print(f"      Ação: Executar calibrate_scores.py")
    
    # Faixa de entrada
    entry_level = analysis['price_ranges']['< 50k']
    entry_pct = entry_level / total * 100
    if entry_pct < 15:
        print(f"   ⚠️  Poucos carros de entrada ({entry_pct:.0f}%)")
        print(f"      Oportunidade: Ampliar faixa < R$ 50k")
    
    print(f"\n{'='*60}")
    print("📋 RECOMENDAÇÕES")
    print("="*60)
    
    if all(0.49 <= v <= 0.51 for v in analysis['avg_scores'].values()):
        print("1. ⭐ URGENTE: Calibrar scores")
        print("   python scripts/calibrate_scores.py")
    
    if diversity < 0.7:
        print("2. 📊 Melhorar diversidade")
        print("   - Adicionar mais marcas")
        print("   - Balancear categorias")
    
    if entry_pct < 15:
        print("3. 💰 Ampliar faixa de entrada")
        print("   - Target: 20% de carros < R$ 50k")
    
    print("\n✅ Análise completa!")
    print("="*60 + "\n")


def main():
    """Executa análise completa"""
    
    # Diretório de dados
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    
    # Carregar dados
    print("Carregando dados...")
    cars = load_all_cars(data_dir)
    
    if not cars:
        print("❌ Nenhum carro encontrado!")
        print(f"   Verifique o diretório: {data_dir}")
        return
    
    # Analisar
    analysis = analyze_inventory(cars)
    diversity = calculate_diversity_score(analysis)
    
    # Relatório
    print_report(analysis, diversity)
    
    # Salvar JSON
    output_file = os.path.join(data_dir, 'analysis_report.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        report = {
            'analysis': analysis,
            'diversity_score': diversity,
        }
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Relatório salvo: {output_file}")


if __name__ == "__main__":
    main()

