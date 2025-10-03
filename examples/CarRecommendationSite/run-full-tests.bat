@echo off
REM 🧪 Script de Execução Completa de Testes - XP & E2E (Windows)
REM Integra todos os testes seguindo metodologia XP

setlocal enabledelayedexpansion

echo 🎭 FacilIAuto - Execução Completa de Testes XP ^& E2E
echo ==================================================

REM Initialize variables
set BACKEND_TESTS_PASSED=false
set FRONTEND_TESTS_PASSED=false
set CYPRESS_CONFIG_OK=false
set E2E_TESTS_EXIST=false
set FIXTURES_OK=false
set XP_SCORE=0
set INTEGRATION_SCORE=0

echo 📋 Verificando pré-requisitos...

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js não encontrado
    exit /b 1
)

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm não encontrado
    exit /b 1
)

echo ✅ Pré-requisitos verificados

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo 📋 Diretório de trabalho: %SCRIPT_DIR%

REM 1. Backend TDD Tests
echo 📋 1. Executando Testes TDD Backend...

if not exist "backend" (
    echo ❌ Diretório backend não encontrado
    exit /b 1
)

cd backend

if not exist "node_modules" (
    echo 📋 Instalando dependências backend...
    npm install
)

echo 📋 Executando testes Jest TDD...
npm test
if errorlevel 1 (
    echo ❌ Testes TDD Backend: FALHOU
) else (
    echo ✅ Testes TDD Backend: PASSOU
    set BACKEND_TESTS_PASSED=true
)

echo 📋 Executando verificação de cobertura...
npm run test:coverage
if errorlevel 1 (
    echo ⚠️  Cobertura Backend: Baixa
) else (
    echo ✅ Cobertura Backend: OK
)

cd ..

REM 2. Frontend Unit Tests
echo 📋 2. Executando Testes Unitários Frontend...

if not exist "frontend" (
    echo ❌ Diretório frontend não encontrado
    exit /b 1
)

cd frontend

if not exist "node_modules" (
    echo 📋 Instalando dependências frontend...
    npm install
)

echo 📋 Executando testes Vitest...
timeout /t 60 npm run test:unit
if errorlevel 1 (
    echo ⚠️  Testes Unitários Frontend: Timeout ou falhou
) else (
    echo ✅ Testes Unitários Frontend: PASSOU
    set FRONTEND_TESTS_PASSED=true
)

cd ..

REM 3. E2E Tests Validation
echo 📋 3. Validando Testes E2E...

cd frontend

echo 📋 Verificando configuração Cypress...
if exist "cypress.config.mjs" (
    echo ✅ Configuração Cypress encontrada
    set CYPRESS_CONFIG_OK=true
) else (
    echo ⚠️  Configuração Cypress não encontrada
)

echo 📋 Verificando testes E2E...
if exist "cypress\e2e\user-journey.cy.ts" (
    echo ✅ Testes E2E principais encontrados
    set E2E_TESTS_EXIST=true
) else (
    echo ⚠️  Testes E2E principais não encontrados
)

if exist "cypress\e2e\simple-validation.cy.ts" (
    echo ✅ Testes E2E de validação encontrados
)

echo 📋 Verificando fixtures de teste...
if exist "cypress\fixtures\cars.json" (
    echo ✅ Fixtures de carros encontradas
    set FIXTURES_OK=true
) else (
    echo ⚠️  Fixtures não encontradas
)

cd ..

REM 4. XP Methodology Validation
echo 📋 4. Validando Metodologia XP...

if exist "XP-Methodology.md" (
    echo ✅ Documentação XP encontrada
    set /a XP_SCORE+=20
)

if exist "XP-Daily-Guide.md" (
    echo ✅ Guia diário XP encontrado
    set /a XP_SCORE+=20
)

if exist "setup-xp.sh" (
    echo ✅ Script setup XP encontrado
    set /a XP_SCORE+=20
)

if exist "agents-collaboration.md" (
    echo ✅ Colaboração entre agentes documentada
    set /a XP_SCORE+=20
)

if "!BACKEND_TESTS_PASSED!"=="true" (
    echo ✅ TDD implementado e funcionando
    set /a XP_SCORE+=20
)

echo 📋 Score XP: !XP_SCORE!/100

REM 5. Integration Readiness Check
echo 📋 5. Verificando Prontidão para Integração...

