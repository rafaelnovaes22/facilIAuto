cd proc@echo off
chcp 65001 >nul
echo ========================================
echo  REINICIANDO BACKEND - FacilIAuto
echo ========================================
echo.

echo [1/3] Parando processos Python...
taskkill /F /IM python.exe 2>nul
if %errorlevel% == 0 (
    echo ✓ Processos Python encerrados
) else (
    echo ℹ Nenhum processo Python em execução
)
timeout /t 2 /nobreak >nul

echo.
echo [2/3] Verificando estrutura...
if not exist "platform\backend" (
    echo ✗ ERRO: Pasta platform\backend não encontrada!
    echo Execute este script na raiz do projeto.
    pause
    exit /b 1
)
echo ✓ Estrutura verificada

echo.
echo [3/3] Iniciando backend...
cd platform\backend
echo ✓ Backend iniciando em http://localhost:8000
echo ℹ Uma nova janela será aberta com o servidor
echo.
start "FacilIAuto Backend" cmd /k "python api/main.py"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo  BACKEND REINICIADO COM SUCESSO!
echo ========================================
echo.
echo ✓ Backend: http://localhost:8000
echo ✓ Health Check: http://localhost:8000/health
echo ✓ Frontend: http://localhost:3000
echo.
echo ℹ Recarregue a página do frontend (F5)
echo   e refaça o questionário
echo.
echo ========================================
pause

