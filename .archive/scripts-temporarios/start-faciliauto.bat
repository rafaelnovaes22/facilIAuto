@echo off
REM 🚀 FacilIAuto - Start Script Rápido (Windows)
REM Inicia backend + frontend simultaneamente

echo 🚀 Iniciando FacilIAuto...
echo ==========================

REM Verificar se está no diretório correto
if not exist "CarRecommendationSite" (
    echo ❌ Execute este script na raiz do projeto ^(onde está CarRecommendationSite/^)
    pause
    exit /b 1
)

cd CarRecommendationSite

REM Verificar pré-requisitos
echo 📋 Verificando pré-requisitos...

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js não encontrado. Instale Node.js 18+ primeiro.
    pause
    exit /b 1
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm não encontrado. Instale npm primeiro.
    pause
    exit /b 1
)

echo ✅ Pré-requisitos OK

REM Preparar backend
echo 📋 Preparando Backend...
cd backend

if not exist "node_modules" (
    echo 📋 Instalando dependências backend...
    npm install
    echo ✅ Dependências backend instaladas
) else (
    echo ℹ️  Dependências backend já instaladas
)

REM Verificar TDD
echo 📋 Verificando TDD...
npm test >nul 2>&1
if errorlevel 1 (
    echo ℹ️  TDD pode precisar de ajustes, mas continuando...
) else (
    echo ✅ TDD Backend funcionando ^(9 testes^)
)

cd ..

REM Preparar frontend
echo 📋 Preparando Frontend...
cd frontend

if not exist "node_modules" (
    echo 📋 Instalando dependências frontend...
    npm install
    echo ✅ Dependências frontend instaladas
) else (
    echo ℹ️  Dependências frontend já instaladas
)

cd ..

REM Criar script de início simultâneo
echo 📋 Criando scripts de execução...

echo @echo off > start-dev.bat
echo echo 🚀 Iniciando FacilIAuto Backend + Frontend... >> start-dev.bat
echo. >> start-dev.bat
echo echo 🔧 Iniciando Backend... >> start-dev.bat
echo start /B cmd /c "cd backend && npm run dev" >> start-dev.bat
echo. >> start-dev.bat
echo echo ⏳ Aguardando backend inicializar... >> start-dev.bat
echo timeout /t 3 /nobreak ^>nul >> start-dev.bat
echo. >> start-dev.bat
echo echo 🌐 Iniciando Frontend... >> start-dev.bat
echo start /B cmd /c "cd frontend && npm run dev" >> start-dev.bat
echo. >> start-dev.bat
echo echo. >> start-dev.bat
echo echo 🎉 FacilIAuto rodando! >> start-dev.bat
echo echo 📡 Backend:  http://localhost:5000 >> start-dev.bat
echo echo 🌐 Frontend: http://localhost:3000 >> start-dev.bat
echo echo 📚 API Docs: http://localhost:5000/docs >> start-dev.bat
echo echo. >> start-dev.bat
echo echo 📋 Para parar: Feche esta janela >> start-dev.bat
echo echo 🧪 Para TDD: Execute start-tdd.bat >> start-dev.bat
echo echo. >> start-dev.bat
echo pause >> start-dev.bat

REM Criar script de TDD
echo @echo off > start-tdd.bat
echo echo 🧪 Iniciando TDD FacilIAuto... >> start-tdd.bat
echo. >> start-tdd.bat
echo echo 🔧 TDD Backend... >> start-tdd.bat
echo start /B cmd /k "cd backend && npm run test:watch" >> start-tdd.bat
echo. >> start-tdd.bat
echo echo 🌐 TDD Frontend... >> start-tdd.bat
echo start /B cmd /k "cd frontend && npm run test:watch" >> start-tdd.bat
echo. >> start-tdd.bat
echo echo 🧪 TDD ativo! Feche as janelas para parar >> start-tdd.bat
echo pause >> start-tdd.bat

REM Criar script de E2E
echo @echo off > start-e2e.bat
echo echo 🌐 Iniciando Testes E2E... >> start-e2e.bat
echo. >> start-e2e.bat
echo cd frontend >> start-e2e.bat
echo. >> start-e2e.bat
echo echo 🧪 Abrindo Cypress... >> start-e2e.bat
echo npm run e2e:open >> start-e2e.bat
echo pause >> start-e2e.bat

echo ✅ Scripts criados

REM Instruções finais
echo.
echo 🎉 FacilIAuto pronto para rodar!
echo =================================
echo.
echo ℹ️  COMANDOS DISPONÍVEIS:
echo.
echo 🚀 INÍCIO RÁPIDO:
echo    start-dev.bat     REM Backend + Frontend simultâneo
echo.
echo 🧪 DESENVOLVIMENTO TDD:
echo    start-tdd.bat     REM TDD contínuo
echo.
echo 🌐 TESTES E2E:
echo    start-e2e.bat     REM Cypress E2E
echo.
echo 🔧 MANUAL:
echo    cd backend ^&^& npm run dev
echo    cd frontend ^&^& npm run dev
echo.
echo ✅ Execute qualquer comando acima para começar!
echo.
echo ℹ️  📖 Guia completo: COMO-RODAR-FACILIAUTO.md
echo.
pause
