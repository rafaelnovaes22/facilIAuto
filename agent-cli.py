#!/usr/bin/env python3
"""
🤖 Agent Framework CLI Tool
Ferramenta para criar e gerenciar agentes especializados

Uso:
    python agent-cli.py create [nome-do-agente] [emoji]
    python agent-cli.py list
    python agent-cli.py validate [nome-do-agente]
    python agent-cli.py help
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

class AgentCLI:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.template_path = self.project_root / "TEMPLATE-AGENT-CONTEXT.md"
        
    def create_agent(self, agent_name: str, emoji: str = "🤖"):
        """Cria um novo agente baseado no template"""
        
        # Validar inputs
        if not agent_name:
            print("❌ Nome do agente é obrigatório")
            return False
            
        # Normalizar nome
        agent_folder = agent_name.replace(" ", " ").title()
        agent_dir = self.project_root / agent_folder
        
        # Verificar se já existe
        if agent_dir.exists():
            print(f"❌ Agente '{agent_folder}' já existe!")
            return False
            
        # Verificar se template existe
        if not self.template_path.exists():
            print("❌ Template não encontrado! Execute este script da raiz do projeto.")
            return False
            
        try:
            # Criar diretório
            agent_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Criando diretório: {agent_folder}")
            
            # Ler template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Fazer substituições
            context_content = template_content.replace(
                "[NOME DO AGENTE]", agent_name
            ).replace(
                "[EMOJI]", emoji
            )
            
            # Escrever arquivo context.md
            context_path = agent_dir / "context.md"
            with open(context_path, 'w', encoding='utf-8') as f:
                f.write(context_content)
            
            print(f"✅ Agente '{agent_name}' {emoji} criado com sucesso!")
            print(f"📝 Edite o arquivo: {context_path}")
            print(f"🔧 Não esqueça de personalizar o contexto antes de usar")
            
            # Atualizar README principal
            self._update_main_readme(agent_name, emoji, agent_folder)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar agente: {e}")
            return False
    
    def _update_main_readme(self, agent_name: str, emoji: str, agent_folder: str):
        """Atualiza o README principal com o novo agente"""
        readme_path = self.project_root / "README.md"
        
        if not readme_path.exists():
            print("⚠️  README.md não encontrado - pule a atualização manual")
            return
            
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Adicionar na estrutura do projeto
            project_structure_line = f"├── {agent_folder}/           # [Adicione descrição aqui]"
            
            # Encontrar onde inserir na estrutura
            if "└── README.md" in content:
                content = content.replace(
                    "└── README.md             # Este arquivo",
                    f"{project_structure_line}\n└── README.md             # Este arquivo"
                )
            
            # Adicionar na visão geral (encontrar o último agente)
            agent_count = content.count("### ") - 3  # Subtrair seções que não são agentes
            new_agent_section = f"""
