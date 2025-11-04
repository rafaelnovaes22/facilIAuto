@echo off
REM Setup script for RobustCar Scraper (Windows)

echo ========================================
echo RobustCar Scraper - Setup
echo ========================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Setup completed successfully!
    echo ========================================
    echo.
    echo You can now run the scraper:
    echo   python -m scraper.orchestrator --mode full
    echo.
) else (
    echo.
    echo ========================================
    echo Setup failed! Please check the errors above.
    echo ========================================
    echo.
)

pause
