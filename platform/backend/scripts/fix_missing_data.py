"""
Corrigir dados faltantes: câmbio e quilometragem
Aplicar estimativas realistas baseadas em marca/modelo/ano
"""

import json
import random
import os
import sys
from datetime import datetime

# Adicionar backend ao path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


def estimate_km(ano):
    """
    Estimar quilometragem baseado no ano
    Média: 15.000 km/ano com variação
    """
    current_year = 2025
    years_old = current_year - ano
    
    if years_old <= 0:
        # Carros 2025: 0-5k km
        return random.randint(0, 5000)
    elif years_old == 1:
        # Carros 2024: 10-25k km
        return random.randint(10000, 25000)
    elif years_old == 2:
        # Carros 2023: 25-45k km
        return random.randint(25000, 45000)
    elif years_old == 3:
        # Carros 2022: 45-65k km
        return random.randint(45000, 65000)
    elif years_old == 4:
        # Carros 2021: 65-85k km
        return random.randint(65000, 85000)
    else:
        # Carros 2020 ou anterior: 85-150k km
        return random.randint(85000, 150000)


def estimate_cambio(marca, modelo, ano):
    """
    Estimar câmbio baseado em marca/modelo/ano
    Usa conhecimento do mercado automotivo brasileiro
    """
    modelo_lower = modelo.lower()
    marca_lower = marca.lower()
    
    # Marcas premium: sempre automático
    if marca_lower in ['volvo', 'bmw', 'audi', 'mercedes', 'lexus', 'land rover']:
        return "Automático"
    
    # Modelos que geralmente são automáticos (médios/grandes)
    modelos_automaticos = [
        'corolla', 'civic', 'accord', 'camry',  # Sedãs médios
        'tracker', 'compass', 'renegade', 'tiguan', 'tucson', 'sportage',  # SUVs
        'kicks', 'creta', 'hr-v', 't-cross',  # SUVs compactos
        'hilux', 'ranger', 'frontier', 's10', 'toro'  # Pickups
    ]
    
    for modelo_auto in modelos_automaticos:
        if modelo_auto in modelo_lower:
            # Carros mais novos têm maior chance de ser automático
            if ano >= 2022:
                # 80% automático, 20% manual
                return random.choices(
                    ["Automático CVT" if modelo_auto in ['corolla', 'civic', 'kicks', 'hr-v'] else "Automático", "Manual"],
                    weights=[80, 20]
                )[0]
            elif ano >= 2020:
                # 60% automático, 40% manual
                return random.choices(["Automático", "Manual"], weights=[60, 40])[0]
            else:
                # 40% automático, 60% manual
                return random.choices(["Automático", "Manual"], weights=[40, 60])[0]
    
    # Modelos populares/compactos: geralmente manual
    modelos_manuais = [
        'onix', 'hb20', 'gol', 'kwid', 'mobi', 'argo', 'polo',
        'ka', 'fiesta', 'sandero', 'logan', 'etios', 'prisma'
    ]
    
    for modelo_manual in modelos_manuais:
        if modelo_manual in modelo_lower:
            # Carros mais novos têm mais chance de ter automático
            if ano >= 2023:
                # 50% manual, 50% automático
                return random.choices(["Manual", "Automático"], weights=[50, 50])[0]
            elif ano >= 2020:
                # 70% manual, 30% automático
                return random.choices(["Manual", "Automático"], weights=[70, 30])[0]
            else:
                # 85% manual, 15% automático
                return random.choices(["Manual", "Automático"], weights=[85, 15])[0]
    
    # Padrão: baseado no ano
    if ano >= 2023:
        return random.choices(["Manual", "Automático"], weights=[50, 50])[0]
    elif ano >= 2020:
        return random.choices(["Manual", "Automático"], weights=[65, 35])[0]
    else:
        return random.choices(["Manual", "Automático"], weights=[75, 25])[0]


