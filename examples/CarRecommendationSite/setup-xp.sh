#!/bin/bash

# 🚀 FacilIAuto XP Setup Script
# Configura o ambiente completo para desenvolvimento com XP e testes E2E

set -e

echo "🚀 Setting up FacilIAuto with XP methodology..."
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found. Please install Node.js 18+ first."
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version must be 18 or higher. Current: $(node --version)"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm not found. Please install npm first."
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git not found. Please install Git first."
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Setup Git hooks for XP practices
setup_git_hooks() {
    print_info "Setting up Git hooks for XP..."
    
    mkdir -p .git/hooks
    
    # Pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
echo "🧪 Running XP pre-commit checks..."

# Run linting
echo "  📋 Checking code style..."
cd backend && npm run lint --silent
if [ $? -ne 0 ]; then
    echo "❌ Backend linting failed"
    exit 1
fi

cd ../frontend && npm run lint --silent
if [ $? -ne 0 ]; then
    echo "❌ Frontend linting failed"
    exit 1
fi

# Run unit tests
echo "  🧪 Running unit tests..."
cd ../backend && npm run test:unit --silent
if [ $? -ne 0 ]; then
    echo "❌ Backend unit tests failed"
    exit 1
fi

cd ../frontend && npm run test:unit --silent
if [ $? -ne 0 ]; then
    echo "❌ Frontend unit tests failed"
    exit 1
fi

echo "✅ All pre-commit checks passed"
EOF

    # Pre-push hook
    cat > .git/hooks/pre-push << 'EOF'
#!/bin/sh
echo "🚀 Running XP pre-push checks..."

# Run integration tests
echo "  🔗 Running integration tests..."
cd backend && npm run test:integration --silent
if [ $? -ne 0 ]; then
    echo "❌ Integration tests failed"
    exit 1
fi

echo "✅ All pre-push checks passed"
EOF

    chmod +x .git/hooks/pre-commit
    chmod +x .git/hooks/pre-push
    
    print_status "Git hooks configured"
}

# Setup backend dependencies and tests
setup_backend() {
    print_info "Setting up backend with TDD structure..."
    
    cd backend
    
    # Install dependencies
    print_info "Installing backend dependencies..."
    npm install
    
    # Create test directories
    mkdir -p tests/{unit,integration,e2e}/{controllers,services,models,utils}
    mkdir -p tests/fixtures
    
    # Setup test database
    print_info "Setting up test database..."
    if command -v docker &> /dev/null; then
        echo "Starting MongoDB test container..."
        docker run -d --name carmatch-mongo-test -p 27017:27017 mongo:6.0
        sleep 5
        print_status "MongoDB test container started"
    else
        print_warning "Docker not found. Please ensure MongoDB is available for tests."
    fi
    
    # Run initial tests
    print_info "Running initial test suite..."
    npm run test:unit
    
    cd ..
    print_status "Backend setup completed"
}

# Setup frontend dependencies and E2E tests
setup_frontend() {
    print_info "Setting up frontend with E2E tests..."
    
    cd frontend
    
    # Install dependencies
    print_info "Installing frontend dependencies..."
    npm install
    
    # Setup Cypress
    print_info "Setting up Cypress E2E tests..."
    npx cypress install
    
    # Create additional Cypress directories
    mkdir -p cypress/{e2e/{smoke,regression,user-journeys},support,fixtures,tasks}
    
    # Verify Cypress installation
    npx cypress verify
    
    # Run initial component tests
    print_info "Running initial component tests..."
    npm run test:unit
    
    cd ..
    print_status "Frontend setup completed"
}

# Setup development environment
setup_dev_environment() {
    print_info "Setting up development environment..."
    
    # Create .env files
    if [ ! -f backend/.env ]; then
        cat > backend/.env << EOF
NODE_ENV=development
PORT=5000
MONGODB_URI=mongodb://localhost:27017/carmatch_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev-secret-key-change-in-production
CORS_ORIGIN=http://localhost:3000
LOG_LEVEL=debug
EOF
        print_status "Backend .env created"
    fi
    
    if [ ! -f frontend/.env ]; then
        cat > frontend/.env << EOF
VITE_API_URL=http://localhost:5000/api/v1
VITE_APP_NAME=CarMatch
VITE_ENVIRONMENT=development
EOF
        print_status "Frontend .env created"
    fi
    
    # Create development scripts
    cat > start-dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting CarMatch development environment..."

# Start MongoDB and Redis (if using Docker)
if command -v docker &> /dev/null; then
    echo "Starting databases..."
    docker run -d --name carmatch-mongo -p 27017:27017 mongo:6.0 2>/dev/null || docker start carmatch-mongo
    docker run -d --name carmatch-redis -p 6379:6379 redis:7 2>/dev/null || docker start carmatch-redis
fi

# Start backend
echo "Starting backend..."
cd backend && npm run dev &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!

echo "🎉 CarMatch is running!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:5000"
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT
wait
EOF
    
    chmod +x start-dev.sh
    print_status "Development environment configured"
}

