"""
Script de Correção de Dados dos Carros
Corrige categorias, enriquece features e recalcula scores
"""

import json
import sys
import os
from typing import Dict, List

# Adicionar path do backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.car_classifier import CarClassifier
from scripts.calibrate_scores import calibrate_car


def fix_car_categories(dealerships_file: str = 'data/dealerships.json') -> Dict:
    """
    Corrigir categorias de todos os carros
    
    Returns:
        Estatísticas da correção
    """
    print("=" * 70)
    print("CORRIGINDO CATEGORIAS DOS CARROS")
    print("=" * 70)
    
    # Carregar dados
    print(f"\n[1] Carregando: {dealerships_file}")
    with open(dealerships_file, 'r', encoding='utf-8') as f:
        dealerships = json.load(f)
    
    classifier = CarClassifier()
    stats = {
        'total': 0,
        'changed': 0,
        'by_category': {},
        'changes': []
    }
    
    # Processar cada concessionária
    for dealership in dealerships:
        for car in dealership.get('carros', []):
            stats['total'] += 1
            
            # Categoria atual
            old_category = car.get('categoria', 'Hatch')
            
            # Classificar nova categoria
            new_category = classifier.classify(
                car.get('nome', ''),
                car.get('modelo', car.get('nome', ''))
            )
            
            # Atualizar se diferente
            if old_category != new_category:
                stats['changed'] += 1
                stats['changes'].append({
                    'nome': car.get('nome'),
                    'old': old_category,
                    'new': new_category
                })
                car['categoria'] = new_category
                print(f"  [CORRIGIDO] {car.get('nome')}: {old_category} -> {new_category}")
            
            # Estatísticas por categoria
            stats['by_category'][new_category] = stats['by_category'].get(new_category, 0) + 1
    
    # Salvar dados corrigidos
    print(f"\n[2] Salvando: {dealerships_file}")
    with open(dealerships_file, 'w', encoding='utf-8') as f:
        json.dump(dealerships, f, ensure_ascii=False, indent=2)
    
    # Estatísticas
    print("\n" + "=" * 70)
    print("ESTATISTICAS DE CORRECAO")
    print("=" * 70)
    print(f"Total de carros: {stats['total']}")
    print(f"Categorias corrigidas: {stats['changed']}")
    print(f"\nDistribuição por categoria:")
    for cat, count in sorted(stats['by_category'].items()):
        print(f"  {cat}: {count} carros")
    
    return stats


def enrich_car_features(dealerships_file: str = 'data/dealerships.json') -> Dict:
    """
    Enriquecer itens de segurança e conforto
    
    Returns:
        Estatísticas do enriquecimento
    """
    print("\n" + "=" * 70)
    print("ENRIQUECENDO FEATURES DOS CARROS")
    print("=" * 70)
    
    # Carregar dados
    print(f"\n[1] Carregando: {dealerships_file}")
    with open(dealerships_file, 'r', encoding='utf-8') as f:
        dealerships = json.load(f)
    
    classifier = CarClassifier()
    stats = {
        'total': 0,
        'safety_enriched': 0,
        'comfort_enriched': 0
    }
    
    # Processar cada concessionária
    for dealership in dealerships:
        for car in dealership.get('carros', []):
            stats['total'] += 1
            
            # Dados do carro
            marca = car.get('marca', '')
            modelo = car.get('modelo', car.get('nome', ''))
            categoria = car.get('categoria', 'Hatch')
            ano = car.get('ano', 2020)
            
            # Itens atuais
            current_safety = car.get('itens_seguranca', [])
            current_comfort = car.get('itens_conforto', [])
            
            # Obter features típicas
            features = classifier.get_typical_features(marca, modelo, categoria, ano)
            
            # Mesclar com itens existentes (não sobrescrever)
            new_safety = list(set(current_safety + features['itens_seguranca']))
            new_comfort = list(set(current_comfort + features['itens_conforto']))
            
            # Atualizar se houve mudança
            if len(new_safety) > len(current_safety):
                stats['safety_enriched'] += 1
                car['itens_seguranca'] = new_safety
                print(f"  [SEGURANCA] {car.get('nome')}: {len(current_safety)} -> {len(new_safety)} itens")
            
            if len(new_comfort) > len(current_comfort):
                stats['comfort_enriched'] += 1
                car['itens_conforto'] = new_comfort
                print(f"  [CONFORTO] {car.get('nome')}: {len(current_comfort)} -> {len(new_comfort)} itens")
    
    # Salvar dados enriquecidos
    print(f"\n[2] Salvando: {dealerships_file}")
    with open(dealerships_file, 'w', encoding='utf-8') as f:
        json.dump(dealerships, f, ensure_ascii=False, indent=2)
    
    # Estatísticas
    print("\n" + "=" * 70)
    print("ESTATISTICAS DE ENRIQUECIMENTO")
    print("=" * 70)
    print(f"Total de carros: {stats['total']}")
    print(f"Seguranca enriquecida: {stats['safety_enriched']}")
    print(f"Conforto enriquecido: {stats['comfort_enriched']}")
    
    return stats


