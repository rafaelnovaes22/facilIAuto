"""
Script para encontrar carros classificados incorretamente
"""
import json
import sys
from pathlib import Path

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.car_classifier import classifier

def check_classification():
    """Verificar classificações incorretas"""
    
    # Carregar estoques
    data_dir = Path(__file__).parent.parent / 'data'
    estoques = ['robustcar_estoque.json', 'autocenter_estoque.json', 'carplus_estoque.json']
    
    problemas = []
    
    for estoque_file in estoques:
        file_path = data_dir / estoque_file
        if not file_path.exists():
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            carros = json.load(f)
        
        for carro in carros:
            nome = carro.get('nome', '')
            modelo = carro.get('modelo', '')
            categoria_atual = carro.get('categoria', '')
            
            # Detectar motos
            if any(palavra in nome.lower() for palavra in ['moto', 'motorcycle', 'bike', 'scooter']):
                problemas.append({
                    'tipo': 'MOTO',
                    'nome': nome,
                    'categoria': categoria_atual,
                    'arquivo': estoque_file
                })
            
            # Detectar Focus Sedan
            if 'focus' in nome.lower() and 'sedan' in nome.lower() and categoria_atual == 'Hatch':
                problemas.append({
                    'tipo': 'SEDAN_COMO_HATCH',
                    'nome': nome,
                    'categoria': categoria_atual,
                    'arquivo': estoque_file
                })
            
            # Detectar Focus sem especificação (pode ser sedan)
            if 'focus' in nome.lower() and categoria_atual == 'Hatch':
                ano = carro.get('ano', 0)
                # Focus 2009-2013 era sedan no Brasil
                if 2009 <= ano <= 2013:
                    problemas.append({
                        'tipo': 'FOCUS_ANTIGO_SEDAN',
                        'nome': nome,
                        'ano': ano,
                        'categoria': categoria_atual,
                        'arquivo': estoque_file
                    })
    
    # Exibir problemas
    print(f"\n{'='*80}")
    print(f"PROBLEMAS DE CLASSIFICAÇÃO ENCONTRADOS: {len(problemas)}")
    print(f"{'='*80}\n")
    
    motos = [p for p in problemas if p['tipo'] == 'MOTO']
    if motos:
        print(f"\n🏍️  MOTOS CLASSIFICADAS COMO CARROS ({len(motos)}):")
        for p in motos[:10]:
            print(f"  - {p['nome']} → {p['categoria']} ({p['arquivo']})")
    
    focus_sedan = [p for p in problemas if 'SEDAN' in p['tipo']]
    if focus_sedan:
        print(f"\n🚗 SEDANS CLASSIFICADOS COMO HATCH ({len(focus_sedan)}):")
        for p in focus_sedan:
            print(f"  - {p['nome']} ({p.get('ano', 'N/A')}) → {p['categoria']} ({p['arquivo']})")
    
    return problemas

if __name__ == '__main__':
    problemas = check_classification()
    
    if problemas:
        print(f"\n\n⚠️  Total de problemas: {len(problemas)}")
        print("Execute o script de correção para resolver.")
    else:
        print("\n✅ Nenhum problema encontrado!")