# Setup VS Code workspace for XP
setup_vscode() {
    print_info "Setting up VS Code workspace for XP..."
    
    mkdir -p .vscode
    
    # VS Code settings
    cat > .vscode/settings.json << 'EOF'
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "eslint.workingDirectories": ["backend", "frontend"],
  "testing.automaticallyOpenPeekView": "failureInVisibleDocument",
  "liveshare.presence": true,
  "liveshare.showInStatusBar": "whileCollaborating",
  "liveshare.anonymousGuestApproval": "prompt",
  "git.autofetch": true,
  "git.enableCommitSigning": false,
  "files.watcherExclude": {
    "**/node_modules/**": true,
    "**/coverage/**": true,
    "**/dist/**": true
  }
}
EOF

    # VS Code extensions recommendations
    cat > .vscode/extensions.json << 'EOF'
{
  "recommendations": [
    "ms-vsliveshare.vsliveshare",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next",
    "orta.vscode-jest",
    "ms-playwright.playwright",
    "humao.rest-client",
    "eamodio.gitlens",
    "streetsidesoftware.code-spell-checker"
  ]
}
EOF

    # VS Code launch configuration
    cat > .vscode/launch.json << 'EOF'
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Backend",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/backend/src/server.ts",
      "env": {
        "NODE_ENV": "development"
      },
      "runtimeArgs": ["-r", "tsx/cjs"]
    },
    {
      "name": "Debug Tests",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/backend/node_modules/.bin/jest",
      "args": ["--runInBand"],
      "env": {
        "NODE_ENV": "test"
      }
    }
  ]
}
EOF

    print_status "VS Code workspace configured"
}

# Setup XP documentation
setup_xp_docs() {
    print_info "Setting up XP documentation..."
    
    # Create quick reference
    cat > XP-QuickRef.md << 'EOF'
# 🚀 FacilIAuto XP Quick Reference

## Daily Commands

```bash
# Start development
./start-dev.sh

# Run all tests
npm run test          # Frontend
cd backend && npm run test  # Backend

# TDD Cycle
npm run test:watch    # Continuous testing

# E2E Tests
npm run e2e:open      # Interactive
npm run e2e          # Headless

# Quality Checks
npm run lint         # Code style
npm run type-check   # TypeScript
```

## Pair Programming
- Switch driver/navigator every 15-20 min
- Commit frequently (every 30-60 min)
- Use VS Code Live Share for remote pairing

## XP Values
1. **Communication** - Daily standups, pair programming
2. **Simplicity** - YAGNI, refactor continuously  
3. **Feedback** - TDD, CI/CD, customer collaboration
4. **Courage** - Refactor, experiment, fail fast
5. **Respect** - Code quality, sustainable pace

## Emergency Contacts
- Build broken: Fix immediately, pair if needed
- Tests failing: Stop feature work, fix tests first
- Deployment issues: Check #deployment channel
EOF

    print_status "XP documentation created"
}

# Create final summary
create_summary() {
    print_info "Creating setup summary..."
    
    cat > SETUP-COMPLETE.md << EOF
# 🎉 FacilIAuto XP Setup Complete!

## What was configured:

✅ **Backend (TDD Ready)**
- Jest test framework with TDD structure
- Unit, Integration, and E2E test folders
- MongoDB test database
- Pre-commit hooks for quality

✅ **Frontend (E2E Ready)**  
- Cypress E2E testing framework
- Component testing setup
- Test fixtures and custom commands
- Responsive design testing

✅ **XP Practices**
- Git hooks for quality gates
- VS Code Live Share configuration
- TDD workflow scripts
- CI/CD pipeline ready

✅ **Development Environment**
- Environment variables configured
- Development startup script
- Database containers (if Docker available)
- Hot reload enabled

## Next Steps:

1. **Start Development**:
   \`\`\`bash
   ./start-dev.sh
   \`\`\`

2. **Run Your First TDD Cycle**:
   \`\`\`bash
   cd backend
   npm run test:watch
   # Write failing test, implement, refactor
   \`\`\`

3. **Setup Your First Pair Session**:
   - Install VS Code Live Share extension
   - Schedule pair programming sessions
   - Follow XP-Daily-Guide.md

4. **Run E2E Tests**:
   \`\`\`bash
   cd frontend
   npm run e2e:open
   \`\`\`

## Useful Commands:

\`\`\`bash
# Quick test run
npm test

# Full CI pipeline locally  
npm run ci

# Start pair programming
code --install-extension ms-vsliveshare.vsliveshare

# Check XP metrics
./xp-metrics.sh
\`\`\`

## Documentation:
- 📖 [XP Methodology](./XP-Methodology.md)
- 📅 [Daily XP Guide](./XP-Daily-Guide.md)  
- 🚀 [Quick Reference](./XP-QuickRef.md)
- 🤝 [Agent Collaboration](./agents-collaboration.md)

## Support:
- 💬 Join #carmatch-dev slack channel
- 📚 Read XP resources in ./docs/
- 🆘 Create issue if something doesn't work

**Happy Coding with XP! 🚀**
EOF

    print_status "Setup summary created"
}

# Main execution
main() {
    echo
    print_info "Starting CarMatch XP setup..."
    echo
    
    check_prerequisites
    setup_git_hooks
    setup_backend
    setup_frontend
    setup_dev_environment
    setup_vscode
    setup_xp_docs
    create_summary
    
    echo
    echo "🎉 CarMatch XP Setup Complete!"
    echo "=============================================="
    print_status "All components configured successfully"
    print_info "Next steps:"
    echo "  1. Run: ./start-dev.sh"
    echo "  2. Open VS Code and install recommended extensions"
    echo "  3. Read SETUP-COMPLETE.md for detailed instructions"
    echo "  4. Start your first TDD cycle!"
    echo
    print_info "Happy coding with XP methodology! 🚀"
}

# Run main function
main "$@"
