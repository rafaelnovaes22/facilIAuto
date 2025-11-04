"""
Script para corrigir classificações incorretas de veículos
Identifica motos classificadas como carros e vice-versa
"""

import json
import os
from pathlib import Path

# Marcas de motos conhecidas
MOTO_BRANDS = [
    'yamaha', 'honda', 'kawasaki', 'suzuki', 'bmw motorrad',
    'harley-davidson', 'ducati', 'triumph', 'ktm', 'royal enfield',
    'benelli', 'dafra', 'shineray', 'traxx', 'kasinski'
]

# Modelos de motos conhecidos (padrões específicos)
MOTO_MODELS = [
    'cb ', 'cb-', 'cbr', 'cb125', 'cb300', 'cb500', 'cb650', 'cb1000',
    'mt-', 'mt07', 'mt09', 'mt03',
    'xj', 'xt', 'xtz', 'ybr', 'fazer', 'yzf', 'r1', 'r3', 'r6',
    'ninja', 'z650', 'z900', 'zx', 'versys',
    'gsxr', 'gsx', 'v-strom', 'bandit', 'intruder',
    'crf', 'xre', 'bros', 'biz', 'pop', 'titan', 'fan',
    'r1200', 'f800', 'g310', 'gs', 'adventure',
    'neo', 'nmax', 'pcx', 'sh', 'lead',  # Scooters
    'lander', 'crosser', 'tenere'
]

# Palavras-chave que indicam moto
MOTO_KEYWORDS = [
    'moto', 'motorcycle', 'bike', 'scooter', 'motocicleta',
    'cilindrada', 'cc', 'trail', 'enduro', 'custom'
]

# Modelos de carros que podem ser confundidos
CAR_MODELS_ONIX = ['onix']  # Chevrolet Onix é sempre carro


def is_motorcycle(vehicle: dict) -> bool:
    """
    Determinar se um veículo é uma moto
    
    Args:
        vehicle: Dicionário com dados do veículo
    
    Returns:
        True se for moto, False se for carro
    """
    nome = vehicle.get('nome', '').lower()
    marca = vehicle.get('marca', '').lower()
    modelo = vehicle.get('modelo', '').lower()
    
    search_text = f"{nome} {marca} {modelo}"
    
    # 1. Verificar marca
    if any(moto_brand in marca for moto_brand in MOTO_BRANDS):
        # Yamaha, Honda, etc podem fazer carros também, então verificar modelo
        # Se tem modelo de moto, é moto
        if any(moto_model in search_text for moto_model in MOTO_MODELS):
            return True
        # Se tem palavra-chave de moto, é moto
        if any(keyword in search_text for keyword in MOTO_KEYWORDS):
            return True
        # Yamaha no Brasil só faz motos
        if 'yamaha' in marca:
            return True
    
    # 2. Verificar modelos específicos de motos
    if any(moto_model in search_text for moto_model in MOTO_MODELS):
        return True
    
    # 3. Verificar palavras-chave
    if any(keyword in search_text for keyword in MOTO_KEYWORDS):
        return True
    
    return False


def is_car(vehicle: dict) -> bool:
    """
    Determinar se um veículo é um carro (não moto)
    
    Args:
        vehicle: Dicionário com dados do veículo
    
    Returns:
        True se for carro, False se for moto
    """
    nome = vehicle.get('nome', '').lower()
    modelo = vehicle.get('modelo', '').lower()
    
    # Chevrolet Onix é sempre carro
    if 'onix' in nome or 'onix' in modelo:
        return True
    
    # Se não é moto, é carro
    return not is_motorcycle(vehicle)


