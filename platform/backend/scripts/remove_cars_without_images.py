"""
Remove carros sem imagens dos arquivos de estoque
"""
import json
import os
from pathlib import Path

def remove_cars_without_images():
    """Remove carros que não têm imagens"""
    
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
        
        # Filtrar carros COM imagens
        filtered_data = []
        removed_cars = []
        
        for car in data:
            # Verificar se tem imagens VÁLIDAS
            has_images = False
            
            # Palavras-chave que indicam imagem inválida
            invalid_keywords = [
                'placeholder',
                'carregando',
                'loading',
                'no-image',
                'sem-imagem',
                'default',
                'coming-soon'
            ]
            
            # Verificar campo 'imagens' (lista)
            if 'imagens' in car and car['imagens']:
                if isinstance(car['imagens'], list) and len(car['imagens']) > 0:
                    # Filtrar imagens válidas
                    valid_images = []
                    for img in car['imagens']:
                        if not img or not img.strip():
                            continue
                        
                        img_lower = img.lower()
                        
                        # Verificar se não contém palavras-chave inválidas
                        if any(keyword in img_lower for keyword in invalid_keywords):
                            continue
                        
                        # Verificar se é uma URL válida (começa com http)
                        if not img.startswith('http'):
                            continue
                        
                        valid_images.append(img)
                    
                    if valid_images:
                        has_images = True
                        # Atualizar lista de imagens com apenas as válidas
                        car['imagens'] = valid_images
            
            # Verificar campo 'imagem' (string única)
            if not has_images and 'imagem' in car and car['imagem']:
                img = car['imagem'].strip()
                img_lower = img.lower()
                
                # Verificar se não contém palavras-chave inválidas
                if not any(keyword in img_lower for keyword in invalid_keywords):
                    # Verificar se é uma URL válida
                    if img.startswith('http'):
                        has_images = True
            
            if has_images:
                filtered_data.append(car)
            else:
                removed_cars.append({
                    'nome': car.get('nome', 'Desconhecido'),
                    'marca': car.get('marca', ''),
                    'modelo': car.get('modelo', ''),
                    'preco': car.get('preco', 0)
                })
        
        # Estatísticas
        removed_count = original_count - len(filtered_data)
        total_removed += removed_count
        total_kept += len(filtered_data)
        
        print(f"  Original: {original_count} carros")
        print(f"  Mantidos: {len(filtered_data)} carros (com imagens)")
        print(f"  Removidos: {removed_count} carros (sem imagens)")
        
        # Mostrar alguns carros removidos
        if removed_cars:
            print(f"\n  📋 Exemplos de carros removidos:")
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
    print(f"Total mantidos: {total_kept} carros (com imagens)")
    print(f"Total removidos: {total_removed} carros (sem imagens)")
    print(f"{'='*60}")
    
    return total_kept, total_removed


if __name__ == "__main__":
    print("🚗 Removendo carros sem imagens do estoque...")
    print("="*60)
    
    kept, removed = remove_cars_without_images()
    
    print(f"\n✅ Processo concluído!")
    print(f"   {kept} carros mantidos")
    print(f"   {removed} carros removidos")
    print(f"\n💡 Backups criados com extensão .backup")
