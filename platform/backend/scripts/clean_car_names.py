#!/usr/bin/env python3
"""
Script para limpar nomes de carros mal formatados
Remove informações desnecessárias e padroniza os nomes
"""

import json
import re
from pathlib import Path


def clean_car_name(raw_name: str, marca: str) -> str:
    """
    Limpar nome do carro removendo informações desnecessárias
    
    Exemplos:
    - "FIAT MOBI LIKEFLEXCINZA202399.057ROBUST" -> "Fiat Mobi Like"
    - "CHEVROLET ONIX PLUS LT 1.0 TURBO" -> "Chevrolet Onix Plus LT"
    - "FORD ECOSPORT 2.0 TITANIUM" -> "Ford EcoSport Titanium"
    """
    if not raw_name:
        return ""
    
    # Converter para title case
    name = raw_name.strip()
    
    # Remover padrões comuns de poluição
    # 1. Remover cores (BRANCO, PRETO, CINZA, etc.)
    cores = ['BRANCO', 'PRETO', 'CINZA', 'PRATA', 'VERMELHO', 'AZUL', 'VERDE', 
             'AMARELO', 'LARANJA', 'ROXO', 'ROSA', 'MARROM', 'BEGE']
    for cor in cores:
        name = re.sub(rf'\b{cor}\b', '', name, flags=re.IGNORECASE)
    
    # 2. Remover combustível (FLEX, GASOLINA, DIESEL, etc.)
    combustiveis = ['FLEX', 'GASOLINA', 'DIESEL', 'ELETRICO', 'HIBRIDO', 'GNV']
    for comb in combustiveis:
        name = re.sub(rf'\b{comb}\b', '', name, flags=re.IGNORECASE)
    
    # 3. Remover anos (2019, 2020, 2021, etc.)
    name = re.sub(r'\b20\d{2}\b', '', name)
    
    # 4. Remover números de identificação (202399.057, etc.)
    name = re.sub(r'\d+\.\d+', '', name)
    
    # 5. Remover palavras como ROBUST, USADO, SEMINOVO, etc.
    palavras_remover = ['ROBUST', 'USADO', 'SEMINOVO', 'NOVO', 'ZERO', 'KM']
    for palavra in palavras_remover:
        name = re.sub(rf'\b{palavra}\b', '', name, flags=re.IGNORECASE)
    
    # 5.1. Remover padrões específicos problemáticos (palavras grudadas)
    # Remove tudo após FLEX/GASOLINA/DIESEL quando grudado com outras palavras
    name = re.sub(r'(flex|gasolina|diesel)\w*', '', name, flags=re.IGNORECASE)
    
    # 6. Remover múltiplos espaços
    name = re.sub(r'\s+', ' ', name).strip()
    
    # 7. Converter para Title Case
    name = name.title()
    
    # 8. Correções específicas de marcas
    name = name.replace('Ecosport', 'EcoSport')
    name = name.replace('Hb20', 'HB20')
    name = name.replace('Hr-V', 'HR-V')
    name = name.replace('Wr-V', 'WR-V')
    name = name.replace('T-Cross', 'T-Cross')
    
    return name


def clean_car_data(input_file: str, output_file: str = None):
    """
    Limpar dados de carros em um arquivo JSON
    """
    if output_file is None:
        output_file = input_file
    
    print(f"\n📂 Lendo arquivo: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        cars = json.load(f)
    
    print(f"📊 Total de carros: {len(cars)}")
    
    cleaned_count = 0
    changes = []
    
    for car in cars:
        old_name = car.get('nome', '')
        marca = car.get('marca', '')
        
        # Limpar nome
        new_name = clean_car_name(old_name, marca)
        
        if new_name != old_name and new_name:
            car['nome'] = new_name
            cleaned_count += 1
            changes.append({
                'old': old_name,
                'new': new_name,
                'marca': marca
            })
        
        # Limpar modelo também
        old_modelo = car.get('modelo', '')
        if old_modelo:
            new_modelo = clean_car_name(old_modelo, marca)
            if new_modelo != old_modelo and new_modelo:
                car['modelo'] = new_modelo
    
    print(f"\n✅ Nomes limpos: {cleaned_count}/{len(cars)}")
    
    # Mostrar exemplos de mudanças
    if changes:
        print("\n📝 Exemplos de mudanças:")
        for i, change in enumerate(changes[:10], 1):
            print(f"  {i}. {change['marca']}")
            print(f"     Antes: {change['old']}")
            print(f"     Depois: {change['new']}")
    
    # Salvar arquivo limpo
    print(f"\n💾 Salvando arquivo: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cars, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Arquivo salvo com sucesso!")
    
    return cleaned_count, changes


def main():
    """
    Limpar todos os arquivos de estoque
    """
    print("=" * 60)
    print("🧹 LIMPEZA DE NOMES DE CARROS")
    print("=" * 60)
    
    # Diretório de dados
    data_dir = Path(__file__).parent.parent / 'data'
    
    # Arquivos de estoque
    estoque_files = [
        'robustcar_estoque.json',
    ]
    
    # Limpar também o dealerships.json
    dealerships_file = data_dir / 'dealerships.json'
    if dealerships_file.exists():
        print("\n" + "=" * 60)
        print("🧹 LIMPANDO DEALERSHIPS.JSON")
        print("=" * 60)
        
        with open(dealerships_file, 'r', encoding='utf-8') as f:
            dealerships = json.load(f)
        
        total_cars = 0
        for dealership in dealerships:
            if 'carros' in dealership:
                for car in dealership['carros']:
                    # Limpar nome
                    old_name = car.get('nome', '')
                    marca = car.get('marca', '')
                    new_name = clean_car_name(old_name, marca)
                    if new_name != old_name and new_name:
                        car['nome'] = new_name
                        total_cars += 1
                    
                    # Limpar modelo também
                    old_modelo = car.get('modelo', '')
                    if old_modelo:
                        new_modelo = clean_car_name(old_modelo, marca)
                        if new_modelo != old_modelo and new_modelo:
                            car['modelo'] = new_modelo
        
        print(f"✅ Nomes limpos em dealerships.json: {total_cars}")
        
        with open(dealerships_file, 'w', encoding='utf-8') as f:
            json.dump(dealerships, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Arquivo salvo: {dealerships_file}")
    
    total_cleaned = 0
    all_changes = []
    
    for filename in estoque_files:
        filepath = data_dir / filename
        
        if filepath.exists():
            cleaned, changes = clean_car_data(str(filepath))
            total_cleaned += cleaned
            all_changes.extend(changes)
        else:
            print(f"⚠️  Arquivo não encontrado: {filepath}")
    
    print("\n" + "=" * 60)
    print(f"✅ TOTAL DE NOMES LIMPOS: {total_cleaned}")
    print("=" * 60)
    
    # Salvar relatório de mudanças
    if all_changes:
        report_file = data_dir / 'car_names_cleaning_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(all_changes, f, ensure_ascii=False, indent=2)
        print(f"\n📄 Relatório salvo em: {report_file}")


if __name__ == '__main__':
    main()
