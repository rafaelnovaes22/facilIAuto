@echo off
REM FacilIAuto - Start Script Simples (Windows)
REM Inicia backend + frontend simultaneamente

echo Iniciando FacilIAuto...
echo ==========================

REM Verificar se esta no diretorio correto
if not exist "CarRecommendationSite" (
    echo ERRO: Execute este script na raiz do projeto onde esta CarRecommendationSite/
    pause
    exit /b 1
)

cd CarRecommendationSite

REM Verificar pre-requisitos
echo Verificando pre-requisitos...

node --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Node.js nao encontrado. Instale Node.js 18+ primeiro.
    pause
    exit /b 1
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: npm nao encontrado. Instale npm primeiro.
    pause
    exit /b 1
)

echo Pre-requisitos OK

REM Preparar backend
echo Preparando Backend...
cd backend

if not exist "node_modules" (
    echo Instalando dependencias backend...
    npm install
    echo Dependencias backend instaladas
) else (
    echo Dependencias backend ja instaladas
)

cd ..

REM Preparar frontend
echo Preparando Frontend...
cd frontend

if not exist "node_modules" (
    echo Instalando dependencias frontend...
    npm install
    echo Dependencias frontend instaladas
) else (
    echo Dependencias frontend ja instaladas
)

cd ..

REM Criar scripts de execucao
echo Criando scripts de execucao...

echo @echo off > start-dev-simple.bat
echo echo Iniciando FacilIAuto Backend + Frontend... >> start-dev-simple.bat
echo. >> start-dev-simple.bat
echo echo Iniciando Backend... >> start-dev-simple.bat
echo start /B cmd /c "cd backend && npm run dev" >> start-dev-simple.bat
echo. >> start-dev-simple.bat
echo echo Aguardando backend inicializar... >> start-dev-simple.bat
echo timeout /t 3 /nobreak ^>nul >> start-dev-simple.bat
echo. >> start-dev-simple.bat
echo echo Iniciando Frontend... >> start-dev-simple.bat
echo start /B cmd /c "cd frontend && npm run dev" >> start-dev-simple.bat
echo. >> start-dev-simple.bat
echo echo. >> start-dev-simple.bat
echo echo FacilIAuto rodando! >> start-dev-simple.bat
echo echo Backend:  http://localhost:5000 >> start-dev-simple.bat
echo echo Frontend: http://localhost:3000 >> start-dev-simple.bat
echo echo API Docs: http://localhost:5000/docs >> start-dev-simple.bat
echo echo. >> start-dev-simple.bat
echo echo Para parar: Feche esta janela >> start-dev-simple.bat
echo pause >> start-dev-simple.bat

echo Scripts criados com sucesso!

echo.
echo FacilIAuto pronto para rodar!
echo =================================
echo.
echo COMANDOS DISPONIVEIS:
echo.
echo INICIO RAPIDO:
echo    start-dev-simple.bat     REM Backend + Frontend simultaneo
echo.
echo MANUAL:
echo    cd backend ^&^& npm run dev
echo    cd frontend ^&^& npm run dev
echo.
echo Execute start-dev-simple.bat para comecar!
echo.
pause
