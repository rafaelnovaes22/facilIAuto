"""
Script simples para corrigir veículos mal classificados
"""

import json
from pathlib import Path

def fix_robustcar_stock():
    """Corrigir classificações no estoque da RobustCar"""
    
    file_path = Path(__file__).parent.parent / 'data' / 'robustcar_estoque.json'
    
    print(f"Carregando: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        vehicles = json.load(f)
    
    corrections = []
    
    for vehicle in vehicles:
        vehicle_id = vehicle.get('id', '')
        nome = vehicle.get('nome', '').lower()
        marca = vehicle.get('marca', '').lower()
        categoria_atual = vehicle.get('categoria', '')
        
        # Regras de correção
        nova_categoria = None
        motivo = None
        
        # 1. Yamaha Neo Automatic - é uma moto (scooter)
        if 'yamaha' in marca and 'neo' in nome:
            if categoria_atual != 'Moto':
                nova_categoria = 'Moto'
                motivo = 'Yamaha Neo é uma moto scooter'
                vehicle['disponivel'] = False  # Motos não aparecem em busca de carros
        
        # 2. Chevrolet Onix - é sempre um carro Hatch
        elif 'onix' in nome and 'chevrolet' in marca:
            if categoria_atual == 'Moto':
                nova_categoria = 'Hatch'
                motivo = 'Chevrolet Onix é um carro hatch'
                vehicle['disponivel'] = True
        
        # 3. Toyota Prius - é um carro Hatch híbrido
        elif 'prius' in nome and 'toyota' in marca:
            if categoria_atual == 'Moto':
                nova_categoria = 'Hatch'
                motivo = 'Toyota Prius é um carro hatch híbrido'
                vehicle['disponivel'] = True
        
        # 4. Mitsubishi ASX - é um SUV
        elif 'asx' in nome and 'mitsubishi' in marca:
            if categoria_atual == 'Moto':
                nova_categoria = 'SUV'
                motivo = 'Mitsubishi ASX é um SUV'
                vehicle['disponivel'] = True
        
        # 5. Qualquer Yamaha que não seja carro (Yamaha só faz motos no Brasil)
        elif 'yamaha' in marca and categoria_atual != 'Moto':
            nova_categoria = 'Moto'
            motivo = 'Yamaha só fabrica motos no Brasil'
            vehicle['disponivel'] = False
        
        # Aplicar correção
        if nova_categoria:
            corrections.append({
                'id': vehicle_id,
                'nome': vehicle.get('nome', ''),
                'de': categoria_atual,
                'para': nova_categoria,
                'motivo': motivo
            })
            vehicle['categoria'] = nova_categoria
    
    # Mostrar correções
    if corrections:
        print(f"\n{'='*80}")
        print(f"CORREÇÕES APLICADAS ({len(corrections)} veículos)")
        print(f"{'='*80}\n")
        
        for corr in corrections:
            print(f"✓ {corr['nome']}")
            print(f"  ID: {corr['id']}")
            print(f"  {corr['de']} → {corr['para']}")
            print(f"  Motivo: {corr['motivo']}")
            print()
        
        # Salvar arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(vehicles, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Arquivo atualizado: {file_path}")
        print(f"✅ {len(corrections)} veículos corrigidos")
    else:
        print("\n✅ Nenhuma correção necessária!")
    
    return len(corrections)


def verify_price_range_10k_15k():
    """Verificar veículos na faixa de R$ 10.000 a R$ 15.000"""
    
    file_path = Path(__file__).parent.parent / 'data' / 'robustcar_estoque.json'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        vehicles = json.load(f)
    
    print(f"\n{'='*80}")
    print("VEÍCULOS NA FAIXA R$ 10.000 - R$ 15.000")
    print(f"{'='*80}\n")
    
    found = []
    for vehicle in vehicles:
        preco = vehicle.get('preco', 0)
        if 10000 <= preco <= 15000:
            found.append(vehicle)
            print(f"• {vehicle.get('nome', 'N/A')}")
            print(f"  Preço: R$ {preco:,.2f}")
            print(f"  Categoria: {vehicle.get('categoria', 'N/A')}")
            print(f"  Disponível: {vehicle.get('disponivel', False)}")
            print()
    
    if not found:
        print("Nenhum veículo encontrado nesta faixa de preço.")
    else:
        print(f"Total: {len(found)} veículos")
    
    return found


if __name__ == '__main__':
    print("\n" + "="*80)
    print("CORREÇÃO DE CLASSIFICAÇÕES DE VEÍCULOS")
    print("="*80)
    
    # Aplicar correções
    num_corrections = fix_robustcar_stock()
    
    # Verificar faixa de preço problemática
    vehicles_in_range = verify_price_range_10k_15k()
    
    print("\n" + "="*80)
    print("CONCLUÍDO")
    print("="*80)
    print(f"✓ {num_corrections} correções aplicadas")
    print(f"✓ {len(vehicles_in_range)} veículos na faixa R$ 10k-15k")
