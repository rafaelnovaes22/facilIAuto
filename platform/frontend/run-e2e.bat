@echo off
echo ========================================
echo 🌲 Testes E2E FacilIAuto
echo ========================================
echo.

echo IMPORTANTE: Certifique-se de que:
echo 1. Backend esta rodando (http://localhost:8000)
echo 2. Frontend esta rodando (http://localhost:3000)
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

echo.
echo Abrindo Cypress...
call npm run e2e:open

echo.
echo ========================================
echo ✅ E2E tests finalizados!
echo ========================================