def fix_data():
    """Corrigir dados faltantes no estoque"""
    
    data_file = os.path.join(backend_dir, "data", "robustcar_estoque.json")
    backup_file = os.path.join(backend_dir, "data", "robustcar_estoque_backup.json")
    
    print("\n" + "="*80)
    print("🔧 CORREÇÃO DE DADOS FALTANTES")
    print("="*80)
    
    # Fazer backup
    print("\n1. Criando backup...")
    with open(data_file, 'r', encoding='utf-8') as f:
        cars = json.load(f)
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(cars, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Backup criado: {backup_file}")
    print(f"   Total de carros: {len(cars)}")
    
    # Estatísticas
    cambios_corrigidos = 0
    km_corrigidos = 0
    
    print("\n2. Aplicando correções...")
    
    for car in cars:
        # Corrigir câmbio se for "Manual" (todos estão assim)
        if car.get('cambio') == 'Manual':
            novo_cambio = estimate_cambio(car['marca'], car['modelo'], car['ano'])
            if novo_cambio != 'Manual':
                car['cambio'] = novo_cambio
                cambios_corrigidos += 1
        
        # Corrigir quilometragem se for 0 e ano < 2024
        if car.get('quilometragem', 0) == 0 and car['ano'] < 2024:
            nova_km = estimate_km(car['ano'])
            car['quilometragem'] = nova_km
            km_corrigidos += 1
        
        # Atualizar data de atualização
        car['data_atualizacao'] = datetime.now().isoformat()
    
    print(f"   ✅ Câmbios corrigidos: {cambios_corrigidos}")
    print(f"   ✅ Quilometragens corrigidas: {km_corrigidos}")
    
    # Salvar dados corrigidos
    print("\n3. Salvando dados corrigidos...")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(cars, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Arquivo atualizado: {data_file}")
    
    # Mostrar estatísticas finais
    print("\n" + "="*80)
    print("📊 ESTATÍSTICAS APÓS CORREÇÃO")
    print("="*80)
    
    # Câmbios
    from collections import Counter
    cambios = Counter(car['cambio'] for car in cars)
    print("\nDistribuição de Câmbios:")
    for cambio, count in cambios.most_common():
        percentage = (count / len(cars)) * 100
        print(f"  {cambio}: {count} carros ({percentage:.1f}%)")
    
    # Quilometragem
    km_zero = sum(1 for car in cars if car['quilometragem'] == 0)
    km_baixa = sum(1 for car in cars if 0 < car['quilometragem'] < 30000)
    km_media = sum(1 for car in cars if 30000 <= car['quilometragem'] <= 80000)
    km_alta = sum(1 for car in cars if car['quilometragem'] > 80000)
    
    print("\nDistribuição de Quilometragem:")
    print(f"  0 km: {km_zero} carros ({km_zero/len(cars)*100:.1f}%)")
    print(f"  < 30.000 km: {km_baixa} carros ({km_baixa/len(cars)*100:.1f}%)")
    print(f"  30.000 - 80.000 km: {km_media} carros ({km_media/len(cars)*100:.1f}%)")
    print(f"  > 80.000 km: {km_alta} carros ({km_alta/len(cars)*100:.1f}%)")
    
    # Exemplos
    print("\n" + "="*80)
    print("📋 EXEMPLOS DE CORREÇÕES")
    print("="*80)
    
    print("\nCarros com câmbio automático (exemplos):")
    automaticos = [car for car in cars if 'Automático' in car['cambio']][:5]
    for car in automaticos:
        print(f"  - {car['nome']} ({car['ano']}) - {car['cambio']}")
    
    print("\nCarros com quilometragem realista (exemplos):")
    com_km = [car for car in cars if car['quilometragem'] > 0][:5]
    for car in com_km:
        print(f"  - {car['nome']} ({car['ano']}) - {car['quilometragem']:,} km")
    
    print("\n" + "="*80)
    print("✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print(f"\nBackup disponível em: {backup_file}")
    print("Para reverter: copie o backup de volta para robustcar_estoque.json")
    print("\n⚠️  IMPORTANTE: Estas são estimativas temporárias!")
    print("Corrija o scraper para obter dados reais.")


if __name__ == "__main__":
    # Verificar se há argumento --force
    import sys
    force = '--force' in sys.argv or '-f' in sys.argv
    
    if not force:
        # Confirmar antes de executar
        print("\n⚠️  ATENÇÃO: Este script irá modificar os dados de estoque!")
        print("Um backup será criado automaticamente.")
        
        resposta = input("\nDeseja continuar? (s/n): ")
        
        if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
            print("\n❌ Operação cancelada.")
            sys.exit(0)
    
    fix_data()
