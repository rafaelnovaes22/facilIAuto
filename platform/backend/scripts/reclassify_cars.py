#!/usr/bin/env python3
"""
Script para reclassificar todos os carros usando o classificador atualizado
"""

import json
from pathlib import Path
import sys

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.car_classifier import classifier


def reclassify_file(filepath):
    """Reclassificar carros em um arquivo"""
    print(f"\n📂 Processando: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    changed = 0
    examples = []
    
    # Se for lista de carros diretamente
    if isinstance(data, list) and len(data) > 0 and 'nome' in data[0]:
        for car in data:
            old_cat = car.get('categoria', '')
            new_cat = classifier.classify(
                car['nome'], 
                car.get('modelo', car['nome']),
                car.get('ano')
            )
            
            # Filtrar motos (não devem estar no estoque de carros)
            if new_cat == 'Moto':
                print(f"⚠️  MOTO DETECTADA (será mantida mas marcada): {car['nome']}")
                car['categoria'] = 'Moto'
                car['disponivel'] = False  # Marcar como indisponível
            
            if old_cat != new_cat:
                car['categoria'] = new_cat
                changed += 1
                examples.append({
                    'nome': car['nome'],
                    'ano': car.get('ano', 'N/A'),
                    'old': old_cat,
                    'new': new_cat
                })
    
    # Se for lista de concessionárias com carros
    elif isinstance(data, list) and len(data) > 0 and 'carros' in data[0]:
        for dealership in data:
            for car in dealership.get('carros', []):
                old_cat = car.get('categoria', '')
                new_cat = classifier.classify(
                    car['nome'], 
                    car.get('modelo', car['nome']),
                    car.get('ano')
                )
                
                # Filtrar motos
                if new_cat == 'Moto':
                    print(f"⚠️  MOTO DETECTADA (será mantida mas marcada): {car['nome']}")
                    car['categoria'] = 'Moto'
                    car['disponivel'] = False
                
                if old_cat != new_cat:
                    car['categoria'] = new_cat
                    changed += 1
                    examples.append({
                        'nome': car['nome'],
                        'ano': car.get('ano', 'N/A'),
                        'old': old_cat,
                        'new': new_cat
                    })
    
    # Salvar arquivo
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Categorias atualizadas: {changed}")
    
    if examples:
        print("\n📝 Exemplos de mudanças:")
        for i, ex in enumerate(examples[:5], 1):
            print(f"  {i}. {ex['nome']} ({ex['ano']})")
            print(f"     {ex['old']} → {ex['new']}")
    
    return changed


def main():
    print("=" * 60)
    print("🔄 RECLASSIFICAÇÃO DE CARROS")
    print("=" * 60)
    
    data_dir = Path(__file__).parent.parent / 'data'
    
    files = [
        data_dir / 'robustcar_estoque.json',
        data_dir / 'autocenter_estoque.json',
        data_dir / 'carplus_estoque.json',
        data_dir / 'dealerships.json',
    ]
    
    total_changed = 0
    
    for filepath in files:
        if filepath.exists():
            changed = reclassify_file(filepath)
            total_changed += changed
        else:
            print(f"⚠️  Arquivo não encontrado: {filepath}")
    
    print("\n" + "=" * 60)
    print(f"✅ TOTAL DE CATEGORIAS ATUALIZADAS: {total_changed}")
    print("=" * 60)


if __name__ == '__main__':
    main()
