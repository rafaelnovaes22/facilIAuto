"""
Script para validar todos os veículos nos estoques
Verifica classificações e identifica problemas
"""

import json
import sys
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.car_classifier import CarClassifier


def validate_stock_file(file_path: Path) -> dict:
    """
    Validar classificações em um arquivo de estoque
    
    Returns:
        Dict com estatísticas e problemas encontrados
    """
    print(f"\n{'='*80}")
    print(f"Validando: {file_path.name}")
    print(f"{'='*80}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        vehicles = json.load(f)
    
    classifier = CarClassifier()
    
    stats = {
        'total': len(vehicles),
        'motos': 0,
        'carros': 0,
        'problemas': [],
        'motos_disponiveis': []
    }
    
    for vehicle in vehicles:
        vehicle_id = vehicle.get('id', 'unknown')
        nome = vehicle.get('nome', '')
        modelo = vehicle.get('modelo', '')
        marca = vehicle.get('marca', '')
        ano = vehicle.get('ano')
        categoria_atual = vehicle.get('categoria', '')
        disponivel = vehicle.get('disponivel', True)
        preco = vehicle.get('preco', 0)
        
        # Classificar corretamente
        categoria_esperada = classifier.classify(
            nome=nome,
            modelo=modelo,
            ano=ano,
            marca=marca
        )
        
        # Contar
        if categoria_esperada == 'Moto':
            stats['motos'] += 1
        else:
            stats['carros'] += 1
        
        # Verificar problemas
        if categoria_atual != categoria_esperada:
            stats['problemas'].append({
                'id': vehicle_id,
                'nome': nome,
                'marca': marca,
                'preco': preco,
                'categoria_atual': categoria_atual,
                'categoria_esperada': categoria_esperada,
                'tipo': 'classificacao_incorreta'
            })
        
        # Motos devem ter disponivel=False
        if categoria_esperada == 'Moto' and disponivel:
            stats['motos_disponiveis'].append({
                'id': vehicle_id,
                'nome': nome,
                'preco': preco
            })
    
    # Relatório
    print(f"\nTotal de veículos: {stats['total']}")
    print(f"  • Carros: {stats['carros']}")
    print(f"  • Motos: {stats['motos']}")
    
    if stats['problemas']:
        print(f"\n⚠️  {len(stats['problemas'])} problemas de classificação:")
        for prob in stats['problemas']:
            print(f"\n  • {prob['nome']}")
            print(f"    ID: {prob['id']}")
            print(f"    Marca: {prob['marca']}")
            print(f"    Preço: R$ {prob['preco']:,.2f}")
            print(f"    Atual: {prob['categoria_atual']} → Esperado: {prob['categoria_esperada']}")
    else:
        print("\n✅ Todas as classificações estão corretas!")
    
    if stats['motos_disponiveis']:
        print(f"\n⚠️  {len(stats['motos_disponiveis'])} motos com disponivel=True:")
        for moto in stats['motos_disponiveis']:
            print(f"  • {moto['nome']} (R$ {moto['preco']:,.2f})")
    
    return stats


def main():
    """Validar todos os arquivos de estoque"""
    
    data_dir = Path(__file__).parent.parent / 'data'
    
    stock_files = [
        data_dir / 'robustcar_estoque.json',
        data_dir / 'autocenter_estoque.json',
        data_dir / 'carplus_estoque.json'
    ]
    
    print("\n" + "="*80)
    print("VALIDAÇÃO DE CLASSIFICAÇÃO DE VEÍCULOS")
    print("="*80)
    
    all_stats = []
    total_problems = 0
    
    for file_path in stock_files:
        if file_path.exists():
            stats = validate_stock_file(file_path)
            all_stats.append((file_path.name, stats))
            total_problems += len(stats['problemas']) + len(stats['motos_disponiveis'])
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO GERAL")
    print("="*80)
    
    total_vehicles = sum(s['total'] for _, s in all_stats)
    total_cars = sum(s['carros'] for _, s in all_stats)
    total_motos = sum(s['motos'] for _, s in all_stats)
    
    print(f"\nTotal geral:")
    print(f"  • Veículos: {total_vehicles}")
    print(f"  • Carros: {total_cars}")
    print(f"  • Motos: {total_motos}")
    
    if total_problems == 0:
        print("\n✅ TUDO OK! Nenhum problema encontrado.")
    else:
        print(f"\n⚠️  {total_problems} problemas encontrados no total.")
        print("\nExecute 'python scripts/fix_misclassified_vehicles.py' para corrigir.")


if __name__ == '__main__':
    main()