def recalculate_scores(dealerships_file: str = 'data/dealerships.json') -> Dict:
    """
    Recalcular scores baseado nas categorias corretas
    
    Returns:
        Estatísticas do recálculo
    """
    print("\n" + "=" * 70)
    print("RECALCULANDO SCORES DOS CARROS")
    print("=" * 70)
    
    # Carregar dados
    print(f"\n[1] Carregando: {dealerships_file}")
    with open(dealerships_file, 'r', encoding='utf-8') as f:
        dealerships = json.load(f)
    
    stats = {
        'total': 0,
        'recalculated': 0
    }
    
    # Processar cada concessionária
    for dealership in dealerships:
        for car in dealership.get('carros', []):
            stats['total'] += 1
            
            # Recalibrar scores usando categoria correta
            calibrated = calibrate_car(car)
            
            # Verificar se houve mudança nos scores
            scores_changed = False
            for score_key in ['score_familia', 'score_economia', 'score_performance', 
                             'score_conforto', 'score_seguranca']:
                old_value = car.get(score_key, 0.5)
                new_value = calibrated.get(score_key, 0.5)
                if abs(old_value - new_value) > 0.01:
                    scores_changed = True
                    break
            
            if scores_changed:
                stats['recalculated'] += 1
                # Atualizar scores
                for score_key in ['score_familia', 'score_economia', 'score_performance', 
                                 'score_conforto', 'score_seguranca']:
                    car[score_key] = calibrated.get(score_key, car.get(score_key, 0.5))
                
                print(f"  [RECALCULADO] {car.get('nome')}: categoria={car.get('categoria')}")
    
    # Salvar dados recalculados
    print(f"\n[2] Salvando: {dealerships_file}")
    with open(dealerships_file, 'w', encoding='utf-8') as f:
        json.dump(dealerships, f, ensure_ascii=False, indent=2)
    
    # Estatísticas
    print("\n" + "=" * 70)
    print("ESTATISTICAS DE RECALCULO")
    print("=" * 70)
    print(f"Total de carros: {stats['total']}")
    print(f"Scores recalculados: {stats['recalculated']}")
    
    return stats


def fix_all(dealerships_file: str = 'data/dealerships.json'):
    """
    Executar todas as correções em ordem
    """
    print("\n" + "=" * 70)
    print("INICIANDO CORRECAO COMPLETA DOS DADOS")
    print("=" * 70)
    
    # 1. Corrigir categorias
    cat_stats = fix_car_categories(dealerships_file)
    
    # 2. Enriquecer features
    feat_stats = enrich_car_features(dealerships_file)
    
    # 3. Recalcular scores
    score_stats = recalculate_scores(dealerships_file)
    
    # Resumo final
    print("\n" + "=" * 70)
    print("RESUMO FINAL")
    print("=" * 70)
    print(f"\nTotal de carros processados: {cat_stats['total']}")
    print(f"\nCategorias:")
    print(f"  - Corrigidas: {cat_stats['changed']}")
    print(f"  - Distribuição:")
    for cat, count in sorted(cat_stats['by_category'].items()):
        print(f"    * {cat}: {count}")
    print(f"\nFeatures:")
    print(f"  - Segurança enriquecida: {feat_stats['safety_enriched']}")
    print(f"  - Conforto enriquecido: {feat_stats['comfort_enriched']}")
    print(f"\nScores:")
    print(f"  - Recalculados: {score_stats['recalculated']}")
    
    print("\n" + "=" * 70)
    print("CORRECAO COMPLETA FINALIZADA COM SUCESSO!")
    print("=" * 70)


if __name__ == "__main__":
    # Executar correção completa
    fix_all()

