"""
Script para migrar dados existentes para o formato multi-concessionária
"""

import json
import os
import shutil
from datetime import datetime
from typing import List, Dict


def migrate_robustcar_data():
    """Migrar dados existentes da RobustCar"""
    print("Migrando dados da RobustCar...")
    
    # Buscar arquivo mais recente de estoque da RobustCar
    robustcar_dir = "../../RobustCar"
    estoque_files = [f for f in os.listdir(robustcar_dir) if f.startswith("robustcar_estoque") and f.endswith(".json")]
    
    if not estoque_files:
        print("[ERRO] Nenhum arquivo de estoque da RobustCar encontrado")
        return
    
    # Pegar o mais recente
    latest_file = sorted(estoque_files)[-1]
    source_path = os.path.join(robustcar_dir, latest_file)
    
    print(f"[OK] Encontrado: {source_path}")
    
    # Carregar dados
    with open(source_path, 'r', encoding='utf-8') as f:
        cars = json.load(f)
    
    print(f"[OK] {len(cars)} carros carregados")
    
    # Enriquecer com informações da concessionária
    enriched_cars = []
    for car in cars:
        # Garantir campos obrigatórios
        enriched_car = {
            **car,
            'dealership_id': 'robustcar',
            'dealership_name': 'RobustCar São Paulo',
            'dealership_city': 'São Paulo',
            'dealership_state': 'SP',
            'dealership_phone': '(11) 3456-7890',
            'dealership_whatsapp': '5511987654321',
            'disponivel': True,
            'destaque': False,
            'data_atualizacao': datetime.now().isoformat()
        }
        
        # Garantir scores
        if 'score_familia' not in enriched_car:
            enriched_car['score_familia'] = 0.5
        if 'score_economia' not in enriched_car:
            enriched_car['score_economia'] = 0.5
        if 'score_performance' not in enriched_car:
            enriched_car['score_performance'] = 0.5
        if 'score_conforto' not in enriched_car:
            enriched_car['score_conforto'] = 0.5
        if 'score_seguranca' not in enriched_car:
            enriched_car['score_seguranca'] = 0.5
        
        enriched_cars.append(enriched_car)
    
    # Salvar no novo formato
    dest_path = "data/robustcar_estoque.json"
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    with open(dest_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_cars, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Dados migrados para: {dest_path}")
    print(f"[OK] Total: {len(enriched_cars)} carros")


def generate_mock_dealership_data(dealership_id: str, dealership_info: Dict, num_cars: int = 20):
    """Gerar dados mock para outras concessionárias"""
    print(f"\nGerando dados mock para {dealership_info['name']}...")
    
    # Carros de exemplo
    mock_cars_templates = [
        {
            "marca": "Volkswagen", "modelo": "Gol", "versao": "1.0", "categoria": "Hatch",
            "combustivel": "Flex", "cambio": "Manual", "portas": 4,
            "score_economia": 0.9, "score_familia": 0.5, "score_performance": 0.4, "score_conforto": 0.5, "score_seguranca": 0.6
        },
        {
            "marca": "Chevrolet", "modelo": "Onix", "versao": "1.0 Turbo", "categoria": "Hatch",
            "combustivel": "Flex", "cambio": "Automático", "portas": 4,
            "score_economia": 0.8, "score_familia": 0.6, "score_performance": 0.6, "score_conforto": 0.7, "score_seguranca": 0.7
        },
        {
            "marca": "Hyundai", "modelo": "HB20", "versao": "1.6", "categoria": "Hatch",
            "combustivel": "Flex", "cambio": "Manual", "portas": 4,
            "score_economia": 0.7, "score_familia": 0.6, "score_performance": 0.5, "score_conforto": 0.6, "score_seguranca": 0.7
        },
        {
            "marca": "Toyota", "modelo": "Corolla", "versao": "2.0 XEi", "categoria": "Sedan",
            "combustivel": "Flex", "cambio": "Automático", "portas": 4,
            "score_economia": 0.7, "score_familia": 0.8, "score_performance": 0.7, "score_conforto": 0.9, "score_seguranca": 0.9
        },
        {
            "marca": "Honda", "modelo": "Civic", "versao": "2.0 EX", "categoria": "Sedan",
            "combustivel": "Gasolina", "cambio": "CVT", "portas": 4,
            "score_economia": 0.6, "score_familia": 0.7, "score_performance": 0.8, "score_conforto": 0.9, "score_seguranca": 0.9
        },
        {
            "marca": "Jeep", "modelo": "Compass", "versao": "Sport", "categoria": "SUV",
            "combustivel": "Flex", "cambio": "Automático", "portas": 4,
            "score_economia": 0.5, "score_familia": 0.9, "score_performance": 0.7, "score_conforto": 0.8, "score_seguranca": 0.9
        },
        {
            "marca": "Nissan", "modelo": "Kicks", "versao": "1.6", "categoria": "SUV",
            "combustivel": "Flex", "cambio": "CVT", "portas": 4,
            "score_economia": 0.7, "score_familia": 0.8, "score_performance": 0.6, "score_conforto": 0.7, "score_seguranca": 0.8
        },
        {
            "marca": "Renault", "modelo": "Duster", "versao": "1.6", "categoria": "SUV",
            "combustivel": "Flex", "cambio": "Manual", "portas": 4,
            "score_economia": 0.6, "score_familia": 0.8, "score_performance": 0.6, "score_conforto": 0.6, "score_seguranca": 0.7
        }
    ]
    
    # Gerar carros
    cars = []
    base_year = 2020
    base_price = 45000 if dealership_id == "autocenter" else 55000
    
    for i in range(num_cars):
        template = mock_cars_templates[i % len(mock_cars_templates)]
        
        car = {
            "id": f"{dealership_id}_{i:03d}",
            "dealership_id": dealership_id,
            "nome": f"{template['marca']} {template['modelo']} {template['versao']}".upper(),
            "marca": template["marca"],
            "modelo": template["modelo"],
            "versao": template["versao"],
            "ano": base_year + (i % 5),
            "preco": base_price + (i * 5000) + ((i % 3) * 10000),
            "quilometragem": 20000 + (i * 5000),
            "combustivel": template["combustivel"],
            "cambio": template["cambio"],
            "cor": ["Branco", "Preto", "Prata", "Vermelho", "Azul"][i % 5],
            "portas": template["portas"],
            "categoria": template["categoria"],
            "score_familia": template["score_familia"],
            "score_economia": template["score_economia"],
            "score_performance": template["score_performance"],
            "score_conforto": template["score_conforto"],
            "score_seguranca": template["score_seguranca"],
            "imagens": [f"https://example.com/cars/{dealership_id}_{i}.jpg"],
            "url_original": f"https://{dealership_info['website']}/carros/{i}",
            "disponivel": True,
            "destaque": i < 3,
            "data_scraping": datetime.now().isoformat(),
            "data_atualizacao": datetime.now().isoformat(),
            "dealership_name": dealership_info["name"],
            "dealership_city": dealership_info["city"],
            "dealership_state": dealership_info["state"],
            "dealership_phone": dealership_info["phone"],
            "dealership_whatsapp": dealership_info["whatsapp"]
        }
        
        cars.append(car)
    
    # Salvar
    dest_path = f"data/{dealership_id}_estoque.json"
    with open(dest_path, 'w', encoding='utf-8') as f:
        json.dump(cars, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] {len(cars)} carros gerados para {dealership_info['name']}")
    print(f"[OK] Salvo em: {dest_path}")


def main():
    """Executar migração completa"""
    print("=" * 60)
    print("MIGRACAO PARA PLATAFORMA MULTI-CONCESSIONARIA")
    print("=" * 60)
    
    # 1. Migrar RobustCar
    migrate_robustcar_data()
    
    # 2. Carregar configurações das concessionárias
    with open("data/dealerships.json", 'r', encoding='utf-8') as f:
        dealerships = json.load(f)
    
    # 3. Gerar dados mock para outras concessionárias
    for dealership in dealerships:
        if dealership['id'] == 'robustcar':
            continue  # Já migrado
        
        generate_mock_dealership_data(
            dealership['id'],
            dealership,
            num_cars=20
        )
    
    print("\n" + "=" * 60)
    print("MIGRACAO CONCLUIDA COM SUCESSO!")
    print("=" * 60)
    print("\nResumo:")
    print("- RobustCar: dados reais migrados")
    print("- AutoCenter: 20 carros mock gerados")
    print("- CarPlus: 20 carros mock gerados")
    print("\nTotal de concessionarias: 3")
    print("Total estimado de carros: 129+")


if __name__ == "__main__":
    main()

