#!/usr/bin/env python3
"""
Script para adicionar RP Multimarcas ao arquivo dealerships.json
"""

import json
from datetime import datetime

# Carrega dealerships existentes
with open('platform/backend/data/dealerships.json', 'r', encoding='utf-8') as f:
    dealerships = json.load(f)

# Remove entrada antiga da RP Multimarcas se existir
dealerships = [d for d in dealerships if d.get('id') != 'rpmultimarcas_001']

# Carrega veículos da RP Multimarcas
with open('platform/backend/data/rpmultimarcas_estoque.json', 'r', encoding='utf-8') as f:
    rp_vehicles = json.load(f)

# Adiciona informações da concessionária aos veículos
for vehicle in rp_vehicles:
    vehicle['dealership_id'] = 'rpmultimarcas'
    vehicle['dealership_name'] = 'RP Multimarcas'
    vehicle['dealership_city'] = 'São Paulo'
    vehicle['dealership_state'] = 'SP'
    vehicle['dealership_phone'] = '(11) 5050-8288'
    vehicle['dealership_whatsapp'] = '5511940360465'
    vehicle['destaque'] = False
    
    # Adiciona scores padrão se não existirem
    if 'score_familia' not in vehicle:
        vehicle['score_familia'] = 0.6
    if 'score_economia' not in vehicle:
        vehicle['score_economia'] = 0.7
    if 'score_performance' not in vehicle:
        vehicle['score_performance'] = 0.5
    if 'score_conforto' not in vehicle:
        vehicle['score_conforto'] = 0.5
    if 'score_seguranca' not in vehicle:
        vehicle['score_seguranca'] = 0.5

# Cria entrada da concessionária
rp_dealership = {
    "id": "rpmultimarcas_001",
    "nome": "RP Multimarcas",
    "cidade": "São Paulo",
    "estado": "SP",
    "telefone": "(11) 5050-8288",
    "whatsapp": "5511940360465",
    "endereco": "Av. Marechal Tito, 5385 - São Paulo - SP - 08115-100",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "carros": rp_vehicles,
    "categoria": "Multimarcas"
}

# Adiciona ao array de concessionárias
dealerships.append(rp_dealership)

# Salva arquivo atualizado
with open('platform/backend/data/dealerships.json', 'w', encoding='utf-8') as f:
    json.dump(dealerships, f, ensure_ascii=False, indent=2)

print(f"✅ RP Multimarcas adicionada com {len(rp_vehicles)} veículos!")
print(f"📊 Total de concessionárias: {len(dealerships)}")
