"""
Sistema de Validação de Dados dos Carros
Valida qualidade dos dados e retorna relatório detalhado
"""

import json
import sys
import os
from typing import Dict, List

# Adicionar path do backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def validate_dealerships_data(file_path: str = 'data/dealerships.json') -> Dict:
    """
    Validar qualidade dos dados e retornar relatório
    
    Returns:
        Dicionário com estatísticas e erros encontrados
    """
    print("=" * 70)
    print("VALIDACAO DE DADOS DOS CARROS")
    print("=" * 70)
    
    # Categorias válidas
    VALID_CATEGORIES = ['Hatch', 'Sedan', 'SUV', 'Pickup', 'Compacto', 'Van']
    
    # Carregar dados
    print(f"\n[1] Carregando: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        dealerships = json.load(f)
    
    stats = {
        'total_cars': 0,
        'total_dealerships': len(dealerships),
        'valid_categories': 0,
        'invalid_categories': 0,
        'missing_images': 0,
        'missing_safety_items': 0,
        'missing_comfort_items': 0,
        'invalid_scores': 0,
        'invalid_prices': 0,
        'invalid_years': 0,
        'invalid_km': 0,
        'errors': [],
        'warnings': [],
        'category_distribution': {}
    }
    
    # Validar cada concessionária
    for dealership in dealerships:
        for car in dealership.get('carros', []):
            stats['total_cars'] += 1
            car_id = car.get('id', 'unknown')
            car_name = car.get('nome', 'unnamed')
            
            # 1. Validar categoria
            categoria = car.get('categoria', '')
            if categoria in VALID_CATEGORIES:
                stats['valid_categories'] += 1
                stats['category_distribution'][categoria] = stats['category_distribution'].get(categoria, 0) + 1
            else:
                stats['invalid_categories'] += 1
                stats['errors'].append(f"[{car_id}] {car_name}: categoria inválida '{categoria}'")
            
            # 2. Validar scores (0-1)
            scores = ['score_familia', 'score_economia', 'score_performance', 'score_conforto', 'score_seguranca']
            for score_key in scores:
                score = car.get(score_key, 0.5)
                if not (0.0 <= score <= 1.0):
                    stats['invalid_scores'] += 1
                    stats['errors'].append(f"[{car_id}] {car_name}: {score_key}={score} fora do range 0-1")
            
            # 3. Validar preço
            preco = car.get('preco', 0)
            if preco <= 0:
                stats['invalid_prices'] += 1
                stats['errors'].append(f"[{car_id}] {car_name}: preço inválido {preco}")
            
            # 4. Validar ano
            ano = car.get('ano', 0)
            if not (2000 <= ano <= 2026):
                stats['invalid_years'] += 1
                stats['errors'].append(f"[{car_id}] {car_name}: ano inválido {ano}")
            
            # 5. Validar quilometragem
            km = car.get('quilometragem', 0)
            if km < 0:
                stats['invalid_km'] += 1
                stats['errors'].append(f"[{car_id}] {car_name}: km negativa {km}")
            
            # 6. Validar imagens
            imagens = car.get('imagens', [])
            if not imagens or len(imagens) == 0:
                stats['missing_images'] += 1
                stats['warnings'].append(f"[{car_id}] {car_name}: sem imagens")
            
            # 7. Validar itens de segurança (ano >= 2015 deveria ter)
            if ano >= 2015:
                itens_seguranca = car.get('itens_seguranca', [])
                if not itens_seguranca or len(itens_seguranca) == 0:
                    stats['missing_safety_items'] += 1
                    stats['warnings'].append(f"[{car_id}] {car_name}: ano {ano} sem itens_seguranca")
            
            # 8. Validar itens de conforto
            itens_conforto = car.get('itens_conforto', [])
            if not itens_conforto or len(itens_conforto) == 0:
                stats['missing_comfort_items'] += 1
                stats['warnings'].append(f"[{car_id}] {car_name}: sem itens_conforto")
    
    # Relatório
    print("\n" + "=" * 70)
    print("RELATORIO DE VALIDACAO")
    print("=" * 70)
    print(f"\nConcessionarias: {stats['total_dealerships']}")
    print(f"Total de carros: {stats['total_cars']}")
    
    print(f"\n[CATEGORIAS]")
    print(f"  Validas: {stats['valid_categories']}")
    print(f"  Invalidas: {stats['invalid_categories']}")
    print(f"\n  Distribuicao:")
    for cat, count in sorted(stats['category_distribution'].items()):
        percentage = (count / stats['total_cars'] * 100) if stats['total_cars'] > 0 else 0
        print(f"    {cat}: {count} ({percentage:.1f}%)")
    
    print(f"\n[DADOS FALTANTES/INVALIDOS]")
    print(f"  Sem imagens: {stats['missing_images']}")
    print(f"  Sem itens_seguranca: {stats['missing_safety_items']}")
    print(f"  Sem itens_conforto: {stats['missing_comfort_items']}")
    print(f"  Scores invalidos: {stats['invalid_scores']}")
    print(f"  Precos invalidos: {stats['invalid_prices']}")
    print(f"  Anos invalidos: {stats['invalid_years']}")
    print(f"  Quilometragem invalida: {stats['invalid_km']}")
    
    print(f"\n[RESUMO]")
    total_errors = len(stats['errors'])
    total_warnings = len(stats['warnings'])
    print(f"  Erros criticos: {total_errors}")
    print(f"  Avisos: {total_warnings}")
    
    if total_errors > 0:
        print(f"\n[ERROS] (mostrando primeiros 10)")
        for error in stats['errors'][:10]:
            print(f"  - {error}")
    
    if total_warnings > 0:
        print(f"\n[AVISOS] (mostrando primeiros 10)")
        for warning in stats['warnings'][:10]:
            print(f"  - {warning}")
    
    # Qualidade geral
    quality_score = 100
    if stats['total_cars'] > 0:
        quality_score -= (stats['invalid_categories'] / stats['total_cars']) * 20
        quality_score -= (stats['missing_images'] / stats['total_cars']) * 15
        quality_score -= (stats['missing_safety_items'] / stats['total_cars']) * 10
        quality_score -= (stats['invalid_scores'] / stats['total_cars']) * 20
        quality_score = max(0, quality_score)
    
    print(f"\n[QUALIDADE GERAL]")
    print(f"  Score: {quality_score:.1f}/100")
    
    if quality_score >= 90:
        print(f"  Status: EXCELENTE")
    elif quality_score >= 75:
        print(f"  Status: BOM")
    elif quality_score >= 60:
        print(f"  Status: REGULAR")
    else:
        print(f"  Status: NECESSITA MELHORIAS")
    
    print("\n" + "=" * 70)
    
    return stats


if __name__ == "__main__":
    validate_dealerships_data()

