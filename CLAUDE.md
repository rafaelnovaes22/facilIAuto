# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FacilIAuto is a production-ready B2B SaaS platform for automotive sales that combines:
- Multi-tenant vehicle recommendation system with unified engine aggregating multiple dealerships
- WhatsApp chatbot with LangGraph conversational AI
- React TypeScript frontend with mobile-first design
- FastAPI Python backend with comprehensive testing

## Development Commands

### Backend (FastAPI + Python 3.11)

Located in `platform/backend/`

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python api/main.py

# Run all tests with coverage
pytest tests/ -v --cov

# Run specific test file
pytest tests/test_recommendation_engine.py -v

# Run tests matching pattern
pytest tests/ -k "test_commercial" -v

# API endpoints
http://localhost:8000        # API base
http://localhost:8000/docs   # Swagger documentation
http://localhost:8000/health # Health check
```

### Frontend (React + TypeScript + Vite)

Located in `platform/frontend/`

```bash
# Install dependencies
npm install

# Development server
npm run dev  # http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview

# Run unit tests (Vitest)
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run E2E tests (Cypress)
npm run e2e          # Headless
npm run e2e:open     # Interactive GUI
npm run e2e:ci       # CI mode with server start

# Lint and format
npm run lint
npm run format
```

### Chatbot (WhatsApp + LangGraph)

Located in `platform/chatbot/`

```bash
# Copy environment file
cp .env.example .env

# Install with Poetry
poetry install

# Run with Docker Compose (recommended)
docker-compose up -d

# Run locally
poetry run uvicorn src.main:app --reload --port 8001

# Run tests
poetry run pytest tests/ -v

# Run Celery worker
poetry run python start_worker.py

# Run Celery beat scheduler
poetry run celery -A src.tasks.celery_app beat
```

### Complete System Startup

**Windows:**
```bash
# From project root
scripts\start-faciliauto.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/start-faciliauto.sh
./scripts/start-faciliauto.sh
```

## Architecture Overview

### Multi-Tenant Data Flow

The system aggregates vehicles from multiple dealerships through a unified recommendation engine:

1. **Data Sources** - JSON files per dealership in `platform/backend/data/`:
   - `dealerships.json` - Dealership metadata
   - `{dealership}_estoque.json` - Individual inventories (robustcar_estoque.json, autocenter_estoque.json, etc.)

2. **Unified Engine** - `services/unified_recommendation_engine.py`:
   - Loads all dealership inventories into unified pool
   - Applies multi-criteria scoring algorithm (budget, preferences, use case)
   - Returns diverse results across dealerships
   - Maintains dealership context in results

3. **API Layer** - `api/main.py`:
   - Exposes RESTful endpoints for recommendations
   - Handles filtering by dealership_id, brand, model, year, etc.
   - Serves static images from `data/images/`

### Recommendation Scoring System

Located in `services/unified_recommendation_engine.py`:

The scoring algorithm evaluates vehicles across multiple dimensions:

- **Budget Match** (40% weight): Price alignment with user budget
- **Use Case Fit** (30% weight): Vehicle classification vs. user's primary use (transport app, commercial, family, etc.)
- **TCO Score** (15% weight): Total Cost of Ownership (fuel efficiency, maintenance)
- **Preference Match** (15% weight): Brand/model/fuel type preferences

Key service files:
- `unified_recommendation_engine.py` - Main recommendation logic
- `car_classifier.py` - Classifies vehicles by use case (transport app, commercial, etc.)
- `tco_calculator.py` - Total Cost of Ownership calculations
- `feedback_engine.py` - Iterative refinement based on user feedback
- `fuel_price_service.py` - Real-time fuel price integration
- `context_based_recommendation_skill.py` - Context-aware search with LLM integration
- `search_intent_classifier.py` - NLP-based search intent classification

### Frontend Component Architecture

Located in `platform/frontend/src/`:

**Pages** (`pages/`):
- `HomePage.tsx` - Landing with CTAs, testimonials, trust badges
- `QuestionnairePage.tsx` - 4-step interactive questionnaire
- `ResultsPage.tsx` - Vehicle recommendations with gallery and comparison
- `DealershipInventoryPage.tsx` - Dealership-specific inventory view

**Component Categories** (`components/`):
- `common/` - Shared components (Header, Footer, LoadingSpinner, ErrorBoundary)
- `questionnaire/` - Multi-step form components (Steps, ProgressBar, BrandSelector)
- `results/` - Result display (CarCard, Comparison, Financing, Gallery)

**State Management**:
- Zustand stores in `store/` for app state
- React Query in `services/` for server state and caching

**Testing**:
- Vitest for unit tests with jsdom
- Cypress E2E tests in `cypress/e2e/`
- Testing library utilities in `__tests__/`

### Chatbot Conversational Flow

Located in `platform/chatbot/src/`:

**State Machine** (`services/conversation_engine.py`):
```
GREETING → VEHICLE_SEARCH → QUALIFICATION → FINANCING → HANDOFF
```

Key components:
- `conversation_engine.py` - LangGraph-based state machine
- `nlp_service.py` - Natural language processing for intent extraction
- `backend_client.py` - HTTP client for recommendation API
- `whatsapp_client.py` - Meta WhatsApp Business API integration
- `session_manager.py` - Redis-based session persistence
- `guardrails.py` - Safety checks and content validation

**Infrastructure**:
- Redis - Session storage and caching
- PostgreSQL - Persistent conversation history
- DuckDB - Analytics and reporting
- Celery + Redis - Asynchronous task queue (audio transcription, webhook processing)

### Scrapers

Located in `platform/scrapers/`:

Extract dealership inventory from websites:
- `robustcar_scraper.py` - RobustCar dealership
- `rpmultimarcas_scraper.py` - RP Multimarcas
- Output to JSON in `platform/backend/data/`

## Testing Strategy

### Backend Tests (pytest)

All tests in `platform/backend/tests/`:

**Test Categories**:
- `test_models.py` - Pydantic model validation
- `test_recommendation_engine.py` - Core algorithm testing
- `test_api_integration.py` - Full API flow tests
- `test_fase1_filtros.py` - Filter validation (Phase 1)
- `test_fase2_feedback.py` - Feedback refinement (Phase 2)
- `test_fase3_metricas.py` - Analytics and metrics (Phase 3)
- `test_ml_*_e2e.py` - End-to-end ML integration tests

**Test Fixtures** (`conftest.py`):
- Shared fixtures for cars, dealerships, user profiles
- TestClient for API testing
- Mock data generators

**Running Tests**:
```bash
# All tests with verbose output and coverage
pytest tests/ -v --cov

