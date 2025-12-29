@echo off
REM ========================================
REM FacilIAuto - Startup Simples (Windows)
REM Sem instalar dependencias, so inicia
REM ========================================

echo.
echo ========================================
echo   FACILIAUTO - Iniciando (Simples)
echo ========================================
echo.

REM Voltar para raiz
cd ..

REM Iniciar Backend
echo [1/2] Iniciando Backend...
start "FacilIAuto Backend" cmd /k "cd platform\backend && python api/main.py"
timeout /t 3 /nobreak >nul

REM Iniciar Frontend
echo [2/2] Iniciando Frontend...
start "FacilIAuto Frontend" cmd /k "cd platform\frontend && npm run dev"
timeout /t 5 /nobreak >nul

REM Abrir navegador
start http://localhost:3000

echo.
echo ========================================
echo   FACILIAUTO INICIADO!
echo ========================================
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo ========================================

