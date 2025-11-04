"""
Script para remover carros inválidos dos estoques
- Carros com preço R$ 0,00
- Motos
"""

import json
from pathlib import Path

def clean_stock_file(file_path: Path) -> dict:
    """
    Limpar carros inválidos de um arquivo de estoque
    
    Returns:
        Dict com estatísticas
    """
    print(f"\n{'='*80}")
    print(f"Limpando: {file_path.name}")
    print(f"{'='*80}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        vehicles = json.load(f)
    
    stats = {
        'total_original': len(vehicles),
        'preco_zero': [],
        'motos': [],
        'validos': []
    }
    
    for vehicle in vehicles:
        vehicle_id = vehicle.get('id', 'unknown')
        nome = vehicle.get('nome', '')
        preco = vehicle.get('preco', 0)
        categoria = vehicle.get('categoria', '')
        
        # Verificar se é inválido
        if preco <= 0:
            stats['preco_zero'].append({
                'id': vehicle_id,
                'nome': nome,
                'preco': preco
            })
        elif categoria == 'Moto':
            stats['motos'].append({
                'id': vehicle_id,
                'nome': nome,
                'preco': preco
            })
        else:
            stats['validos'].append(vehicle)
    
    # Relatório
    print(f"\nTotal original: {stats['total_original']}")
    
    if stats['preco_zero']:
        print(f"\n❌ {len(stats['preco_zero'])} carros com preço R$ 0,00:")
        for car in stats['preco_zero'][:10]:  # Mostrar até 10
            print(f"  • {car['nome']} - R$ {car['preco']:.2f}")
        if len(stats['preco_zero']) > 10:
            print(f"  ... e mais {len(stats['preco_zero']) - 10}")
    
    if stats['motos']:
        print(f"\n❌ {len(stats['motos'])} motos:")
        for moto in stats['motos']:
            print(f"  • {moto['nome']} - R$ {moto['preco']:,.2f}")
    
    print(f"\n✅ {len(stats['validos'])} carros válidos")
    
    # Salvar arquivo limpo
    if stats['preco_zero'] or stats['motos']:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(stats['validos'], f, ensure_ascii=False, indent=2)
        print(f"\n✅ Arquivo atualizado: {file_path.name}")
    else:
        print(f"\n✅ Nenhuma limpeza necessária")
    
    return stats


def main():
    """Limpar todos os arquivos de estoque"""
    
    data_dir = Path(__file__).parent.parent / 'data'
    
    stock_files = [
        data_dir / 'robustcar_estoque.json',
        data_dir / 'autocenter_estoque.json',
        data_dir / 'carplus_estoque.json'
    ]
    
    print("\n" + "="*80)
    print("LIMPEZA DE CARROS INVÁLIDOS")
    print("="*80)
    
    all_stats = []
    total_removed = 0
    
    for file_path in stock_files:
        if file_path.exists():
            stats = clean_stock_file(file_path)
            all_stats.append((file_path.name, stats))
            total_removed += len(stats['preco_zero']) + len(stats['motos'])
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO GERAL")
    print("="*80)
    
    total_original = sum(s['total_original'] for _, s in all_stats)
    total_validos = sum(len(s['validos']) for _, s in all_stats)
    
    print(f"\nTotal original: {total_original} veículos")
    print(f"Total válido: {total_validos} carros")
    print(f"Total removido: {total_removed} veículos")
    
    if total_removed > 0:
        print(f"\n✅ {total_removed} veículos inválidos removidos!")
        print("\nExecute 'python scripts/sync_dealerships_json.py' para sincronizar.")
    else:
        print("\n✅ Todos os estoques estão limpos!")


if __name__ == '__main__':
    main()
