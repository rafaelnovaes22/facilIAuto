@echo off
REM Script para preparar commits estruturados do FacilIAuto
REM Execute este script para fazer commits organizados e profissionais

echo ========================================
echo PREPARANDO COMMITS ESTRUTURADOS
echo ========================================

cd /d "%~dp0"

echo.
echo Este script vai criar 6 commits estruturados:
echo 1. Documentacao completa
echo 2. Framework de agentes
echo 3. Plataforma unificada
echo 4. Sistema RobustCar
echo 5. Metodologia XP e testes
echo 6. Documentacao adicional
echo.

set /p CONFIRM="Continuar? [y/N]: "
if /i not "%CONFIRM%"=="y" (
    echo Cancelado.
    exit /b 1
)

REM Remover arquivos temporários
echo.
echo [1/7] Removendo arquivos temporarios...
git rm -f tatus 2>nul
git rm -f test-api-fix.bat 2>nul

REM Commit 1: Documentação Base
echo.
echo [2/7] Commit 1: Documentacao completa...
git add README.md
git add CONTRIBUTING.md
git add FOR-RECRUITERS.md
git add GIT-GUIDE.md
git add GIT-SETUP.md
git add LICENSE
git add .gitignore
git add PROJECT-SUMMARY.md
git add REESTRUTURACAO-COMPLETA.md
git add COMO-RODAR-FACILIAUTO.md

git commit -m "docs: adiciona documentacao completa e profissional"

REM Commit 2: Framework
echo.
echo [3/7] Commit 2: Framework de agentes...
git add "Agent Orchestrator/" 2>nul
git add "AI Engineer/" 2>nul
git add "Business Analyst/" 2>nul
git add "Content Creator/" 2>nul
git add "Data Analyst/" 2>nul
git add "Financial Advisor/" 2>nul
git add "Marketing Strategist/" 2>nul
git add "Operations Manager/" 2>nul
git add "Product Manager/" 2>nul
git add "Sales Coach/" 2>nul
git add "System Archictecture/" 2>nul
git add "Tech Lead/" 2>nul
git add "UX Especialist/" 2>nul
git add agent-cli.py 2>nul
git add orchestrator.py 2>nul
git add orchestrated_cli.py 2>nul
git add run_orchestrator.py 2>nul

git commit -m "feat: implementa framework de 12 agentes especializados"

REM Commit 3: Plataforma
echo.
echo [4/7] Commit 3: Plataforma unificada...
git add platform/
git add docs/REESTRUTURACAO-PLATAFORMA-UNICA.md
git add docs/ARQUITETURA-SAAS.md

git commit -m "feat: implementa plataforma unificada multi-concessionaria"

REM Commit 4: RobustCar
echo.
echo [5/7] Commit 4: Sistema RobustCar...
git add RobustCar/

git commit -m "feat: adiciona sistema RobustCar funcional completo"

REM Commit 5: XP
echo.
echo [6/7] Commit 5: Metodologia XP e testes...
git add CarRecommendationSite/

git commit -m "test: implementa metodologia XP 100%% com TDD e E2E"

REM Commit 6: Docs
echo.
echo [7/7] Commit 6: Documentacao adicional...
git add docs/
git add *.bat 2>nul
git add *.sh 2>nul

git commit -m "docs: adiciona documentacao completa e scripts de execucao"

echo.
echo ========================================
echo COMMITS CONCLUIDOS COM SUCESSO!
echo ========================================
echo.
echo Proximos passos:
echo 1. Verificar commits: git log --oneline
echo 2. Criar repositorio no GitHub/GitLab
echo 3. Adicionar remote: git remote add origin ^<URL^>
echo 4. Push: git push -u origin master
echo.
echo Ver guia completo em: GIT-GUIDE.md

pause