def fix_classifications(file_path: str, dry_run: bool = True) -> dict:
    """
    Corrigir classificações incorretas em um arquivo de estoque
    
    Args:
        file_path: Caminho do arquivo JSON
        dry_run: Se True, apenas reporta sem modificar
    
    Returns:
        Dict com estatísticas das correções
    """
    print(f"\n{'='*80}")
    print(f"Processando: {file_path}")
    print(f"{'='*80}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        vehicles = json.load(f)
    
    stats = {
        'total': len(vehicles),
        'motos_corretas': 0,
        'carros_corretos': 0,
        'moto_como_carro': 0,
        'carro_como_moto': 0,
        'corrigidos': []
    }
    
    for vehicle in vehicles:
        current_category = vehicle.get('categoria', '')
        vehicle_id = vehicle.get('id', 'unknown')
        nome = vehicle.get('nome', '')
        
        is_moto = is_motorcycle(vehicle)
        should_be = 'Moto' if is_moto else current_category
        
        # Verificar se está incorreto
        if is_moto and current_category != 'Moto':
            stats['moto_como_carro'] += 1
            print(f"\n❌ MOTO classificada como {current_category}:")
            print(f"   ID: {vehicle_id}")
            print(f"   Nome: {nome}")
            print(f"   Marca: {vehicle.get('marca', 'N/A')}")
            print(f"   Modelo: {vehicle.get('modelo', 'N/A')}")
            print(f"   → Deve ser: Moto")
            
            if not dry_run:
                vehicle['categoria'] = 'Moto'
                vehicle['disponivel'] = False  # Motos não devem aparecer em busca de carros
                stats['corrigidos'].append({
                    'id': vehicle_id,
                    'nome': nome,
                    'de': current_category,
                    'para': 'Moto'
                })
        
        elif not is_moto and current_category == 'Moto':
            stats['carro_como_moto'] += 1
            
            # Reclassificar o carro corretamente
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from services.car_classifier import classifier
            correct_category = classifier.classify(
                nome=vehicle.get('nome', ''),
                modelo=vehicle.get('modelo', ''),
                ano=vehicle.get('ano')
            )
            
            print(f"\n❌ CARRO classificado como Moto:")
            print(f"   ID: {vehicle_id}")
            print(f"   Nome: {nome}")
            print(f"   Marca: {vehicle.get('marca', 'N/A')}")
            print(f"   Modelo: {vehicle.get('modelo', 'N/A')}")
            print(f"   → Deve ser: {correct_category}")
            
            if not dry_run:
                vehicle['categoria'] = correct_category
                vehicle['disponivel'] = True  # Carros devem estar disponíveis
                stats['corrigidos'].append({
                    'id': vehicle_id,
                    'nome': nome,
                    'de': 'Moto',
                    'para': correct_category
                })
        
        elif is_moto:
            stats['motos_corretas'] += 1
        else:
            stats['carros_corretos'] += 1
    
    # Salvar arquivo corrigido
    if not dry_run and stats['corrigidos']:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(vehicles, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Arquivo atualizado: {file_path}")
    
    return stats


def main():
    """Executar correção em todos os arquivos de estoque"""
    
    # Diretório de dados
    data_dir = Path(__file__).parent.parent / 'data'
    
    # Arquivos de estoque
    stock_files = [
        data_dir / 'robustcar_estoque.json',
        data_dir / 'autocenter_estoque.json',
        data_dir / 'carplus_estoque.json'
    ]
    
    print("\n" + "="*80)
    print("ANÁLISE DE CLASSIFICAÇÃO DE VEÍCULOS")
    print("="*80)
    print("\nModo: DRY RUN (apenas análise, sem modificações)")
    print("\nPressione ENTER para continuar ou Ctrl+C para cancelar...")
    input()
    
    # Primeira passagem: dry run
    all_stats = []
    for file_path in stock_files:
        if file_path.exists():
            stats = fix_classifications(str(file_path), dry_run=True)
            all_stats.append((file_path.name, stats))
    
    # Resumo
    print("\n" + "="*80)
    print("RESUMO GERAL")
    print("="*80)
    
    total_issues = 0
    for filename, stats in all_stats:
        issues = stats['moto_como_carro'] + stats['carro_como_moto']
        total_issues += issues
        
        print(f"\n{filename}:")
        print(f"  Total de veículos: {stats['total']}")
        print(f"  ✅ Motos corretas: {stats['motos_corretas']}")
        print(f"  ✅ Carros corretos: {stats['carros_corretos']}")
        print(f"  ❌ Motos como carros: {stats['moto_como_carro']}")
        print(f"  ❌ Carros como motos: {stats['carro_como_moto']}")
    
    if total_issues > 0:
        print(f"\n⚠️  Total de problemas encontrados: {total_issues}")
        print("\nDeseja aplicar as correções? (s/N): ", end='')
        response = input().strip().lower()
        
        if response == 's':
            print("\n" + "="*80)
            print("APLICANDO CORREÇÕES")
            print("="*80)
            
            for file_path in stock_files:
                if file_path.exists():
                    fix_classifications(str(file_path), dry_run=False)
            
            print("\n✅ Todas as correções foram aplicadas!")
        else:
            print("\n❌ Correções canceladas.")
    else:
        print("\n✅ Nenhum problema encontrado! Todas as classificações estão corretas.")


if __name__ == '__main__':
    main()
