"""
Sincronizar dealerships.json com robustcar_estoque.json
Os carros corrigidos estão em robustcar_estoque.json
Precisamos atualizar o dealerships.json
"""

import json
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Carregar estoque corrigido
estoque_file = os.path.join(backend_dir, "data", "robustcar_estoque.json")
with open(estoque_file, 'r', encoding='utf-8') as f:
    carros_corrigidos = json.load(f)

print(f"✅ Carregados {len(carros_corrigidos)} carros do estoque corrigido")

# Carregar dealerships
dealerships_file = os.path.join(backend_dir, "data", "dealerships.json")
with open(dealerships_file, 'r', encoding='utf-8') as f:
    dealerships = json.load(f)

print(f"✅ Carregadas {len(dealerships)} concessionárias")

# Fazer backup
backup_file = os.path.join(backend_dir, "data", "dealerships_backup.json")
with open(backup_file, 'w', encoding='utf-8') as f:
    json.dump(dealerships, f, indent=2, ensure_ascii=False)

print(f"✅ Backup criado: {backup_file}")

# Atualizar carros na concessionária RobustCar
for dealership in dealerships:
    if dealership['id'] == 'robustcar_001':
        print(f"\n📝 Atualizando {dealership['nome']}...")
        print(f"   Carros antes: {len(dealership.get('carros', []))}")
        
        # Substituir carros
        dealership['carros'] = carros_corrigidos
        
        print(f"   Carros depois: {len(dealership['carros'])}")
        
        # Verificar câmbios
        cambios = {}
        for car in dealership['carros']:
            cambio = car.get('cambio', 'N/A')
            cambios[cambio] = cambios.get(cambio, 0) + 1
        
        print(f"\n   Distribuição de câmbios:")
        for cambio, count in sorted(cambios.items(), key=lambda x: x[1], reverse=True):
            print(f"     {cambio}: {count} carros")

# Salvar dealerships atualizado
with open(dealerships_file, 'w', encoding='utf-8') as f:
    json.dump(dealerships, f, indent=2, ensure_ascii=False)

print(f"\n✅ Arquivo atualizado: {dealerships_file}")
print("\n🎉 Sincronização concluída com sucesso!")
