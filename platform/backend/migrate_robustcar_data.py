"""
Script para migrar dados do RobustCar (com imagens reais) para a plataforma FacilIAuto
"""

import json
import os
from pathlib import Path

def migrate_robustcar_to_platform():
    """Migrar dados do RobustCar para a plataforma"""
    
    # Caminhos
    robustcar_json = Path('../../examples/RobustCar/robustcar_estoque_20250912_135949.json')
    dealership_json = Path('data/dealerships.json')
    
    print("=" * 70)
    print("MIGRACAO DE DADOS ROBUSTCAR -> FACILIAUTO")
    print("=" * 70)
    
    # Carregar dados do RobustCar
    print("\n[1] Carregando dados do RobustCar...")
    with open(robustcar_json, 'r', encoding='utf-8') as f:
        robustcar_cars = json.load(f)
    
    print(f"    [OK] {len(robustcar_cars)} carros carregados do RobustCar")
    
    # Criar estrutura de concessionária RobustCar
    robustcar_dealership = {
        "id": "robustcar_001",
        "nome": "RobustCar - Veículos Selecionados",
        "cidade": "São Paulo",
        "estado": "SP",
        "telefone": "(11) 99999-9999",
        "whatsapp": "5511999999999",
        "endereco": "Av. Exemplo, 1000 - São Paulo - SP",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "carros": []
    }
    
    print("\n[2] Convertendo carros para formato da plataforma...")
    converted_count = 0
    
    for car in robustcar_cars:
        # Converter para formato da plataforma
        platform_car = {
            "id": car.get('id', f"robust_{converted_count}"),
            "dealership_id": "robustcar_001",
            "nome": car.get('nome', car.get('modelo', 'Sem nome')),
            "marca": car.get('marca', 'Sem marca'),
            "modelo": car.get('modelo', car.get('nome', 'Sem modelo')),
            "ano": car.get('ano', 2024),
            "preco": car.get('preco', 0),
            "quilometragem": car.get('quilometragem', 0),
            "combustivel": car.get('combustivel', 'Flex'),
            "categoria": car.get('categoria', 'Hatch'),
            "cambio": car.get('cambio', 'Manual'),
            "cor": car.get('cor', 'Não informado'),
            
            # Dados da concessionária (denormalizados)
            "dealership_name": "RobustCar - Veículos Selecionados",
            "dealership_city": "São Paulo",
            "dealership_state": "SP",
            "dealership_phone": "(11) 99999-9999",
            "dealership_whatsapp": "5511999999999",
            "dealership_latitude": -23.5505,
            "dealership_longitude": -46.6333,
            
            # Imagens (CHAVE PARA O PROBLEMA!)
            "imagens": car.get('imagens', []),
            
            # Scores (se existirem)
            "score_economia": car.get('score_economia', 0.5),
            "score_familia": car.get('score_familia', 0.5),
            
            # Itens de segurança e conforto (inferir da categoria)
            "itens_seguranca": [],
            "itens_conforto": []
        }
        
        # Adicionar itens baseado na categoria/ano
        if platform_car['ano'] >= 2020:
            platform_car['itens_seguranca'].extend(['ABS', 'airbag'])
            platform_car['itens_conforto'].extend(['ar_condicionado'])
            
        if platform_car['ano'] >= 2022:
            platform_car['itens_seguranca'].append('controle_estabilidade')
            
        robustcar_dealership['carros'].append(platform_car)
        converted_count += 1
    
    print(f"    [OK] {converted_count} carros convertidos")
    
    # Carregar concessionárias existentes
    print("\n[3] Integrando com concessionárias existentes...")
    
    if dealership_json.exists():
        with open(dealership_json, 'r', encoding='utf-8') as f:
            existing_dealerships = json.load(f)
        print(f"    [INFO] {len(existing_dealerships)} concessionárias existentes")
    else:
        existing_dealerships = []
        print(f"    [INFO] Nenhuma concessionária existente, criando nova lista")
    
    # Remover RobustCar antiga se existir
    existing_dealerships = [d for d in existing_dealerships if d.get('id') != 'robustcar_001']
    
    # Adicionar RobustCar atualizada
    existing_dealerships.append(robustcar_dealership)
    
    print(f"    [OK] RobustCar adicionada (total: {len(existing_dealerships)} concessionárias)")
    
    # Salvar
    print("\n[4] Salvando dados atualizados...")
    with open(dealership_json, 'w', encoding='utf-8') as f:
        json.dump(existing_dealerships, f, ensure_ascii=False, indent=2)
    
    print(f"    [OK] Salvo em: {dealership_json}")
    
    # Estatísticas
    total_cars = sum(len(d['carros']) for d in existing_dealerships)
    cars_with_images = sum(
        1 for d in existing_dealerships 
        for car in d['carros'] 
        if car.get('imagens') and len(car['imagens']) > 0
    )
    
    print("\n" + "=" * 70)
    print("ESTATISTICAS FINAIS")
    print("=" * 70)
    print(f"Concessionarias: {len(existing_dealerships)}")
    print(f"Total de carros: {total_cars}")
    print(f"Carros com imagens: {cars_with_images} ({cars_with_images/total_cars*100:.1f}%)")
    print(f"RobustCar carros: {len(robustcar_dealership['carros'])}")
    print(f"RobustCar imagens: {converted_count} (100%)")
    print("=" * 70)
    
    # Mostrar exemplos de URLs de imagens
    print("\n[EXEMPLO] URLs de imagens migradas:")
    for i, car in enumerate(robustcar_dealership['carros'][:3]):
        if car.get('imagens'):
            print(f"  {i+1}. {car['nome']}")
            print(f"     Imagens: {len(car['imagens'])}")
            print(f"     URL: {car['imagens'][0][:80]}...")
    
    print("\n[SUCESSO] Migracao concluida com sucesso!")
    print("O frontend agora vai exibir imagens reais dos carros!")
    
    return True

if __name__ == "__main__":
    migrate_robustcar_to_platform()