# Specific test file
pytest tests/test_recommendation_engine.py -v

# Tests matching pattern
pytest tests/ -k "commercial" -v

# Stop on first failure
pytest tests/ -x
```

### Frontend Tests

**Unit Tests** (Vitest + Testing Library):
- Component behavior and rendering
- Hook logic and state management
- Utility functions

**E2E Tests** (Cypress):
- `cypress/e2e/user-journey.cy.ts` - Complete user flow (398 lines)
- `cypress/e2e/simple-validation.cy.ts` - Basic validations
- Uses `data-testid` attributes for reliable selectors

### Chatbot Tests

Located in `platform/chatbot/tests/`:
- Unit tests for conversation flows
- Mock WhatsApp webhooks
- Redis session validation
- NLP intent classification tests

## Code Standards

### Python (Backend)

Following XP methodology with TDD:

- **Style**: PEP 8 compliant, Black formatter (line length 88)
- **Type Hints**: Required for all function signatures
- **Docstrings**: Required for public methods
- **Testing**: Write tests BEFORE implementation (Red-Green-Refactor)
- **Coverage**: Maintain ≥ 80% test coverage

Example:
```python
from typing import List, Optional
from models.user_profile import UserProfile
from models.car import Car

def recommend_cars(
    profile: UserProfile,
    limit: int = 10,
    dealership_id: Optional[str] = None
) -> List[Car]:
    """
    Generate vehicle recommendations based on user profile.

    Args:
        profile: User profile with preferences and constraints
        limit: Maximum number of recommendations
        dealership_id: Optional filter for specific dealership

    Returns:
        Ordered list of recommended vehicles with scores
    """
    pass
