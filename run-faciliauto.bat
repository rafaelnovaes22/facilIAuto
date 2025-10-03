@echo off
echo Iniciando FacilIAuto - Backend e Frontend
echo ==========================================

cd CarRecommendationSite

echo.
echo [1/4] Instalando dependencias do Backend...
cd backend
npm install
if errorlevel 1 (
    echo ERRO ao instalar dependencias do backend
    pause
    exit /b 1
)

echo.
echo [2/4] Instalando dependencias do Frontend...
cd ..\frontend
npm install
if errorlevel 1 (
    echo ERRO ao instalar dependencias do frontend
    pause
    exit /b 1
)

echo.
echo [3/4] Iniciando Backend...
cd ..\backend
start "FacilIAuto Backend" cmd /k "npm run dev"

echo.
echo [4/4] Aguardando e iniciando Frontend...
timeout /t 5 /nobreak >nul
cd ..\frontend
start "FacilIAuto Frontend" cmd /k "npm run dev"

echo.
echo ==========================================
echo FacilIAuto rodando com sucesso!
echo ==========================================
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:5000/docs
echo ==========================================
echo.
echo Duas janelas foram abertas:
echo - FacilIAuto Backend (porta 5000)
echo - FacilIAuto Frontend (porta 3000)
echo.
echo Para parar: Feche as janelas do Backend e Frontend
echo.
pause
