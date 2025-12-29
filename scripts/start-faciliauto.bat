@echo off
REM ========================================
REM FacilIAuto - Startup Script (Windows)
REM ========================================

echo.
echo ========================================
echo   FACILIAUTO - Iniciando Projeto
echo ========================================
echo.

REM Ir para a raiz do projeto (assumindo que script esta em /scripts)
cd ..

REM Verificar se estamos na raiz do projeto
if not exist "platform" (
    echo [ERRO] Estrutura de projeto invalida.
    echo Certifique-se de executar este script da pasta 'scripts' e que a pasta 'platform' existe na raiz.
    pause
    exit /b 1
)

echo [1/5] Configurando Backend...
echo.

REM Ir para o backend
cd platform\backend

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

REM Instalar dependências do backend (se necessário)
if not exist "venv" (
    echo [INFO] Criando ambiente virtual Python...
    python -m venv venv
)

echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [INFO] Instalando dependencias do backend...
pip install -r requirements.txt --quiet

echo.
echo [2/5] Configurando Frontend...
echo.

REM Voltar para a raiz e ir para frontend
cd ..\..
cd platform\frontend

REM Verificar se Node.js está instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Node.js nao encontrado. Instale Node.js 18+ primeiro.
    pause
    exit /b 1
)

REM Instalar dependências do frontend (se necessário)
if not exist "node_modules" (
    echo [INFO] Instalando dependencias do frontend...
    call npm install --quiet
) else (
    echo [INFO] Dependencias do frontend ja instaladas.
)

echo.
echo [3/5] Iniciando Backend API...
echo.

REM Voltar para backend e iniciar API em background
cd ..\backend

REM Iniciar backend em nova janela
start "FacilIAuto Backend" cmd /k "call venv\Scripts\activate.bat && python api/main.py"

echo [OK] Backend iniciado em http://localhost:8000
timeout /t 3 /nobreak >nul

echo.
echo [4/5] Iniciando Frontend...
echo.

REM Ir para frontend
cd ..\frontend

REM Iniciar frontend em nova janela
start "FacilIAuto Frontend" cmd /k "npm run dev"

echo [OK] Frontend iniciado em http://localhost:3000
timeout /t 3 /nobreak >nul

echo.
echo [5/5] Abrindo navegador...
echo.

REM Aguardar um pouco para os serviços iniciarem
timeout /t 5 /nobreak >nul

REM Abrir navegador
start http://localhost:3000

REM Voltar para raiz
cd ..\..

echo.
echo ========================================
echo   FACILIAUTO INICIADO COM SUCESSO!
echo ========================================
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo   Para parar os servicos, feche as janelas do terminal.
echo.
echo ========================================
echo.

pause