```

### TypeScript (Frontend)

- **Strict Mode**: Enabled, no implicit any
- **Components**: Functional components with TypeScript interfaces
- **Props**: Explicit interface definitions
- **Testing**: data-testid attributes for E2E tests
- **Style**: ESLint + Prettier, 2-space indentation

Example:
```typescript
interface CarCardProps {
  car: Car
  onSelect: (car: Car) => void
  showScore?: boolean
}

export const CarCard: React.FC<CarCardProps> = ({
  car,
  onSelect,
  showScore = false
}) => {
  return (
    <div data-testid={`car-card-${car.id}`}>
      <h3>{car.nome}</h3>
      {showScore && <span>{car.score}</span>}
      <button
        data-testid={`select-car-${car.id}`}
        onClick={() => onSelect(car)}
      >
        Selecionar
      </button>
    </div>
  )
}
```

### Commit Conventions

Format: `type(scope): message`

Types:
- `feat` - New feature
- `fix` - Bug fix
- `test` - Add/modify tests
- `docs` - Documentation
- `refactor` - Code refactoring
- `chore` - Maintenance tasks

Examples:
```bash
git commit -m "feat(engine): add multi-dealership scoring"
git commit -m "test(e2e): add mobile user journey tests"
git commit -m "fix(api): correct TCO calculation for hybrid vehicles"
```

## Key Design Patterns

### Multi-Tenant Architecture

Each dealership is a tenant with isolated inventory but shared infrastructure:

1. Dealership metadata in `dealerships.json`
2. Separate inventory files per dealership
3. Unified engine aggregates all inventories
4. Results maintain dealership_id for attribution
5. Optional filtering by dealership_id in API

### Recommendation Algorithm Extensibility

To add new scoring criteria:

1. Add new service in `platform/backend/services/`
2. Implement scoring method returning 0-1 normalized score
3. Integrate in `unified_recommendation_engine.py`'s `calculate_match_score()`
4. Adjust weights in scoring algorithm
5. Add tests in `tests/test_recommendation_engine.py`

### Chatbot Context Management

Conversation state is managed through:

1. **LangGraph State Machine** - Defines conversation flow and transitions
2. **Redis Sessions** - Short-term context (current conversation)
3. **PostgreSQL History** - Long-term conversation history
4. **Context Injection** - User profile + conversation history passed to LLM

### Frontend State Architecture

Two-tier state management:

1. **Server State** (React Query):
   - API data fetching and caching
   - Automatic background refetching
   - Optimistic updates

2. **Client State** (Zustand):
   - User questionnaire responses
   - UI state (modals, filters)
   - Local preferences

## Common Tasks

### Adding a New Dealership

1. Add dealership metadata to `platform/backend/data/dealerships.json`:
```json
{
  "id": "newdealer",
  "nome": "New Dealer Motors",
  "cidade": "São Paulo",
  "estado": "SP",
  "site": "https://newdealer.com.br",
  "telefone": "(11) 9999-9999",
  "email": "contato@newdealer.com.br",
  "logo_url": "/static/images/logos/newdealer.png"
}
```

2. Create inventory file `newdealer_estoque.json` with car data
3. Restart backend - engine auto-loads new dealership
4. Verify with: `GET /api/dealerships`

### Adding a New API Endpoint

1. Define request/response models in `platform/backend/models/`
2. Add endpoint in `platform/backend/api/main.py`:
```python
@app.post("/api/new-endpoint", response_model=ResponseModel)
async def new_endpoint(request: RequestModel):
    """Endpoint description for OpenAPI docs"""
    # Implementation
    return response
