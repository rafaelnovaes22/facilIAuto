"""
Script de Reorganização da Estrutura do Projeto FacilIAuto
Executa movimentação segura de arquivos e pastas
"""
import os
import shutil
from pathlib import Path

def create_directory(path):
    """Criar diretório se não existir"""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"[OK] Criado: {path}")

def move_item(source, destination):
    """Mover arquivo ou pasta com segurança"""
    if os.path.exists(source):
        try:
            # Criar diretório de destino se necessário
            dest_dir = os.path.dirname(destination)
            if dest_dir:
                create_directory(dest_dir)
            
            # Mover
            shutil.move(source, destination)
            print(f"[OK] Movido: {source} -> {destination}")
            return True
        except Exception as e:
            print(f"[ERRO] Ao mover {source}: {e}")
            return False
    else:
        print(f"[AVISO] Nao encontrado: {source}")
        return False

def delete_item(path):
    """Deletar arquivo ou pasta"""
    if os.path.exists(path):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            print(f"[OK] Deletado: {path}")
            return True
        except Exception as e:
            print(f"[ERRO] Ao deletar {path}: {e}")
            return False
    return False

def main():
    print("=" * 60)
    print("REORGANIZAÇÃO DO PROJETO FACILIAUTO")
    print("=" * 60)
    print()
    
    # 1. CRIAR NOVAS PASTAS
    print("\n[1/9] Criando nova estrutura de pastas...")
    create_directory("agents")
    create_directory("docs/business")
    create_directory("docs/technical")
    create_directory("docs/implementation")
    create_directory("docs/guides")
    create_directory("examples")
    create_directory(".archive/scripts-temporarios")
    create_directory(".archive/docs-processo")
    
    # 2. MOVER AGENTES
    print("\n[2/9] Movendo agentes...")
    agents = [
        ("Agent Orchestrator", "agents/agent-orchestrator"),
        ("AI Engineer", "agents/ai-engineer"),
        ("Business Analyst", "agents/business-analyst"),
        ("Content Creator", "agents/content-creator"),
        ("Data Analyst", "agents/data-analyst"),
        ("Financial Advisor", "agents/financial-advisor"),
        ("Marketing Strategist", "agents/marketing-strategist"),
        ("Operations Manager", "agents/operations-manager"),
        ("Product Manager", "agents/product-manager"),
        ("Sales Coach", "agents/sales-coach"),
        ("System Archictecture", "agents/system-architecture"),
        ("Tech Lead", "agents/tech-lead"),
        ("UX Especialist", "agents/ux-especialist"),
    ]
    
    for source, dest in agents:
        move_item(source, dest)
    
    # Scripts de agentes
    move_item("agent-cli.py", "agents/agent-cli.py")
    move_item("orchestrator.py", "agents/orchestrator.py")
    move_item("orchestrated_cli.py", "agents/orchestrated_cli.py")
    move_item("run_orchestrator.py", "agents/run_orchestrator.py")
    
    # 3. MOVER DOCS BUSINESS
    print("\n[3/9] Movendo documentação de negócio...")
    business_docs = [
        "docs/VISAO-PRODUTO-SAAS.md",
        "docs/PLANO-VENDAS-ESTRATEGICO.md",
        "docs/PLANO-IMPLEMENTACAO-COMERCIAL.md",
        "docs/PLANO-BOOTSTRAP-ZERO-INVESTIMENTO.md",
        "docs/METRICAS-ROI-VENDAS.md",
        "docs/ROADMAP-AQUISICAO-CLIENTES.md",
        "docs/ESTRATEGIA-TARGETING-AVANCADO.md",
        "docs/GUIA-CONCESSIONARIAS.md",
        "docs/CHECKLIST-REGISTRO-EMPRESA.md",
        "docs/EXECUCAO-IMEDIATA.md",
    ]
    
    for doc in business_docs:
        filename = os.path.basename(doc)
        move_item(doc, f"docs/business/{filename}")
    
    # 4. MOVER DOCS TÉCNICOS
    print("\n[4/9] Movendo documentação técnica...")
    technical_docs = [
        "docs/ARQUITETURA-SAAS.md",
        "docs/ORCHESTRATOR-SYSTEM.md",
        "docs/REESTRUTURACAO-PLATAFORMA-UNICA.md",
    ]
    
    for doc in technical_docs:
        filename = os.path.basename(doc)
        move_item(doc, f"docs/technical/{filename}")
    
    # Manter alguns docs na raiz de docs
    # (Competitive Analysis, Design System, UX Research, etc.)
    
    # 5. MOVER DOCS DE IMPLEMENTAÇÃO
    print("\n[5/9] Movendo documentação de implementação...")
    impl_docs = [
        "IMPLEMENTACAO-XP-TDD-COMPLETA.md",
        "CONCLUSAO-FINAL.md",
        "MISSAO-CUMPRIDA-XP-TDD.md",
        "README-IMPLEMENTACAO-XP.md",
        "REESTRUTURACAO-COMPLETA.md",
    ]
    
    for doc in impl_docs:
        move_item(doc, f"docs/implementation/{doc}")
    
    # 6. MOVER GUIAS
    print("\n[6/9] Movendo guias práticos...")
    guides = [
        "COMO-RODAR-FACILIAUTO.md",
        "GIT-GUIDE.md",
        "GIT-SETUP.md",
    ]
    
    for guide in guides:
        move_item(guide, f"docs/guides/{guide}")
    
    # 7. MOVER EXEMPLOS
    print("\n[7/9] Movendo exemplos/protótipos...")
    move_item("CarRecommendationSite", "examples/CarRecommendationSite")
    move_item("RobustCar", "examples/RobustCar")
    
    # 8. ARQUIVAR TEMPORÁRIOS
    print("\n[8/9] Arquivando arquivos temporários...")
    temp_scripts = [
        "commit-limpo.bat",
        "commit-limpo.sh",
        "rodar-faciliauto.bat",
        "run-faciliauto.bat",
        "start-faciliauto-simple.bat",
        "start-faciliauto.bat",
        "start-faciliauto.sh",
        "test-api-fix.bat",
        "prepare-git-commits.bat",
        "prepare-git-commits.sh",
    ]
    
    for script in temp_scripts:
        move_item(script, f".archive/scripts-temporarios/{script}")
    
    temp_docs = [
        "ATUALIZAR-REPOSITORIO-GITHUB.md",
        "EXECUTAR-AGORA-LIMPO.md",
        "EXECUTAR-PUSH-AGORA.md",
        "LIMPEZA-REPOSITORIO-FINAL.md",
        "PREPARACAO-GIT-COMPLETA.md",
        "REORGANIZACAO-ESTRUTURA-FINAL.md",
    ]
    
    for doc in temp_docs:
        move_item(doc, f".archive/docs-processo/{doc}")
    
    # 9. DELETAR OBSOLETOS
    print("\n[9/9] Deletando arquivos obsoletos...")
    delete_item("__pycache__")
    delete_item("tatus")
    
    print("\n" + "=" * 60)
    print("[SUCESSO] REORGANIZACAO CONCLUIDA!")
    print("=" * 60)
    print("\nNova estrutura:")
    print("  - platform/         (Projeto principal)")
    print("  - agents/           (Framework de agentes)")
    print("  - docs/             (Documentacao organizada)")
    print("  - examples/         (Prototipos)")
    print("  - .archive/         (Arquivos historicos)")
    print("\nProximo passo: git add . && git commit")

if __name__ == "__main__":
    main()