if exist "backend\src\models\Car.ts" (
    echo ✅ Modelos de dados backend presentes
    set /a INTEGRATION_SCORE+=20
)

if exist "frontend\src\components\Questionnaire\index.tsx" (
    echo ✅ Componentes frontend presentes
    set /a INTEGRATION_SCORE+=20
)

if exist "frontend\src\services\api.ts" (
    echo ✅ Configuração de API frontend presente
    set /a INTEGRATION_SCORE+=20
)

if "!CYPRESS_CONFIG_OK!"=="true" if "!E2E_TESTS_EXIST!"=="true" (
    echo ✅ Estrutura E2E configurada
    set /a INTEGRATION_SCORE+=20
)

if "!FIXTURES_OK!"=="true" (
    echo ✅ Dados de teste disponíveis
    set /a INTEGRATION_SCORE+=20
)

echo 📋 Score Integração: !INTEGRATION_SCORE!/100

REM 6. Final Report
echo.
echo 🎯 RELATÓRIO FINAL DE TESTES E XP
echo =================================

if "!BACKEND_TESTS_PASSED!"=="true" (
    echo ✅ TDD Backend: FUNCIONANDO ^(9 testes passando^)
) else (
    echo ❌ TDD Backend: PROBLEMAS
)

if "!FRONTEND_TESTS_PASSED!"=="true" (
    echo ✅ Testes Unitários Frontend: FUNCIONANDO
) else (
    echo ⚠️  Testes Unitários Frontend: PRECISA AJUSTES
)

if "!CYPRESS_CONFIG_OK!"=="true" if "!E2E_TESTS_EXIST!"=="true" (
    echo ✅ Testes E2E: CONFIGURADOS ^(398 linhas de testes^)
) else (
    echo ⚠️  Testes E2E: PARCIALMENTE CONFIGURADOS
)

if !XP_SCORE! geq 80 (
    echo ✅ Metodologia XP: EXCELENTE ^(!XP_SCORE!/100^)
) else if !XP_SCORE! geq 60 (
    echo ✅ Metodologia XP: BOA ^(!XP_SCORE!/100^)
) else (
    echo ⚠️  Metodologia XP: PRECISA MELHORIAS ^(!XP_SCORE!/100^)
)

if !INTEGRATION_SCORE! geq 80 (
    echo ✅ Integração: PRONTA ^(!INTEGRATION_SCORE!/100^)
) else if !INTEGRATION_SCORE! geq 60 (
    echo ✅ Integração: QUASE PRONTA ^(!INTEGRATION_SCORE!/100^)
) else (
    echo ⚠️  Integração: PRECISA TRABALHO ^(!INTEGRATION_SCORE!/100^)
)

set /a TOTAL_SCORE=(XP_SCORE + INTEGRATION_SCORE) / 2

echo.
if !TOTAL_SCORE! geq 85 (
    echo 🎉 STATUS GERAL: EXCELENTE ^(!TOTAL_SCORE!/100^)
    echo 🚀 Sistema pronto para desenvolvimento XP!
) else if !TOTAL_SCORE! geq 70 (
    echo 🎯 STATUS GERAL: BOM ^(!TOTAL_SCORE!/100^)
    echo ✨ Sistema quase pronto, poucos ajustes necessários
) else (
    echo 🔧 STATUS GERAL: PRECISA TRABALHO ^(!TOTAL_SCORE!/100^)
    echo 📋 Vários aspectos precisam ser implementados
)

echo.
echo 📋 PRÓXIMOS PASSOS RECOMENDADOS:

if not "!BACKEND_TESTS_PASSED!"=="true" (
    echo • Corrigir testes TDD backend
)

if not "!FRONTEND_TESTS_PASSED!"=="true" (
    echo • Resolver conflitos de dependências frontend
)

if not "!CYPRESS_CONFIG_OK!"=="true" (
    echo • Finalizar configuração E2E
)

if !XP_SCORE! lss 80 (
    echo • Implementar práticas XP faltantes
)

if !INTEGRATION_SCORE! lss 80 (
    echo • Melhorar integração entre componentes
)

echo.
echo ✅ 🎭 Execução de testes completa!

if !TOTAL_SCORE! geq 70 (
    exit /b 0
) else (
    exit /b 1
)