```
3. Add tests in `tests/test_api_integration.py`
4. Verify in Swagger: http://localhost:8000/docs

### Updating Vehicle Classification Logic

Edit `platform/backend/services/car_classifier.py`:

1. Modify `classify_car()` method
2. Update classification criteria (cargo capacity, passenger count, etc.)
3. Add/modify tests in `tests/test_car_classification.py`
4. Run tests: `pytest tests/test_car_classification.py -v`

### Debugging Recommendation Scores

Enable debug logging in recommendation engine:

1. In `unified_recommendation_engine.py`, uncomment debug prints
2. Or add breakpoint in `calculate_match_score()` method
3. Call API with verbose=true parameter (if implemented)
4. Check score breakdown in response

## Project Structure Notes

- **`/platform`** - Main production codebase (backend, frontend, chatbot, scrapers)
- **`/examples`** - Reference prototypes and proof-of-concepts (CarRecommendationSite, RobustCar)
- **`/agents`** - 12 specialized AI agent context files for development assistance
- **`/docs`** - Extensive documentation (134+ files) organized by category
- **`/data`** - Additional data files not in platform/backend/data
- **`/.kiro`** - Kiro AI specifications and task management
- **`/scripts`** - Startup and utility scripts for full system

The examples folder contains earlier prototypes that informed the platform design. When working on the platform, use `platform/` as the source of truth.

## Important Implementation Details

### Transport App Validation

Located in `services/app_transport_validator.py` and `services/commercial_vehicle_validator.py`:

Validates vehicles for ride-sharing apps (Uber, 99, etc.) based on:
- Year restrictions (typically 2015+)
- Passenger capacity requirements
- Safety features (airbags, ABS, etc.)
- Vehicle condition and documentation

Used in recommendations when user selects "transporte por aplicativo" as primary use.

### Fuel Price Integration

`services/fuel_price_service.py` fetches real-time fuel prices from ANP (Agência Nacional do Petróleo) API for accurate TCO calculations. Caches prices with 24-hour TTL.

### Context-Based Search

`services/context_based_recommendation_skill.py` implements LLM-powered contextual search:

- Natural language query understanding
- Intent classification (explore vs. specific search)
- Context-aware filtering based on conversation history
- Fallback to traditional filtering when appropriate

### ML User Learning (Phase 2)

Framework for tracking user interactions and learning preferences:

- `services/interaction_service.py` - Track clicks, time spent, feedback
- `tests/test_ml_*_e2e.py` - E2E tests for interaction tracking
- Future: Personalized scoring based on historical interactions

## Documentation References

For detailed information, see:

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines and XP methodology
- **[FOR-RECRUITERS.md](FOR-RECRUITERS.md)** - Technical evaluation and project showcase
- **[platform/README.md](platform/README.md)** - Platform-specific documentation
- **[platform/chatbot/README.md](platform/chatbot/README.md)** - Chatbot architecture and setup
- **[agents/README.md](agents/README.md)** - AI agent framework
- **[docs/guides/COMO-RODAR-FACILIAUTO.md](docs/guides/COMO-RODAR-FACILIAUTO.md)** - Detailed setup guide
- **[docs/technical/](docs/technical/)** - Technical architecture documents

## Environment Variables

### Backend
No required environment variables for basic operation. Optional:
- `FRONTEND_URL` - CORS configuration for production

### Chatbot (required)
Located in `platform/chatbot/.env`:
```
# WhatsApp Business API
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_ACCESS_TOKEN=your_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_id

# OpenAI API
OPENAI_API_KEY=your_api_key

# Database
REDIS_URL=redis://localhost:6379/0
POSTGRES_URL=postgresql://user:pass@localhost:5432/faciliauto_chatbot
DUCKDB_PATH=./data/chatbot.duckdb

# Backend API
BACKEND_API_URL=http://localhost:8000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

## Performance Considerations

### Backend
- Recommendation engine loads all inventories into memory at startup
- Typical response time: <100ms for basic recommendations
- Scales to ~10k vehicles before optimization needed
- Consider Redis caching for high-traffic scenarios

### Frontend
- Vite build with code splitting for optimal loading
- Images lazy-loaded with Chakra UI's Image component
- React Query caches API responses with 5-minute stale time
- Framer Motion animations use CSS transforms for 60fps

### Chatbot
- Redis session cache prevents database hits on every message
- Celery workers process audio transcription asynchronously
- LangGraph state machine minimizes LLM API calls
- DuckDB analytics queries run on separate thread

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.11+)
- Verify data files exist in `platform/backend/data/`
- Check port 8000 is available

### Frontend build fails
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (need 18+)
- Verify Vite config in `vite.config.ts`

### Tests failing
- Backend: Check pytest version and conftest.py fixtures
- Frontend: Ensure jsdom is installed for Vitest
- E2E: Verify Cypress browser compatibility

### Chatbot not responding
- Check Redis connection: `redis-cli ping`
- Verify WhatsApp webhook is reachable
- Check Celery workers are running: `celery -A src.tasks.celery_app status`
- Review logs in docker-compose logs

For more troubleshooting, see `docs/troubleshooting/` directory.
