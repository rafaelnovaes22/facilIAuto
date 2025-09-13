@echo off
REM CarMatch XP Setup Script for Windows
REM Configura o ambiente completo para desenvolvimento com XP e testes E2E

echo 🚀 Setting up CarMatch with XP methodology...
echo ==============================================

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 18+ first.
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm not found. Please install npm first.
    exit /b 1
)

echo ✅ Prerequisites check passed

echo ℹ️ Setting up backend with TDD structure...
cd backend
if not exist "tests" mkdir tests
if not exist "tests\unit" mkdir tests\unit
if not exist "tests\integration" mkdir tests\integration
if not exist "tests\e2e" mkdir tests\e2e
if not exist "tests\fixtures" mkdir tests\fixtures

echo Installing backend dependencies...
call npm install
if errorlevel 1 (
    echo ❌ Backend npm install failed
    exit /b 1
)

echo ✅ Backend setup completed

cd ..\frontend
echo ℹ️ Setting up frontend with E2E tests...

if not exist "cypress" mkdir cypress
if not exist "cypress\e2e" mkdir cypress\e2e
if not exist "cypress\support" mkdir cypress\support
if not exist "cypress\fixtures" mkdir cypress\fixtures

echo Installing frontend dependencies...
call npm install
if errorlevel 1 (
    echo ❌ Frontend npm install failed
    exit /b 1
)

echo Setting up Cypress...
call npx cypress install

echo ✅ Frontend setup completed

cd ..

echo ℹ️ Setting up development environment...

REM Create .env files if they don't exist
if not exist "backend\.env" (
    echo NODE_ENV=development > backend\.env
    echo PORT=5000 >> backend\.env
    echo MONGODB_URI=mongodb://localhost:27017/carmatch_dev >> backend\.env
    echo REDIS_URL=redis://localhost:6379 >> backend\.env
    echo JWT_SECRET=dev-secret-key-change-in-production >> backend\.env
    echo CORS_ORIGIN=http://localhost:3000 >> backend\.env
    echo LOG_LEVEL=debug >> backend\.env
    echo ✅ Backend .env created
)

if not exist "frontend\.env" (
    echo VITE_API_URL=http://localhost:5000/api/v1 > frontend\.env
    echo VITE_APP_NAME=CarMatch >> frontend\.env
    echo VITE_ENVIRONMENT=development >> frontend\.env
    echo ✅ Frontend .env created
)

REM Create development startup script
echo @echo off > start-dev.bat
echo echo 🚀 Starting CarMatch development environment... >> start-dev.bat
echo echo Starting backend... >> start-dev.bat
echo start "Backend" cmd /k "cd backend && npm run dev" >> start-dev.bat
echo timeout /t 5 >> start-dev.bat
echo echo Starting frontend... >> start-dev.bat
echo start "Frontend" cmd /k "cd frontend && npm run dev" >> start-dev.bat
echo echo 🎉 CarMatch is running! >> start-dev.bat
echo echo Frontend: http://localhost:3000 >> start-dev.bat
echo echo Backend: http://localhost:5000 >> start-dev.bat

echo ✅ Development environment configured

REM Create VS Code settings
if not exist ".vscode" mkdir .vscode

echo { > .vscode\settings.json
echo   "editor.formatOnSave": true, >> .vscode\settings.json
echo   "editor.codeActionsOnSave": { >> .vscode\settings.json
echo     "source.fixAll.eslint": true >> .vscode\settings.json
echo   }, >> .vscode\settings.json
echo   "eslint.workingDirectories": ["backend", "frontend"], >> .vscode\settings.json
echo   "testing.automaticallyOpenPeekView": "failureInVisibleDocument", >> .vscode\settings.json
echo   "liveshare.presence": true, >> .vscode\settings.json
echo   "liveshare.showInStatusBar": "whileCollaborating" >> .vscode\settings.json
echo } >> .vscode\settings.json

echo ✅ VS Code workspace configured

REM Create setup summary
echo # 🎉 CarMatch XP Setup Complete! > SETUP-COMPLETE.md
echo. >> SETUP-COMPLETE.md
echo ## What was configured: >> SETUP-COMPLETE.md
echo. >> SETUP-COMPLETE.md
echo ✅ **Backend (TDD Ready)** >> SETUP-COMPLETE.md
echo - Jest test framework with TDD structure >> SETUP-COMPLETE.md
echo - Unit, Integration, and E2E test folders >> SETUP-COMPLETE.md
echo - Environment variables configured >> SETUP-COMPLETE.md
echo. >> SETUP-COMPLETE.md
echo ✅ **Frontend (E2E Ready)** >> SETUP-COMPLETE.md
echo - Cypress E2E testing framework >> SETUP-COMPLETE.md
echo - Component testing setup >> SETUP-COMPLETE.md
echo - Test fixtures and custom commands >> SETUP-COMPLETE.md
echo. >> SETUP-COMPLETE.md
echo ## Next Steps: >> SETUP-COMPLETE.md
echo. >> SETUP-COMPLETE.md
echo 1. **Start Development**: >> SETUP-COMPLETE.md
echo    ```batch >> SETUP-COMPLETE.md
echo    start-dev.bat >> SETUP-COMPLETE.md
echo    ``` >> SETUP-COMPLETE.md
echo. >> SETUP-COMPLETE.md
echo 2. **Run Your First TDD Cycle**: >> SETUP-COMPLETE.md
echo    ```batch >> SETUP-COMPLETE.md
echo    cd backend >> SETUP-COMPLETE.md
echo    npm run test:watch >> SETUP-COMPLETE.md
echo    ``` >> SETUP-COMPLETE.md
echo. >> SETUP-COMPLETE.md
echo 3. **Run E2E Tests**: >> SETUP-COMPLETE.md
echo    ```batch >> SETUP-COMPLETE.md
echo    cd frontend >> SETUP-COMPLETE.md
echo    npm run e2e:open >> SETUP-COMPLETE.md
echo    ``` >> SETUP-COMPLETE.md

echo.
echo 🎉 CarMatch XP Setup Complete!
echo ==============================================
echo ✅ All components configured successfully
echo ℹ️ Next steps:
echo   1. Run: start-dev.bat
echo   2. Open VS Code and install recommended extensions
echo   3. Read SETUP-COMPLETE.md for detailed instructions
echo   4. Start your first TDD cycle!
echo.
echo ℹ️ Happy coding with XP methodology! 🚀
pause
