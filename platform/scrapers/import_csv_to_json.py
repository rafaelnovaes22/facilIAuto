"""
Importar dados de veículos de CSV para JSON

Uso: python import_csv_to_json.py <arquivo.csv> [dealership_id]

Exemplo:
  python import_csv_to_json.py rpmultimarcas.csv rpmultimarcas
"""

import csv
import json
import sys
from datetime import datetime
import hashlib
from typing import Dict, List


def calculate_hash(data: Dict) -> str:
    """Calcular hash MD5 do conteúdo"""
    hashable = {k: v for k, v in data.items() if k not in ['id', 'data_scraping', 'content_hash']}
    content_str = json.dumps(hashable, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(content_str.encode('utf-8')).hexdigest()


def import_csv_to_json(csv_file: str, dealership_id: str = None, output_file: str = None):
    """
    Importar CSV para formato JSON do FacilIAuto
    
    Args:
        csv_file: Caminho do arquivo CSV
        dealership_id: ID da concessionária (ex: rpmultimarcas)
        output_file: Caminho do arquivo de saída (opcional)
    """
    
    # Determinar dealership_id do nome do arquivo se não fornecido
    if not dealership_id:
        dealership_id = csv_file.replace('.csv', '').replace('_', '').lower()
    
    # Determinar output_file se não fornecido
    if not output_file:
        output_file = f"{dealership_id}_estoque.json"
    
    print(f"\n📥 Importando dados de: {csv_file}")
    print(f"   Concessionária: {dealership_id}")
    
    vehicles = []
    errors = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader, 1):
                try:
                    # Validar campos obrigatórios
                    required_fields = ['nome', 'marca', 'modelo', 'ano', 'preco', 'quilometragem']
                    missing = [f for f in required_fields if not row.get(f)]
                    
                    if missing:
                        errors.append(f"Linha {i}: Campos obrigatórios faltando: {missing}")
                        continue
                    
                    # Converter tipos
                    vehicle = {
                        'id': f"{dealership_id}_{i}_{int(datetime.now().timestamp())}",
                        'nome': row['nome'].strip(),
                        'marca': row['marca'].strip(),
                        'modelo': row['modelo'].strip(),
                        'ano': int(row['ano']),
                        'preco': float(row['preco'].replace('.', '').replace(',', '.')),
                        'quilometragem': int(row['quilometragem'].replace('.', '').replace(',', '')),
                        'url_original': row.get('url_original', '').strip(),
                        'data_scraping': datetime.now().isoformat()
                    }
                    
                    # Campos opcionais
                    if row.get('combustivel'):
                        vehicle['combustivel'] = row['combustivel'].strip()
                    
                    if row.get('cambio'):
                        vehicle['cambio'] = row['cambio'].strip()
                    
                    if row.get('cor'):
                        vehicle['cor'] = row['cor'].strip()
                    
                    if row.get('portas'):
                        try:
                            vehicle['portas'] = int(row['portas'])
                        except ValueError:
                            pass
                    
                    if row.get('categoria'):
                        vehicle['categoria'] = row['categoria'].strip()
                    
                    if row.get('descricao'):
                        vehicle['descricao'] = row['descricao'].strip()
                    
                    # Imagens (separadas por ;)
                    if row.get('imagens'):
                        images = [img.strip() for img in row['imagens'].split(';') if img.strip()]
                        if images:
                            vehicle['imagens'] = images
                    
                    # Calcular hash
                    vehicle['content_hash'] = calculate_hash(vehicle)
                    
                    vehicles.append(vehicle)
                    print(f"   ✅ Linha {i}: {vehicle['nome']}")
                
                except Exception as e:
                    errors.append(f"Linha {i}: Erro ao processar - {e}")
                    print(f"   ❌ Linha {i}: {e}")
    
    except FileNotFoundError:
        print(f"\n❌ Arquivo não encontrado: {csv_file}")
        return False
    
    except Exception as e:
        print(f"\n❌ Erro ao ler CSV: {e}")
        return False
    
    # Mostrar resumo
    print(f"\n📊 Resumo da Importação:")
    print(f"   Total de linhas: {len(vehicles) + len(errors)}")
    print(f"   Importados com sucesso: {len(vehicles)}")
    print(f"   Erros: {len(errors)}")
    
    if errors:
        print(f"\n⚠️  Erros encontrados:")
        for error in errors[:10]:  # Mostrar apenas primeiros 10
            print(f"   - {error}")
        if len(errors) > 10:
            print(f"   ... e mais {len(errors) - 10} erros")
    
    if not vehicles:
        print(f"\n❌ Nenhum veículo válido para salvar")
        return False
    
    # Salvar JSON
    output = {
        'metadata': {
            'source': dealership_id,
            'method': 'manual_csv_import',
            'timestamp': datetime.now().isoformat(),
            'total_vehicles': len(vehicles),
            'csv_file': csv_file
        },
        'vehicles': vehicles
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Dados salvos com sucesso!")
        print(f"   Arquivo: {output_file}")
        print(f"   Veículos: {len(vehicles)}")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Erro ao salvar JSON: {e}")
        return False


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("\n❌ Uso incorreto")
        print("\nUso: python import_csv_to_json.py <arquivo.csv> [dealership_id]")
        print("\nExemplos:")
        print("  python import_csv_to_json.py rpmultimarcas.csv")
        print("  python import_csv_to_json.py rpmultimarcas.csv rpmultimarcas")
        print("  python import_csv_to_json.py autocenter.csv autocenter")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    dealership_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = import_csv_to_json(csv_file, dealership_id)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
