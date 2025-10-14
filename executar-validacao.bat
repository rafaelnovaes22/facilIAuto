@echo off
echo ========================================
echo   VALIDACAO BACKEND - FacilIAuto
echo ========================================
echo.

python validar-backend.py > relatorio-validacao.txt 2>&1

echo Validacao concluida!
echo.
echo Relatorio salvo em: relatorio-validacao.txt
echo.
type relatorio-validacao.txt
echo.
pause
