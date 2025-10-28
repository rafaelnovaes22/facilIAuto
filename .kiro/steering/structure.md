# FacilIAuto - Project Structure

## Root Organization

```
FacilIAuto/
├── platform/           # Main platform code
├── agents/             # 12 specialized AI agents framework
├── docs/               # Centralized documentation
├── examples/           # Reference prototypes
├── .kiro/              # Kiro IDE configuration
├── README.md           # Project overview
└── start-faciliauto.*  # Quick start scripts
```

## Platform Structure

### Backend (`platform/backend/`)

```
backend/
├── api/
│   └── main.py                    # FastAPI application (all endpoints)
├── models/
│   ├── car.py                     # Car model with Pydantic
│   ├── dealership.py              # Dealership model
│   ├── user_profile.py            # User profile and preferences
│   ├── feedback.py                # Feedback system models
│   └── interaction.py             # ML interaction tracking
├── services/
│   ├── unified_recommendation_engine.py  # Main recommendation logic
│   ├── feedback_engine.py                # Iterative feedback system
│   ├── interaction_service.py            # ML data collection
│   ├── car_classifier.py                 # Car classification logic
│   └── car_metrics.py                    # Scoring algorithms
├── data/
│   ├── dealerships.json           # Dealership configurations
│   ├── robustcar_estoque.json     # RobustCar inventory
│   ├── autocenter_estoque.json    # AutoCenter inventory
│   ├── carplus_estoque.json       # CarPlus inventory
│   └── interactions/              # ML interaction logs
├── tests/
│   ├── conftest.py                # Pytest fixtures
│   ├── test_models.py             # Model validation tests
│   ├── test_recommendation_engine.py  # Engine logic tests
│   ├── test_api_integration.py    # API endpoint tests
│   ├── test_fase2_feedback.py     # Feedback system tests
│   └── test_ml_*.py               # ML system tests
├── scripts/
│   ├── calibrate_scores.py        # Score calibration tools
│   ├── analyze_metrics.py         # Metrics analysis
│   └── validate_car_data.py       # Data validation
├── utils/
│   └── geo_distance.py            # Geographic utilities
├── monitoring/
│   └── prometheus.yml             # Prometheus config
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Pytest configuration
├── Dockerfile                     # Container definition
├── docker-compose.yml             # Multi-service orchestration
└── README.md                      # Backend documentation
```

### Frontend (`platform/frontend/`)

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/                # Reusable UI components
│   │   ├── questionnaire/         # Questionnaire step components
│   │   ├── results/               # Results display components
│   │   └── dealership/            # Dealership-specific components
│   ├── pages/
│   │   ├── HomePage.tsx           # Landing page
│   │   ├── QuestionnairePage.tsx  # User profiling flow
│   │   └── ResultsPage.tsx        # Recommendations display
│   ├── services/
│   │   ├── api.ts                 # Backend API client
│   │   └── InteractionTracker.ts  # ML interaction tracking
│   ├── store/
│   │   └── questionnaireStore.ts  # Zustand state management
│   ├── hooks/
│   │   └── useApi.ts              # Custom React hooks
│   ├── types/
│   │   └── index.ts               # TypeScript type definitions
│   ├── theme/
│   │   └── index.ts               # Chakra UI theme customization
│   ├── utils/
│   │   └── imagePlaceholder.ts    # Utility functions
│   ├── App.tsx                    # Root component
│   └── main.tsx                   # Application entry point
├── cypress/                       # E2E tests
├── tests/                         # Unit tests
├── package.json                   # Node dependencies
├── vite.config.ts                 # Vite configuration
├── tsconfig.json                  # TypeScript configuration
└── README.md                      # Frontend documentation
```

## Agents Framework (`agents/`)

12 specialized agents providing context and expertise:

```
agents/
├── ai-engineer/                   # AI and ML expertise
├── tech-lead/                     # Technical leadership
├── ux-especialist/                # UX/UI design
├── system-architecture/           # System design
├── business-analyst/              # Business analysis
├── product-manager/               # Product strategy
├── marketing-strategist/          # Marketing and growth
├── financial-advisor/             # Financial strategy
├── sales-coach/                   # Sales optimization
├── operations-manager/            # Operations and processes
├── data-analyst/                  # Data insights
├── content-creator/               # Content and storytelling
├── agent-cli.py                   # CLI tool for agents
├── orchestrator.py                # Agent orchestration
└── README.md                      # Framework documentation
```

Each agent has a `context.md` file with expertise and guidelines.

## Documentation (`docs/`)

```
docs/
├── business/                      # Business strategy documents
├── technical/                     # Technical architecture docs
├── implementation/                # XP/TDD implementation guides
├── guides/                        # Practical how-to guides
├── reports/                       # Validation and status reports
└── troubleshooting/               # Common issues and solutions
```

## Examples (`examples/`)

Reference implementations and prototypes:

```
examples/
├── CarRecommendationSite/         # XP/TDD/E2E complete example
├── RobustCar/                     # Single-tenant POC
└── README.md                      # Examples documentation
```

## Key Conventions

### File Naming
- **Python**: `snake_case.py` (PEP 8)
- **TypeScript**: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **Tests**: `test_*.py` (Python), `*.test.ts` (TypeScript)
- **Config**: `lowercase.json`, `lowercase.yml`

### Directory Naming
- **Lowercase with hyphens**: `platform/backend/`
- **Plural for collections**: `models/`, `services/`, `tests/`
- **Singular for single purpose**: `api/`, `monitoring/`

### Import Conventions

**Python (Backend)**:
```python
# Standard library first
import os
import sys

# Third-party packages
from fastapi import FastAPI
from pydantic import BaseModel

# Local imports
from models.car import Car
from services.unified_recommendation_engine import UnifiedRecommendationEngine
```

**TypeScript (Frontend)**:
```typescript
// React and external libraries
import { useState } from 'react'
import { Box, Button } from '@chakra-ui/react'

// Local imports with @ alias
import { api } from '@/services/api'
import type { Car } from '@/types'
```

### Test Organization
- **Co-located with source**: Tests in `tests/` directory mirror source structure
- **Fixtures**: Shared fixtures in `conftest.py` (Python) or `test-setup.ts` (TypeScript)
- **Naming**: `test_<feature>.py` or `<Component>.test.tsx`

### Documentation Location
- **API docs**: Auto-generated at `/docs` endpoint (FastAPI)
- **Code docs**: Docstrings (Python), JSDoc (TypeScript)
- **Project docs**: `docs/` directory
- **Component docs**: README.md in each major directory

## Data Flow

```
User (Browser)
    ↓
Frontend (React + TypeScript)
    ↓ HTTP/REST
Backend API (FastAPI)
    ↓
Services (Recommendation Engine)
    ↓
Data (JSON files)
```

## Multi-Tenant Architecture

- **Dealerships**: Configured in `data/dealerships.json`
- **Inventory**: Separate JSON file per dealership (`{dealership_id}_estoque.json`)
- **Aggregation**: Engine loads all dealerships and cars at startup
- **Filtering**: Geographic and preference-based filtering at query time

## Configuration Files

- **Backend**: `requirements.txt`, `pytest.ini`, `docker-compose.yml`
- **Frontend**: `package.json`, `vite.config.ts`, `tsconfig.json`
- **CI/CD**: `.github/workflows/` (GitHub Actions)
- **IDE**: `.kiro/` (Kiro configuration)
