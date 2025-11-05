"""
Valida URLs de imagens e remove carros com imagens quebradas
"""
import json
import os
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple

def check_image_url(url: str, timeout: int = 5) -> bool:
    """
    Verifica se uma URL de imagem é válida
    """
    try:
        # Fazer HEAD request para verificar se a URL existe
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        
        # Verificar se o status é OK (200-299)
        if 200 <= response.status_code < 300:
            # Verificar se é realmente uma imagem
            content_type = response.headers.get('content-type', '').lower()
            if 'image' in content_type:
                return True
        
        return False
    except Exception as e:
        print(f"    ❌ Erro ao verificar {url[:50]}...: {str(e)[:50]}")
        return False


def validate_car_images(car: Dict, check_urls: bool = True) -> Tuple[bool, List[str]]:
    """
    Valida as imagens de um carro
    Retorna (tem_imagens_validas, lista_urls_validas)
    """
    valid_images = []
    
    # Verificar campo 'imagens' (lista)
    if 'imagens' in car and car['imagens']:
        if isinstance(car['imagens'], list):
            for img in car['imagens']:
                if not img or not img.strip():
                    continue
                
                # Verificar se é URL válida
                if not img.startswith('http'):
                    continue
                
                # Se check_urls=True, verificar se a URL funciona
                if check_urls:
                    if check_image_url(img):
                        valid_images.append(img)
                else:
                    valid_images.append(img)
    
    # Verificar campo 'imagem' (string única)
    if not valid_images and 'imagem' in car and car['imagem']:
        img = car['imagem'].strip()
        if img.startswith('http'):
            if check_urls:
                if check_image_url(img):
                    valid_images.append(img)
            else:
                valid_images.append(img)
    
    return len(valid_images) > 0, valid_images


def validate_and_clean_stock(check_urls: bool = False):
    """
    Valida e limpa o estoque
    check_urls: Se True, faz requisição HTTP para validar cada URL (mais lento)
    """
    
    # Diretório de dados
    backend_dir = Path(__file__).parent.parent
    data_dir = backend_dir / "data"
    
    # Arquivos de estoque
    estoque_files = [
        "robustcar_estoque.json",
        "rpmultimarcas_estoque.json"
    ]
    
    total_removed = 0
    total_kept = 0
    total_fixed = 0
    
    for filename in estoque_files:
        filepath = data_dir / filename
        
        if not filepath.exists():
            print(f"⚠️  Arquivo não encontrado: {filename}")
            continue
        
        print(f"\n📁 Processando: {filename}")
        
        # Ler arquivo
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        original_count = len(data)
        
        # Filtrar carros COM imagens válidas
        filtered_data = []
        removed_cars = []
        fixed_cars = []
        
        for i, car in enumerate(data):
            print(f"  Verificando {i+1}/{original_count}: {car.get('nome', 'Desconhecido')[:40]}...", end='\r')
            
            has_valid_images, valid_images = validate_car_images(car, check_urls=check_urls)
            
            if has_valid_images:
                # Atualizar lista de imagens com apenas as válidas
                original_image_count = len(car.get('imagens', []))
                car['imagens'] = valid_images
                
                if original_image_count != len(valid_images):
                    fixed_cars.append({
                        'nome': car.get('nome', 'Desconhecido'),
                        'original': original_image_count,
                        'validas': len(valid_images)
                    })
                
                filtered_data.append(car)
            else:
                removed_cars.append({
                    'nome': car.get('nome', 'Desconhecido'),
                    'marca': car.get('marca', ''),
                    'modelo': car.get('modelo', ''),
                    'preco': car.get('preco', 0)
                })
        
        print()  # Nova linha após o loop
        
        # Estatísticas
        removed_count = original_count - len(filtered_data)
        fixed_count = len(fixed_cars)
        total_removed += removed_count
        total_kept += len(filtered_data)
        total_fixed += fixed_count
        
        print(f"  Original: {original_count} carros")
        print(f"  Mantidos: {len(filtered_data)} carros")
        print(f"  Corrigidos: {fixed_count} carros (imagens inválidas removidas)")
        print(f"  Removidos: {removed_count} carros (sem imagens válidas)")
        
        # Mostrar carros corrigidos
        if fixed_cars:
            print(f"\n  🔧 Carros com imagens corrigidas:")
            for car in fixed_cars[:5]:
                print(f"    - {car['nome']}: {car['original']} → {car['validas']} imagens")
            if len(fixed_cars) > 5:
                print(f"    ... e mais {len(fixed_cars) - 5} carros")
        
        # Mostrar carros removidos
        if removed_cars:
            print(f"\n  ❌ Carros removidos (sem imagens válidas):")
            for car in removed_cars[:5]:
                print(f"    - {car['nome']} - R$ {car['preco']:,.2f}")
            if len(removed_cars) > 5:
                print(f"    ... e mais {len(removed_cars) - 5} carros")
        
        # Criar backup
        backup_path = data_dir / f"{filename}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  💾 Backup criado: {backup_path.name}")
        
        # Salvar arquivo filtrado
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ Arquivo atualizado: {filename}")
    
    # Resumo final
    print(f"\n{'='*60}")
    print(f"📊 RESUMO FINAL")
    print(f"{'='*60}")
    print(f"Total mantidos: {total_kept} carros")
    print(f"Total corrigidos: {total_fixed} carros (imagens inválidas removidas)")
    print(f"Total removidos: {total_removed} carros (sem imagens válidas)")
    print(f"{'='*60}")
    
    return total_kept, total_fixed, total_removed


if __name__ == "__main__":
    print("🚗 Validando imagens do estoque...")
    print("="*60)
    print("\n⚠️  MODO RÁPIDO: Validando apenas formato de URL")
    print("   (Não verifica se a URL funciona)")
    print("   Para validação completa, use: check_urls=True")
    print()
    
    kept, fixed, removed = validate_and_clean_stock(check_urls=False)
    
    print(f"\n✅ Processo concluído!")
    print(f"   {kept} carros mantidos")
    print(f"   {fixed} carros corrigidos")
    print(f"   {removed} carros removidos")
    print(f"\n💡 Backups criados com extensão .backup")
