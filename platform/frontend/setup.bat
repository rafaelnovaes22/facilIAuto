@echo off
echo ========================================
echo 🎨 Setup Frontend FacilIAuto
echo ========================================
echo.

echo [1/2] Instalando dependencias...
call npm install

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERRO: Falha ao instalar dependencias
    exit /b 1
)

echo.
echo ========================================
echo ✅ Setup Completo!
echo ========================================
echo.
echo Proximo passo:
echo   npm run dev
echo.
echo Abrir: http://localhost:3000
echo ========================================

