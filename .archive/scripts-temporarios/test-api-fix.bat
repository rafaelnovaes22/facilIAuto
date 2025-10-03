@echo off
echo ===========================
echo  TESTANDO CORRECOES DA API
echo ===========================
echo.

echo [1] Parando processos anteriores...
taskkill /f /im python.exe >nul 2>&1

echo [2] Entrando no diretorio RobustCar...
cd RobustCar

echo [3] Testando sintaxe do arquivo API...
python -m py_compile api.py
if errorlevel 1 (
    echo ERRO: Problemas de sintaxe no api.py
    pause
    exit /b 1
)
echo Sintaxe OK!

echo.
echo [4] Iniciando API corrigida...
echo.
echo Backend iniciando em http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Pressione Ctrl+C para parar
echo.
python api.py