### {agent_count + 1}. **{agent_name}** {emoji}
- **Foco**: [Adicione foco principal aqui]
- **Especialidades**: [Adicione especialidades aqui]
- **Ideal para**: [Adicione casos de uso ideais aqui]
"""
            
            # Inserir antes de "## 🚀 Como Usar Este Framework"
            content = content.replace(
                "## 🚀 Como Usar Este Framework",
                f"{new_agent_section}\n## 🚀 Como Usar Este Framework"
            )
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"📝 README.md atualizado - revise e complete as descrições")
            
        except Exception as e:
            print(f"⚠️  Erro ao atualizar README: {e}")
    
    def list_agents(self):
        """Lista todos os agentes existentes"""
        print("📋 Agentes Existentes:")
        print("=" * 50)
        
        count = 0
        for item in self.project_root.iterdir():
            if item.is_dir() and (item / "context.md").exists():
                # Pular diretórios especiais
                if item.name in ["CarRecommendationSite", ".git", "__pycache__"]:
                    continue
                    
                count += 1
                context_path = item / "context.md"
                
                # Tentar extrair emoji do context.md
                emoji = "📄"
                try:
                    with open(context_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline()
                        if " - Contexto e Regras" in first_line:
                            # Extrair emoji se existir
                            title = first_line.split(" - Contexto e Regras")[0].strip("# ")
                            words = title.split()
                            if len(words) > 1 and any(ord(char) > 127 for char in words[-1]):
                                emoji = words[-1]
                except:
                    pass
                
                print(f"{count:2d}. {emoji} {item.name}")
                
        if count == 0:
            print("❌ Nenhum agente encontrado!")
        else:
            print(f"\n✅ Total: {count} agentes")
    
    def validate_agent(self, agent_name: str):
        """Valida se um agente está completo"""
        agent_folder = agent_name.replace(" ", " ").title()
        agent_dir = self.project_root / agent_folder
        context_path = agent_dir / "context.md"
        
        if not context_path.exists():
            print(f"❌ Agente '{agent_name}' não encontrado!")
            return False
        
        print(f"🔍 Validando agente: {agent_name}")
        print("=" * 50)
        
        try:
            with open(context_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Checklist de validação
            checks = [
                ("✅ Arquivo context.md existe", True),
                ("📝 Missão definida", "## 🎯 Missão" in content),
                ("👤 Perfil definido", "## 👤 Perfil do Agente" in content),
                ("📋 Responsabilidades definidas", "## 📋 Responsabilidades Principais" in content),
                ("🛠️ Stack tecnológico definido", "## 🛠️ Stack Tecnológico" in content),
                ("📐 Frameworks definidos", "## 📐 Frameworks e Metodologias" in content),
                ("📊 Métricas definidas", "## 📊 Métricas" in content),
                ("🎭 Soft skills definidas", "## 🎭 Soft Skills" in content),
                ("🚨 Princípios definidos", "## 🚨 Princípios" in content),
                ("🤝 Integração definida", "## 🤝 Integração" in content),
                ("❌ Template não removido", "[NOME DO AGENTE]" not in content),
                ("📏 Tamanho adequado", len(content.splitlines()) > 200),
                ("🔄 XP integrado", "XP" in content or "Extreme Programming" in content),
            ]
            
            passed = 0
            total = len(checks)
            
            for check_name, condition in checks:
                if condition:
                    print(f"✅ {check_name}")
                    passed += 1
                else:
                    print(f"❌ {check_name}")
            
            print(f"\n📊 Score: {passed}/{total} ({passed/total*100:.1f}%)")
            
            if passed == total:
                print("🎉 Agente está completo e pronto para uso!")
                return True
            elif passed >= total * 0.8:
                print("⚠️  Agente está quase pronto - alguns ajustes necessários")
                return False
            else:
                print("🚧 Agente precisa de mais trabalho")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao validar agente: {e}")
            return False
    
    def show_help(self):
        """Mostra help da ferramenta"""
        print("""
🤖 Agent Framework CLI Tool

COMANDOS DISPONÍVEIS:

  create [nome] [emoji]     Cria novo agente
    Exemplo: python agent-cli.py create "UX Designer" 🎨
    
  list                      Lista todos os agentes
    Exemplo: python agent-cli.py list
    
  validate [nome]           Valida agente existente
    Exemplo: python agent-cli.py validate "UX Designer"
    
  help                      Mostra esta ajuda
    Exemplo: python agent-cli.py help

WORKFLOW RECOMENDADO:

  1. 📋 Liste agentes existentes:
     python agent-cli.py list
     
  2. 🆕 Crie novo agente:
     python agent-cli.py create "Seu Agente" 🚀
     
  3. ✏️ Edite o arquivo context.md gerado
  
  4. ✅ Valide quando terminar:
     python agent-cli.py validate "Seu Agente"

DICAS:

  • Use nomes descritivos (ex: "UX Designer", "DevOps Engineer")
  • Escolha emojis representativos
  • Personalize TODAS as seções do template
  • Mantenha alinhamento com metodologia XP
  • Valide sempre antes de usar

📖 Documentação completa: README.md
        """)

def main():
    cli = AgentCLI()
    
    if len(sys.argv) < 2:
        cli.show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        if len(sys.argv) < 3:
            print("❌ Nome do agente é obrigatório!")
            print("Uso: python agent-cli.py create 'Nome do Agente' 🚀")
            return
            
        agent_name = sys.argv[2]
        emoji = sys.argv[3] if len(sys.argv) > 3 else "🤖"
        cli.create_agent(agent_name, emoji)
        
    elif command == "list":
        cli.list_agents()
        
    elif command == "validate":
        if len(sys.argv) < 3:
            print("❌ Nome do agente é obrigatório!")
            print("Uso: python agent-cli.py validate 'Nome do Agente'")
            return
            
        agent_name = sys.argv[2]
        cli.validate_agent(agent_name)
        
    elif command == "help":
        cli.show_help()
        
    else:
        print(f"❌ Comando '{command}' não reconhecido!")
        cli.show_help()

if __name__ == "__main__":
    main()
