#!/usr/bin/env python3
"""
Script para corrigir classificações incorretas específicas
"""

import json
from pathlib import Path
import sys

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.car_classifier import classifier


def fix_classifications():
    """Corrigir classificações conhecidas"""
    
    print("=" * 80)
    print("🔧 CORREÇÃO DE CLASSIFICAÇÕES INCORRETAS")
    print("=" * 80)
    
    data_dir = Path(__file__).parent.parent / 'data'
    estoques = [
        'robustcar_estoque.json',
        'autocenter_estoque.json', 
        'carplus_estoque.json'
    ]
    
    total_fixed = 0
    
    for estoque_file in estoques:
        file_path = data_dir / estoque_file
        if not file_path.exists():
            print(f"⚠️  Arquivo não encontrado: {estoque_file}")
            continue
        
        print(f"\n📂 Processando: {estoque_file}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            carros = json.load(f)
        
        fixed_in_file = 0
        changes = []
        
        for carro in carros:
            nome = carro.get('nome', '')
            modelo = carro.get('modelo', '')
            ano = carro.get('ano', 0)
            categoria_antiga = carro.get('categoria', '')
            
            # Reclassificar usando o classificador atualizado
            categoria_nova = classifier.classify(nome, modelo, ano)
            
            # Aplicar correção se mudou
            if categoria_antiga != categoria_nova:
                carro['categoria'] = categoria_nova
                fixed_in_file += 1
                total_fixed += 1
                
                changes.append({
                    'nome': nome,
                    'ano': ano,
                    'antiga': categoria_antiga,
                    'nova': categoria_nova
                })
                
                # Marcar motos como indisponíveis
                if categoria_nova == 'Moto':
                    carro['disponivel'] = False
        
        # Salvar arquivo atualizado
        if fixed_in_file > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(carros, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Corrigidos: {fixed_in_file}")
            print("\n📝 Mudanças:")
            for change in changes[:10]:  # Mostrar até 10 exemplos
                print(f"  • {change['nome']} ({change['ano']})")
                print(f"    {change['antiga']} → {change['nova']}")
        else:
            print(f"✅ Nenhuma correção necessária")
    
    print("\n" + "=" * 80)
    print(f"✅ TOTAL DE CORREÇÕES: {total_fixed}")
    print("=" * 80)
    
    if total_fixed > 0:
        print("\n💡 Reinicie o backend para aplicar as mudanças:")
        print("   python api/main.py")
    
    return total_fixed


if __name__ == '__main__':
    fix_classifications()
