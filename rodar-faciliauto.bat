@echo off
echo ====================================
echo    FACILIAUTO - SISTEMA FUNCIONANDO
echo ====================================
echo.

echo [STEP 1] Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo [STEP 2] Verificando Node.js...
node --version
if errorlevel 1 (
    echo ERRO: Node.js nao encontrado!
    pause
    exit /b 1
)

echo.
echo [STEP 3] Iniciando Backend Python...
echo.
cd RobustCar
start "FacilIAuto Backend" cmd /k "python api.py"

echo [STEP 4] Aguardando backend...
timeout /t 5 /nobreak >nul

echo [STEP 5] Iniciando Frontend React...
echo.
cd frontend
start "FacilIAuto Frontend" cmd /k "npm run dev"

cd ..\..

echo.
echo ====================================
echo       FACILIAUTO INICIADO!
echo ====================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173  
echo API Docs: http://localhost:8000/docs
echo.
echo Duas janelas foram abertas:
echo - FacilIAuto Backend (Python)
echo - FacilIAuto Frontend (React)
echo.
echo Para testar:
echo 1. Abra http://localhost:5173 no navegador
echo 2. Teste o questionario de carros
echo 3. Veja as recomendacoes
echo.
pause
