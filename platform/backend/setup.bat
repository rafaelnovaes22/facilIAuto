@echo off
REM Setup do backend - Instalar dependencias
REM FacilIAuto Platform - Windows

echo ========================================
echo FacilIAuto - Backend Setup
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Instalando dependencias...
pip install -r requirements.txt

echo.
echo [2/2] Verificando instalacao...
python -c "import fastapi, pytest, pydantic; print('[OK] Todas as dependencias instaladas!')"

echo.
echo ========================================
echo Setup Concluido!
echo ========================================
echo.
echo Proximos passos:
echo 1. Rodar testes: run-tests.bat
echo 2. Iniciar API: python api/main.py
echo.
pause

