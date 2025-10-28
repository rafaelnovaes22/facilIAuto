# FacilIAuto - Technical Stack

## Architecture

**Multi-tenant B2B SaaS** with clean separation between backend API and frontend client.

## Backend Stack

### Core Technologies
- **Python 3.10+**
- **FastAPI** - Modern async web framework with automatic OpenAPI docs
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server

### Testing & Quality
- **pytest** - Testing framework
- **pytest-cov** - Code coverage (target: ≥80%)
- **pytest-asyncio** - Async test support
- **httpx** - HTTP client for API testing
- **black** - Code formatting
- **flake8** - Linting
- **mypy** - Type checking

### Production
- **Docker** + **docker-compose** - Containerization
- **Nginx** - Reverse proxy
- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboards

## Frontend Stack

### Core Technologies
- **React 18** with **TypeScript**
- **Vite** - Build tool and dev server
- **Chakra UI** - Component library (mobile-first design system)
- **React Router** - Client-side routing

### State & Data
- **Zustand** - Lightweight state management
- **TanStack React Query** - Server state management and caching
- **Axios** - HTTP client

### Testing
- **Vitest** - Unit testing (53 tests)
- **Testing Library** - Component testing
- **Cypress** - E2E testing (18 tests)

### Code Quality
- **ESLint** - Linting
- **Prettier** - Code formatting
- **TypeScript** - Type safety

## Common Commands

### Backend

```bash
# Setup (first time)
cd platform/backend
pip install -r requirements.txt

# Run API (development)
python api/main.py
# Access: http://localhost:8000
# Docs: http://localhost:8000/docs

# Run tests (TDD workflow)
pytest tests/ -v
pytest --cov=. --cov-report=term-missing
pytest --cov=. --cov-report=html  # HTML report

# Code quality
black .                    # Format code
flake8 .                   # Lint
mypy .                     # Type check

# Quick scripts (Windows)
setup.bat                  # Install dependencies
run-tests.bat              # Run all tests

# Quick scripts (Linux/Mac)
./setup.sh                 # Install dependencies
./run-tests.sh             # Run all tests

# Docker (production)
docker-compose up -d       # Start all services
docker-compose down        # Stop services
docker-compose ps          # Check status
```

### Frontend

```bash
# Setup (first time)
cd platform/frontend
npm install

# Development
npm run dev                # Start dev server (http://localhost:3000)
npm run build              # Production build
npm run preview            # Preview production build

# Testing
npm test                   # Unit tests (watch mode)
npm run test:coverage      # Coverage report
npm run e2e                # E2E tests (headless)
npm run e2e:open           # E2E tests (interactive)
npm run test:all           # All tests

# Code quality
npm run lint               # ESLint
npm run format             # Prettier
```

### Full System

```bash
# Windows
start-faciliauto.bat       # Start backend + frontend

# Linux/Mac
./start-faciliauto.sh      # Start backend + frontend
```

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /stats` - Platform statistics
- `GET /dealerships` - List dealerships
- `GET /cars` - List cars (with filters)
- `POST /recommend` - Get personalized recommendations

### Feedback System (Phase 2)
- `POST /feedback` - Submit user feedback
- `POST /refine-recommendations` - Iterative refinement
- `GET /feedback/history/{user_id}` - User history

### ML System (Data Collection)
- `POST /api/interactions/track` - Track user interactions
- `GET /api/ml/stats` - ML system statistics

## Development Methodology

### XP (Extreme Programming)
- **TDD (Test-Driven Development)**: Red-Green-Refactor cycle
- **Continuous Integration**: Automated testing on every commit
- **Continuous Refactoring**: Keep code clean and simple
- **Collective Code Ownership**: Anyone can modify any code
- **Coding Standards**: PEP 8 (Python), ESLint (TypeScript)
- **Simple Design**: YAGNI, DRY, SOLID principles

### Testing Strategy
- **Unit Tests**: 100% coverage for models and core logic
- **Integration Tests**: 100% coverage for API endpoints
- **E2E Tests**: Critical user flows
- **Coverage Target**: ≥80% overall

### Commit Conventions
```
feat: add new feature
fix: bug fix
docs: documentation update
test: add or update tests
refactor: code refactoring
style: formatting changes
chore: maintenance tasks
```

## Code Style

### Python
- **PEP 8** compliance
- **Type hints** on all functions
- **Docstrings** for public APIs
- **Max line length**: 100 characters
- **Black** for formatting

### TypeScript
- **Strict mode** enabled
- **Explicit types** (avoid `any`)
- **JSDoc** for complex functions
- **ESLint** + **Prettier** for consistency

## Performance Targets

- **API Response Time**: <100ms (average)
- **Frontend Load Time**: <2s
- **Test Suite**: <10s (backend), <30s (frontend)
- **Code Coverage**: ≥80%

## Data Storage

- **JSON files** for car inventory and dealership data (current)
- **File-based** interaction tracking for ML (current)
- **Future**: PostgreSQL for production scale
