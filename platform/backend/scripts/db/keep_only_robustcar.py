"""
Script para manter apenas a concessionária RobustCar (com imagens reais)
Remove outras concessionárias temporariamente
"""

import json

def keep_only_robustcar():
    """Manter apenas RobustCar no sistema"""
    
    print("=" * 70)
    print("MANTENDO APENAS ROBUSTCAR (COM IMAGENS REAIS)")
    print("=" * 70)
    
    # Carregar dados
    print("\n[1] Carregando concessionárias...")
    with open('data/dealerships.json', 'r', encoding='utf-8') as f:
        dealerships = json.load(f)
    
    print(f"    [INFO] Total antes: {len(dealerships)} concessionárias")
    
    # Filtrar apenas RobustCar
    print("\n[2] Filtrando apenas RobustCar...")
    robustcar_only = [d for d in dealerships if d.get('id') == 'robustcar_001']
    
    if not robustcar_only:
        print("    [ERRO] RobustCar não encontrada!")
        return False
    
    robustcar = robustcar_only[0]
    total_cars = len(robustcar.get('carros', []))
    
    print(f"    [OK] RobustCar encontrada")
    print(f"    [OK] {total_cars} carros")
    
    # Criar backup
    print("\n[3] Criando backup...")
    with open('data/dealerships_backup.json', 'w', encoding='utf-8') as f:
        json.dump(dealerships, f, ensure_ascii=False, indent=2)
    print(f"    [OK] Backup salvo em: data/dealerships_backup.json")
    
    # Salvar apenas RobustCar
    print("\n[4] Salvando apenas RobustCar...")
    with open('data/dealerships.json', 'w', encoding='utf-8') as f:
        json.dump([robustcar], f, ensure_ascii=False, indent=2)
    print(f"    [OK] Salvo em: data/dealerships.json")
    
    # Estatísticas
    cars_with_images = sum(
        1 for car in robustcar['carros'] 
        if car.get('imagens') and len(car['imagens']) > 0
    )
    
    print("\n" + "=" * 70)
    print("ESTATISTICAS FINAIS")
    print("=" * 70)
    print(f"Concessionarias ativas: 1 (RobustCar)")
    print(f"Total de carros: {total_cars}")
    print(f"Carros com imagens: {cars_with_images} ({cars_with_images/total_cars*100:.1f}%)")
    print("=" * 70)
    
    print("\n[SUCESSO] Agora apenas RobustCar esta ativa!")
    print("Todas as recomendacoes virao com imagens reais do S3!")
    
    return True

if __name__ == "__main__":
    keep_only_robustcar()

