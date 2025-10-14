"""
Script para organizar arquivos da pasta raiz do projeto FacilIAuto
Move arquivos de documentação para pastas apropriadas
"""

import os
import shutil
from pathlib import Path

def organize_root():
    """Organizar arquivos da raiz do projeto"""
    
    # Configuração de movimentação de arquivos
    moves = {
        # Relatórios e resumos de implementação -> docs/reports/
        'docs/reports/': [
            'AVALIACAO-SISTEMA-RECOMENDACAO.md',
            'EXECUCAO-TESTES-SUCESSO.md',
            'FASE1-IMPLEMENTADA.md',
            'FASE1-VISUAL-SUMMARY.md',
            'FASE2-IMPLEMENTADA-COMPLETA.md',
            'RELATORIO-TESTES-3-FASES.md',
            'RESPOSTA-XP-E2E.md',
            'RESULTADO-TESTES-PLATAFORMA.md',
            'RESUMO-FASE1-COMPLETA.md',
            'STATUS-XP-E2E.md',
            'TESTES-IMPLEMENTADOS-SUCESSO.md',
            'TODAS-FASES-100-COMPLETAS.md',
            'TODAS-FASES-COMPLETAS.md',
        ],
        
        # Guias de execução -> docs/guides/
        'docs/guides/': [
            'COMO-EXECUTAR.md',
            'COMO-TESTAR-GALERIA.md',
        ],
        
        # Troubleshooting e correções -> docs/troubleshooting/
        'docs/troubleshooting/': [
            'CORRECAO-ERRO-500.md',
            'RESTART-NOW.bat',
            'restart-backend.bat',
        ],
        
        # Documentação geral -> docs/
        'docs/': [
            'REORGANIZACAO-ESTRUTURA.md',
            'RESUMO-GALERIA-FOTOS.md',
        ],
        
        # Implementação -> docs/implementation/
        'docs/implementation/': [
            'TRANSPORTE-PASSAGEIROS-IMPLEMENTADO.md',
        ],
    }
    
    print("=" * 70)
    print("ORGANIZANDO PASTA RAIZ DO PROJETO FACILIAUTO")
    print("=" * 70)
    
    moved_count = 0
    skipped_count = 0
    error_count = 0
    
    for target_dir, files in moves.items():
        # Criar diretório de destino se não existir
        os.makedirs(target_dir, exist_ok=True)
        
        for file in files:
            source = file
            destination = os.path.join(target_dir, file)
            
            if os.path.exists(source):
                try:
                    shutil.move(source, destination)
                    print(f"[OK] Movido: {file} -> {target_dir}")
                    moved_count += 1
                except Exception as e:
                    print(f"[ERRO] {file}: {e}")
                    error_count += 1
            else:
                print(f"[SKIP] Arquivo nao encontrado: {file}")
                skipped_count += 1
    
    print("\n" + "=" * 70)
    print("RESUMO DA ORGANIZACAO")
    print("=" * 70)
    print(f"Arquivos movidos: {moved_count}")
    print(f"Arquivos ignorados (nao encontrados): {skipped_count}")
    print(f"Erros: {error_count}")
    print("=" * 70)
    
    # Listar arquivos que permanecem na raiz
    print("\nARQUIVOS QUE PERMANECEM NA RAIZ:")
    print("-" * 70)
    
    root_files = []
    for item in os.listdir('.'):
        if os.path.isfile(item):
            root_files.append(item)
    
    # Categorizar arquivos na raiz
    essential = []
    scripts = []
    other = []
    
    for file in sorted(root_files):
        if file in ['README.md', 'LICENSE', 'PROJECT-SUMMARY.md', 'CONTRIBUTING.md', 'FOR-RECRUITERS.md']:
            essential.append(file)
        elif file.endswith('.bat') or file.endswith('.sh') or file.endswith('.py'):
            scripts.append(file)
        else:
            other.append(file)
    
    print("\n[ESSENCIAIS] Documentacao principal:")
    for f in essential:
        print(f"  - {f}")
    
    print("\n[SCRIPTS] Scripts de execucao:")
    for f in scripts:
        print(f"  - {f}")
    
    if other:
        print("\n[OUTROS] Outros arquivos:")
        for f in other:
            print(f"  - {f}")
    
    print("\n" + "=" * 70)
    print("[SUCESSO] Pasta raiz organizada!")
    print("=" * 70)

if __name__ == "__main__":
    organize_root()

