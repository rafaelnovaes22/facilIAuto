@echo off
chcp 65001 >nul
cls
echo ============================================================
echo   REINICIALIZACAO COMPLETA - FacilIAuto Backend
echo ============================================================
echo.

echo [1/3] Encerrando processos Python...
taskkill /F /IM python.exe 2>nul
if %errorlevel% == 0 (
    echo OK - Processos encerrados
) else (
    echo INFO - Nenhum processo em execucao
)

echo.
echo [2/3] Aguardando 2 segundos...
timeout /t 2 /nobreak >nul
echo OK - Aguardado

echo.
echo [3/3] Iniciando backend corrigido...
cd platform\backend
echo.
echo ============================================================
echo   BACKEND INICIANDO EM: http://localhost:8000
echo ============================================================
echo.
python api/main.py

