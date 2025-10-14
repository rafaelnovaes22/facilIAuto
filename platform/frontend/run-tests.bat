@echo off
echo ========================================
echo 🧪 Testes Frontend FacilIAuto
echo ========================================
echo.

echo [1/3] Rodando testes unitarios...
call npm test -- --run

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERRO: Testes unitarios falharam
    exit /b 1
)

echo.
echo [2/3] Gerando coverage report...
call npm run test:coverage -- --run

echo.
echo [3/3] Testes completos!
echo.
echo ========================================
echo ✅ Todos os testes passaram!
echo ========================================
echo.
echo Para ver coverage: open coverage/index.html
echo Para rodar E2E: npm run e2e:open
echo ========================================

