"""
Auditoria de Qualidade dos Dados
Verificar classificação, câmbio e quilometragem
"""

import json
import sys
import os
from collections import Counter

# Adicionar backend ao path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


def analyze_data_quality():
    """Analisar qualidade dos dados de estoque"""
    
    data_file = os.path.join(backend_dir, "data", "robustcar_estoque.json")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        cars = json.load(f)
    
    print("\n" + "="*80)
    print("🔍 AUDITORIA DE QUALIDADE DOS DADOS")
    print("="*80)
    print(f"\nTotal de carros: {len(cars)}")
    
    # Análise de Categoria
    print("\n" + "="*80)
    print("📊 ANÁLISE DE CATEGORIA (Classificação)")
    print("="*80)
    
    categorias = Counter()
    categorias_suspeitas = []
    
    for car in cars:
        categoria = car.get('categoria', 'N/A')
        categorias[categoria] += 1
        
        # Verificar se categoria faz sentido para o modelo
        nome = car.get('nome', '').lower()
        modelo = car.get('modelo', '').lower()
        
        # Casos suspeitos
        if 'suv' in nome or 'suv' in modelo:
            if categoria != 'SUV':
                categorias_suspeitas.append({
                    'nome': car['nome'],
                    'categoria_atual': categoria,
                    'categoria_esperada': 'SUV',
                    'motivo': 'Nome/modelo contém SUV'
                })
        
        if 'sedan' in nome or 'sedan' in modelo:
            if categoria not in ['Sedan', 'Sedan Compacto']:
                categorias_suspeitas.append({
                    'nome': car['nome'],
                    'categoria_atual': categoria,
                    'categoria_esperada': 'Sedan',
                    'motivo': 'Nome/modelo contém Sedan'
                })
        
        if 'hatch' in nome or 'hatch' in modelo:
            if categoria != 'Hatch':
                categorias_suspeitas.append({
                    'nome': car['nome'],
                    'categoria_atual': categoria,
                    'categoria_esperada': 'Hatch',
                    'motivo': 'Nome/modelo contém Hatch'
                })
        
        if 'pickup' in nome or 'pickup' in modelo or 'toro' in nome.lower() or 'ranger' in nome.lower():
            if categoria != 'Pickup':
                categorias_suspeitas.append({
                    'nome': car['nome'],
                    'categoria_atual': categoria,
                    'categoria_esperada': 'Pickup',
                    'motivo': 'Nome/modelo indica Pickup'
                })
    
    print("\nDistribuição de Categorias:")
    for categoria, count in categorias.most_common():
        percentage = (count / len(cars)) * 100
        print(f"  {categoria}: {count} carros ({percentage:.1f}%)")
    
    if categorias_suspeitas:
        print(f"\n⚠️  {len(categorias_suspeitas)} classificações suspeitas encontradas:")
        for i, caso in enumerate(categorias_suspeitas[:10], 1):
            print(f"\n  {i}. {caso['nome']}")
            print(f"     Categoria atual: {caso['categoria_atual']}")
            print(f"     Categoria esperada: {caso['categoria_esperada']}")
            print(f"     Motivo: {caso['motivo']}")
        
        if len(categorias_suspeitas) > 10:
            print(f"\n  ... e mais {len(categorias_suspeitas) - 10} casos")
    else:
        print("\n✅ Nenhuma classificação suspeita encontrada")
    
    # Análise de Câmbio
    print("\n" + "="*80)
    print("⚙️  ANÁLISE DE CÂMBIO")
    print("="*80)
    
    cambios = Counter()
    cambios_invalidos = []
    cambios_vazios = []
    
    for car in cars:
        cambio = car.get('cambio', '')
        
        if not cambio or cambio.strip() == '':
            cambios_vazios.append(car['nome'])
            cambios['[VAZIO]'] += 1
        else:
            cambios[cambio] += 1
            
            # Verificar se é um valor válido
            cambio_lower = cambio.lower()
            if not any(x in cambio_lower for x in ['manual', 'automático', 'automatico', 'cvt', 'automatizada']):
                cambios_invalidos.append({
                    'nome': car['nome'],
                    'cambio': cambio
                })
    
    print("\nDistribuição de Câmbios:")
    for cambio, count in cambios.most_common():
        percentage = (count / len(cars)) * 100
        status = "⚠️ " if cambio == '[VAZIO]' else ""
        print(f"  {status}{cambio}: {count} carros ({percentage:.1f}%)")
    
    if cambios_vazios:
        print(f"\n⚠️  {len(cambios_vazios)} carros SEM informação de câmbio:")
        for nome in cambios_vazios[:5]:
            print(f"  - {nome}")
        if len(cambios_vazios) > 5:
            print(f"  ... e mais {len(cambios_vazios) - 5} carros")
    
    if cambios_invalidos:
        print(f"\n⚠️  {len(cambios_invalidos)} carros com câmbio INVÁLIDO:")
        for caso in cambios_invalidos[:5]:
            print(f"  - {caso['nome']}: '{caso['cambio']}'")
        if len(cambios_invalidos) > 5:
            print(f"  ... e mais {len(cambios_invalidos) - 5} carros")
    
    if not cambios_vazios and not cambios_invalidos:
        print("\n✅ Todos os câmbios estão preenchidos corretamente")
    
    # Análise de Quilometragem
    print("\n" + "="*80)
    print("🚗 ANÁLISE DE QUILOMETRAGEM")
    print("="*80)
    
    km_stats = {
        'zero_km': 0,
        'baixa_km': 0,  # < 30k
        'media_km': 0,  # 30k - 80k
        'alta_km': 0,   # > 80k
        'invalida': 0
    }
    
    km_suspeitas = []
    
    for car in cars:
        km = car.get('quilometragem', 0)
        ano = car.get('ano', 2020)
        
        if km == 0:
            km_stats['zero_km'] += 1
            # Verificar se faz sentido ser 0km
            if ano < 2024:
                km_suspeitas.append({
                    'nome': car['nome'],
                    'ano': ano,
                    'km': km,
                    'motivo': f'Carro de {ano} com 0km é suspeito'
                })
        elif km < 30000:
            km_stats['baixa_km'] += 1
        elif km <= 80000:
            km_stats['media_km'] += 1
        else:
            km_stats['alta_km'] += 1
        
        # Verificar quilometragem muito alta para ano recente
        if ano >= 2023 and km > 50000:
            km_suspeitas.append({
                'nome': car['nome'],
                'ano': ano,
                'km': km,
                'motivo': f'Carro de {ano} com {km:,}km é muito alto'
            })
        
        # Verificar quilometragem muito baixa para ano antigo
        if ano <= 2018 and km < 20000:
            km_suspeitas.append({
                'nome': car['nome'],
                'ano': ano,
                'km': km,
                'motivo': f'Carro de {ano} com apenas {km:,}km é suspeito'
            })
    
    print("\nDistribuição de Quilometragem:")
    for categoria, count in km_stats.items():
        percentage = (count / len(cars)) * 100
        label = {
            'zero_km': '0 km (Zero KM)',
            'baixa_km': '< 30.000 km',
            'media_km': '30.000 - 80.000 km',
            'alta_km': '> 80.000 km',
            'invalida': 'Inválida'
        }[categoria]
        print(f"  {label}: {count} carros ({percentage:.1f}%)")
    
    if km_suspeitas:
        print(f"\n⚠️  {len(km_suspeitas)} quilometragens suspeitas encontradas:")
        for i, caso in enumerate(km_suspeitas[:10], 1):
            print(f"\n  {i}. {caso['nome']} ({caso['ano']})")
            print(f"     Quilometragem: {caso['km']:,} km")
            print(f"     Motivo: {caso['motivo']}")
        
        if len(km_suspeitas) > 10:
            print(f"\n  ... e mais {len(km_suspeitas) - 10} casos")
    else:
        print("\n✅ Nenhuma quilometragem suspeita encontrada")
    
    # Resumo Geral
    print("\n" + "="*80)
    print("📋 RESUMO DA AUDITORIA")
    print("="*80)
    
    total_problemas = len(categorias_suspeitas) + len(cambios_vazios) + len(cambios_invalidos) + len(km_suspeitas)
    
    print(f"\nTotal de carros analisados: {len(cars)}")
    print(f"Total de problemas encontrados: {total_problemas}")
    print(f"\nDetalhamento:")
    print(f"  - Classificações suspeitas: {len(categorias_suspeitas)}")
    print(f"  - Câmbios vazios: {len(cambios_vazios)}")
    print(f"  - Câmbios inválidos: {len(cambios_invalidos)}")
    print(f"  - Quilometragens suspeitas: {len(km_suspeitas)}")
    
    if total_problemas == 0:
        print("\n✅ QUALIDADE DOS DADOS: EXCELENTE")
        print("Todos os dados estão corretos e consistentes!")
    elif total_problemas < 10:
        print("\n⚠️  QUALIDADE DOS DADOS: BOA")
        print("Poucos problemas encontrados, revisar casos específicos.")
    elif total_problemas < 30:
        print("\n⚠️  QUALIDADE DOS DADOS: REGULAR")
        print("Alguns problemas encontrados, recomenda-se revisão.")
    else:
        print("\n❌ QUALIDADE DOS DADOS: RUIM")
        print("Muitos problemas encontrados, revisão urgente necessária!")
    
    # Recomendações
    print("\n" + "="*80)
    print("💡 RECOMENDAÇÕES")
    print("="*80)
    
    if categorias_suspeitas:
        print("\n1. CLASSIFICAÇÃO:")
        print("   - Revisar classificações suspeitas")
        print("   - Usar script: fix_vehicle_classification.py")
        print("   - Validar com base no nome/modelo do veículo")
    
    if cambios_vazios or cambios_invalidos:
        print("\n2. CÂMBIO:")
        print("   - Preencher câmbios vazios")
        print("   - Padronizar valores: 'Manual', 'Automático', 'Automático CVT'")
        print("   - Verificar fonte de dados original")
    
    if km_suspeitas:
        print("\n3. QUILOMETRAGEM:")
        print("   - Revisar quilometragens suspeitas")
        print("   - Verificar se 0km realmente são carros novos")
        print("   - Validar quilometragem vs ano do veículo")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    analyze_data_quality()
