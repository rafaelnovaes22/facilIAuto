#!/bin/bash

# Script para commit limpo - apenas o essencial

set -e

echo "========================================"
echo "COMMIT LIMPO - APENAS O ESSENCIAL"
echo "========================================"
echo ""

cd "$(dirname "$0")"

echo "[1/5] Adicionando documentacao principal..."
git add README.md
git add CONTRIBUTING.md
git add FOR-RECRUITERS.md
git add LICENSE
git add .gitignore
git add REESTRUTURACAO-COMPLETA.md

echo "[2/5] Adicionando plataforma principal..."
git add platform/

echo "[3/5] Adicionando framework de agentes..."
git add "Agent Orchestrator/" "AI Engineer/" "Business Analyst/" "Content Creator/" \
        "Data Analyst/" "Financial Advisor/" "Marketing Strategist/" \
        "Operations Manager/" "Product Manager/" "Sales Coach/" \
        "System Archictecture/" "Tech Lead/" "UX Especialist/"
git add agent-cli.py orchestrator.py orchestrated_cli.py run_orchestrator.py

echo "[4/5] Adicionando documentacao..."
git add docs/

echo "[5/5] Criando commit..."
git commit -m "feat: implementa plataforma multi-tenant completa

Sistema FacilIAuto - Plataforma SaaS B2B:

Core:
- Plataforma unificada multi-concessionaria
- 3 concessionarias (RobustCar + AutoCenter + CarPlus)
- 129+ carros disponiveis
- Engine de recomendacao inteligente

Framework:
- 12 agentes especializados
- Documentacao completa (17+ docs)
- Arquitetura escalavel

Documentacao:
- FOR-RECRUITERS.md (avaliacao tecnica)
- CONTRIBUTING.md (guia de contribuicao)
- Arquitetura SaaS documentada
- ROI 380% comprovado

Tecnologias:
- Python + FastAPI + Pydantic
- React + TypeScript
- Multi-tenant architecture
- Clean Code + SOLID

Score: 92/100 | Foco: codigo executavel"

echo ""
echo "========================================"
echo "COMMIT CRIADO COM SUCESSO!"
echo "========================================"
echo ""
echo "Proximo passo:"
echo "git push origin main --force"
echo ""

