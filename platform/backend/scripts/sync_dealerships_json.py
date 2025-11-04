"""
Script para sincronizar dealerships.json com os arquivos de estoque corrigidos
"""

import json
from pathlib import Path

def sync_dealerships():
    """Sincronizar dealerships.json com robustcar_estoque.json"""
    
    backend_dir = Path(__file__).parent.parent
    data_dir = backend_dir / 'data'
    
    # Carregar estoque corrigido
    robustcar_file = data_dir / 'robustcar_estoque.json'
    with open(robustcar_file, 'r', encoding='utf-8') as f:
        robustcar_cars = json.load(f)
    
    # Carregar dealerships
    dealerships_file = data_dir / 'dealerships.json'
    with open(dealerships_file, 'r', encoding='utf-8') as f:
        dealerships = json.load(f)
    
    # Encontrar RobustCar
    robustcar_dealer = None
    for dealer in dealerships:
        if dealer['id'] == 'robustcar_001':
            robustcar_dealer = dealer
            break
    
    if not robustcar_dealer:
        print("❌ RobustCar não encontrada em dealerships.json")
        return
    
    print(f"\n{'='*80}")
    print("SINCRONIZAÇÃO DE DADOS")
    print(f"{'='*80}\n")
    
    # Filtrar apenas carros disponíveis (excluir motos)
    cars_disponiveis = [car for car in robustcar_cars if car.get('disponivel', True)]
    
    print(f"Estoque RobustCar:")
    print(f"  • Total de veículos: {len(robustcar_cars)}")
    print(f"  • Carros disponíveis: {len(cars_disponiveis)}")
    print(f"  • Motos/indisponíveis: {len(robustcar_cars) - len(cars_disponiveis)}")
    
    # Atualizar carros no dealership
    robustcar_dealer['carros'] = cars_disponiveis
    
    # Salvar dealerships.json
    with open(dealerships_file, 'w', encoding='utf-8') as f:
        json.dump(dealerships, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ dealerships.json atualizado!")
    print(f"✅ {len(cars_disponiveis)} carros sincronizados")
    
    # Mostrar motos excluídas
    motos = [car for car in robustcar_cars if not car.get('disponivel', True)]
    if motos:
        print(f"\n📋 Veículos excluídos (motos/indisponíveis):")
        for moto in motos:
            print(f"  • {moto['nome']} - {moto['categoria']} - R$ {moto['preco']:,.2f}")


if __name__ == '__main__':
    sync_dealerships()
