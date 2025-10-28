@echo off
REM Setup script for FacilIAuto Chatbot development environment (Windows)

echo ==========================================
echo FacilIAuto Chatbot - Setup Script
echo ==========================================
echo.

REM Check if Poetry is installed
where poetry >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Poetry is not installed.
    echo Please install Poetry: https://python-poetry.org/docs/#installation
    exit /b 1
)
echo + Poetry is installed

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Docker is not installed.
    echo Please install Docker: https://docs.docker.com/get-docker/
    exit /b 1
)
echo + Docker is installed

echo.
echo Installing Python dependencies...
poetry install

echo.
echo Installing pre-commit hooks...
poetry run pre-commit install

echo.
echo Downloading spaCy Portuguese model...
poetry run python -m spacy download pt_core_news_lg

echo.
echo Creating .env file from template...
if not exist .env (
    copy .env.example .env
    echo + Created .env file. Please edit it with your configuration.
) else (
    echo ! .env file already exists. Skipping.
)

echo.
echo Starting Docker services...
docker-compose up -d

echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo + Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your WhatsApp API credentials
echo 2. Run 'make dev' to start the development server
echo 3. Run 'make test' to run tests
echo 4. Visit http://localhost:8000/docs for API documentation
echo.
echo Useful commands:
echo   make help       - Show all available commands
echo   make docker-up  - Start Docker services
echo   make dev        - Run development server
echo   make test       - Run tests
echo.

pause
