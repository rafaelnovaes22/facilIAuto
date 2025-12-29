# 🚗 **FacilIAuto - Intelligent Automotive Sales Platform**

<div align="center">

![FacilIAuto Logo](platform/frontend/src/faciliauto-logo.png)

**B2B SaaS automotive recommendation platform with conversational AI via WhatsApp**

[![Backend Status](https://img.shields.io/badge/Backend-Production--Ready-success?style=for-the-badge)]()
[![Frontend Status](https://img.shields.io/badge/Frontend-Production--Ready-success?style=for-the-badge)]()
[![Chatbot Status](https://img.shields.io/badge/Chatbot-Production--Ready-success?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

</div>

---

## 📋 **Table of Contents**

- [Overview](#-overview)
- [Project Status](#-project-status)
- [Architecture](#-architecture)
- [Components](#-components)
  - [Backend](#backend-rest-api-python--fastapi)
  - [Frontend](#frontend-react--typescript--chakra-ui)
  - [WhatsApp Chatbot](#whatsapp-chatbot-langgraph--pydantic-ai)
  - [Scrapers](#scrapers-data-extraction)
  - [AI Agents](#framework-of-12-specialized-agents)
- [How to Run](#-how-to-run)
- [Tech Stack](#-tech-stack)
- [Documentation](#-documentation)
- [Contributing](#-contributing)

---

## 🎯 **Overview**

**FacilIAuto** is a complete solution for dealerships and car stores that integrates:

1. **🌐 Recommendation Website** - Mobile-first web interface for lead capture
2. **🤖 WhatsApp Chatbot** - Intelligent assistant with conversational AI
3. **📊 Recommendation Engine** - Matching algorithm with intelligent scoring
4. **📱 Admin Panel** - Inventory and lead management

### ✨ **Key Differentiators**

| Aspect | **FacilIAuto** | Competitors |
|---------|----------------|--------------|
| **Mobile UX** | ✅ Native mobile-first | ❌ Adapted desktop |
| **Setup** | ✅ 30 minutes | ❌ 2-4 weeks |
| **Price** | ✅ R$ 497-1.997/month | ❌ R$ 8k-15k/month |
| **Conversational AI** | ✅ Integrated WhatsApp | ❌ Not available |
| **Customization** | ✅ Full white-label | ❌ Logo only |

---

## 📊 **Project Status**

### ✅ **Production-Ready Components**

```
┌────────────────────────────────────────────────────────────────┐
│                    FACILIAUTO - CURRENT STATUS                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  🔧 Backend API:           ✅ Production-Ready                  │
│     • FastAPI + Python 3.11                                    │
│     • 23+ test files                                           │
│     • Unified recommendation engine                            │
│     • Docker + CI/CD configured                                │
│                                                                │
│  🎨 Frontend Web:          ✅ Production-Ready                  │
│     • React 18 + TypeScript                                    │
│     • Chakra UI + Framer Motion                                │
│     • 4 main pages implemented                                 │
│     • 46+ reusable components                                  │
│     • Vitest + Cypress E2E tests                               │
│                                                                │
│  💬 WhatsApp Chatbot:      ✅ Production-Ready                  │
│     • LangGraph for conversational flow                        │
│     • Meta WhatsApp Business API integration                   │
│     • Intelligent lead qualification                           │
│     • Audio transcription with Whisper                         │
│     • Redis for sessions + PostgreSQL                          │
│                                                                │
│  🕷️ Scrapers:              ✅ Working                           │
│     • Automatic inventory extraction                           │
│     • Support for multiple dealerships                         │
│     • Data validation and transformation                       │
│                                                                │
│  🤖 Agents Framework:      ✅ Complete                          │
│     • 12 specialized agents                                    │
│     • CLI for orchestration                                    │
│     • Scalable templates                                       │
│                                                                │
│  📚 Documentation:         ✅ Extensive                         │
│     • 134+ documentation files                                 │
│     • Business, Technical, Implementation                      │
│     • Guides and Troubleshooting                               │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ **Architecture**

```
                     ┌─────────────────────┐
                     │    End Customer     │
                     │    (WhatsApp)       │
                     └─────────┬───────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                         FACILIAUTO                                │
├───────────────────┬───────────────────┬──────────────────────────┤
│                   │                   │                          │
│  ┌─────────────┐  │  ┌─────────────┐  │  ┌─────────────────────┐ │
│  │  Frontend   │  │  │   Backend   │  │  │  WhatsApp Chatbot   │ │
│  │   React +   │  │  │   FastAPI   │  │  │     LangGraph +     │ │
│  │ TypeScript  │  │  │   Python    │  │  │    Pydantic AI      │ │
│  └─────────────┘  │  └─────────────┘  │  └─────────────────────┘ │
│        │          │        │          │           │              │
│        └──────────┼────────┴──────────┼───────────┘              │
│                   │                   │                          │
│                   ▼                   │                          │
│         ┌─────────────────┐           │                          │
│         │   Unified       │           │                          │
│         │ Recommendation  │           │                          │
│         │    Engine       │           │                          │
│         └─────────────────┘           │                          │
│                   │                   │                          │
│                   ▼                   │                          │
│       ┌───────────────────┐           │                          │
│       │  Data Layer       │           │                          │
│       │ Redis │ PostgreSQL│           │                          │
│       │ JSON  │ DuckDB    │           │                          │
│       └───────────────────┘           │                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🧩 **Components**

### **Backend (REST API Python + FastAPI)**
📁 `platform/backend/`

| Feature | Description | Status |
|----------------|-----------|--------|
| **REST API** | 13+ documented endpoints (OpenAPI/Swagger) | ✅ |
| **Recommendation Engine** | Matching algorithm with multi-criteria scoring | ✅ |
| **TCO Calculator** | Total Cost of Ownership calculation | ✅ |
| **Car Classifier** | Automatic vehicle classification | ✅ |
| **Financial Health** | Financial capacity validation | ✅ |
| **Feedback Engine** | Iterative feedback system | ✅ |
| **Multi-Tenant** | Support for multiple dealerships | ✅ |
| **Docker/CI-CD** | Containerization and automated deploy | ✅ |
| **Monitoring** | Prometheus + Grafana | ✅ |

**Implemented Services:**
- `unified_recommendation_engine.py` - Main recommendation engine
- `tco_calculator.py` - Total cost calculator
- `car_classifier.py` - Vehicle classifier
- `feedback_engine.py` - Feedback system
- `fuel_price_service.py` - Fuel price service

---

### **Frontend (React + TypeScript + Chakra UI)**
📁 `platform/frontend/`

| Page | Feature | Status |
|--------|----------------|--------|
| **HomePage** | Landing page with CTA, testimonials, badges | ✅ |
| **QuestionnairePage** | Interactive 4-step questionnaire | ✅ |
| **ResultsPage** | Recommendations display with gallery | ✅ |
| **DealershipInventoryPage** | Dealership inventory page | ✅ |

**Key Components (46+):**
- `common/` - Header, Footer, LoadingSpinner, ErrorBoundary, etc.
- `questionnaire/` - Steps, ProgressBar, BrandSelector, etc.
- `results/` - CarCard, Comparison, Financing, Gallery, etc.
- `CarHighlights.tsx` - Vehicle highlights
- `Testimonials.tsx` - Customer testimonials
- `TrustBadges.tsx` - Trust badges
- `PartnerLogos.tsx` - Partner logos

**Technologies:**
- React 18 + TypeScript
- Chakra UI + Framer Motion (animations)
- Zustand (state management)
- React Query (data fetching)
- Vitest + Cypress (tests)

---

### **WhatsApp Chatbot (LangGraph + Pydantic AI)**
📁 `platform/chatbot/`

| Feature | Description | Status |
|---------|-----------|--------|
| **Meta API Integration** | Official WhatsApp Business API | ✅ |
| **LangGraph Flow** | Conversational flow with states | ✅ |
| **NLP in PT-BR** | Natural language processing | ✅ |
| **Audio Transcription** | Whisper + OpenAI for voice messages | ✅ |
| **Lead Qualification** | Intelligent data collection | ✅ |
| **Vehicle Search** | Integration with recommendation engine | ✅ |
| **Guardrails** | Protection against inappropriate responses | ✅ |
| **Session Management** | Redis for session persistence | ✅ |
| **Handoff to Human** | Transfer to human agent | ✅ |

**Conversational Flow:**
```
GREETING → VEHICLE_SEARCH → QUALIFICATION → FINANCING → HANDOFF
    ↓           ↓               ↓              ↓
  Name       Model/Year      Budget      Financing
  Greeting   Preferences     Usage       TradeIn
```

**Implemented Services:**
- `conversation_engine.py` - Main engine with LangGraph
- `nlp_service.py` - Natural language processing
- `backend_client.py` - Client for backend API
- `whatsapp_client.py` - Meta WhatsApp API client
- `session_manager.py` - Session manager
- `guardrails.py` - Guardrails system

---

### **Scrapers (Data Extraction)**
📁 `platform/scrapers/`

| Scraper | Dealership | Status |
|---------|----------------|--------|
| `robustcar_scraper.py` | RobustCar | ✅ |
| `rpmultimarcas_scraper.py` | RP Multimarcas | ✅ |

**Features:**
- Automatic inventory extraction
- Data validation
- Transformation and normalization
- JSON export

---

### **Framework of 12 Specialized Agents**
📁 `agents/`

| Category | Agents |
|-----------|---------|
| **Core** | AI Engineer, Tech Lead, UX Specialist, Product Manager |
| **Business** | Business Analyst, Marketing Strategist, Sales Coach, Financial Advisor |
| **Operations** | Operations Manager, System Architecture, Data Analyst, Content Creator |

**CLI Tool:**
```bash
python agent-cli.py list      # List agents
python agent-cli.py validate  # Validate quality
python agent-cli.py create    # Create new agents
```

---

## 🚀 **How to Run**

### **Prerequisites**

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- Redis (for chatbot)
- PostgreSQL (for chatbot)

### **1. Backend**

```bash
cd platform/backend

# Install dependencies
pip install -r requirements.txt

# Run API
python api/main.py

# Run tests
pytest tests/ -v --cov
```

**Available endpoints:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### **2. Frontend**

```bash
cd platform/frontend

# Install dependencies
npm install

# Run in development
npm run dev

# Run tests
npm test

# Run E2E tests
npm run e2e
```

**Access:** http://localhost:5173

### **3. Chatbot**

```bash
cd platform/chatbot

# Copy environment variables
cp .env.example .env

# Configure credentials (edit .env)

# Run with Docker
docker-compose up -d

# Or locally with Poetry
poetry install
poetry run uvicorn src.main:app --reload --port 8001
```

### **4. Full Execution (Windows)**

```bash
# In project root
start-faciliauto.bat
```

### **5. Full Execution (Linux/Mac)**

```bash
chmod +x start-faciliauto.sh
./start-faciliauto.sh
```

---

## 🛠️ **Tech Stack**

### **Backend**
| Technology | Version | Usage |
|------------|--------|-----|
| Python | 3.11+ | Main language |
| FastAPI | 0.109+ | API Framework |
| Pydantic | 2.5+ | Data validation |
| pytest | 7.4+ | Tests |
| Docker | - | Containerization |
| Prometheus | - | Metrics |
| Grafana | - | Dashboards |

### **Frontend**
| Technology | Version | Usage |
|------------|--------|-----|
| React | 18.2 | UI Library |
| TypeScript | 5.3 | Type safety |
| Chakra UI | 2.8 | Design System |
| Framer Motion | 10.16 | Animations |
| Zustand | 4.4 | State Management |
| React Query | 5.12 | Data Fetching |
| Vite | 5.0 | Build Tool |
| Vitest | 1.0 | Unit Tests |
| Cypress | 13.6 | E2E Tests |

### **Chatbot**
| Technology | Version | Usage |
|------------|--------|-----|
| LangGraph | 0.0.20 | Conversational flow |
| LangChain | 0.1+ | LLM Framework |
| Pydantic AI | 0.0.13 | AI Validation |
| Redis | 5.0 | Cache/Sessions |
| PostgreSQL | - | Persistence |
| DuckDB | 0.9 | Analytics |
| Celery | 5.3 | Task Queue |
| spaCy | 3.7 | NLP |
| Whisper | - | Audio transcription |

---

## 📚 **Documentation**

### **Documentation Structure**

```
docs/
├── business/           # Strategy and business (16 docs)
├── technical/          # Technical architecture (18 docs)
├── implementation/     # Implementation guides (15 docs)
├── guides/             # Practical tutorials (19 docs)
├── reports/            # Reports (16 docs)
├── troubleshooting/    # Troubleshooting (32 docs)
├── deployment/         # Deploy and infrastructure (4 docs)
└── ml/                 # Machine Learning (2 docs)
```

### **Main Documents**

| Document | Description |
|-----------|-----------|
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guide |
| [FOR-RECRUITERS.md](FOR-RECRUITERS.md) | Technical evaluation of the project |
| [platform/README.md](platform/README.md) | Platform documentation |
| [platform/chatbot/README.md](platform/chatbot/README.md) | Chatbot documentation |
| [agents/README.md](agents/README.md) | Agents framework |

---

## 📁 **Project Structure**

```
FacilIAuto/
├── 📁 platform/                 # MAIN PLATFORM
│   ├── 📁 backend/             # REST API (Python + FastAPI)
│   │   ├── api/               # API Endpoints
│   │   ├── services/          # Business logic (12 services)
│   │   ├── models/            # Pydantic models
│   │   ├── tests/             # Tests (23 files)
│   │   └── data/              # Dealership data
│   │
│   ├── 📁 frontend/           # Web App (React + TypeScript)
│   │   ├── src/
│   │   │   ├── components/   # 46+ components
│   │   │   ├── pages/        # 4 main pages
│   │   │   ├── services/     # API clients
│   │   │   ├── store/        # Zustand stores
│   │   │   └── hooks/        # Custom hooks
│   │   └── cypress/          # E2E Tests
│   │
│   ├── 📁 chatbot/            # WhatsApp Bot (LangGraph)
│   │   ├── src/
│   │   │   ├── api/          # Webhooks
│   │   │   ├── services/     # 8 main services
│   │   │   ├── tasks/        # Celery tasks
│   │   │   └── utils/        # Utilities
│   │   └── tests/            # Unit and E2E tests
│   │
│   └── 📁 scrapers/           # Data extraction
│       ├── scraper/          # Scraper modules
│       └── tests/            # Tests
│
├── 📁 agents/                   # Framework of 12 AI agents
│   ├── ai-engineer/
│   ├── tech-lead/
│   ├── ux-especialist/
│   ├── product-manager/
│   ├── business-analyst/
│   ├── marketing-strategist/
│   ├── sales-coach/
│   ├── financial-advisor/
│   ├── operations-manager/
│   ├── system-architecture/
│   ├── data-analyst/
│   ├── content-creator/
│   └── agent-cli.py          # CLI tool
│
├── 📁 docs/                     # Extensive documentation (134+ files)
│   ├── business/
│   ├── technical/
│   ├── implementation/
│   ├── guides/
│   └── troubleshooting/
│
├── 📁 examples/                 # Reference prototypes
│   ├── CarRecommendationSite/
│   └── RobustCar/
│
├── 📄 README.md                 # This file
├── 📄 CONTRIBUTING.md           # Contribution guide
├── 📄 FOR-RECRUITERS.md         # Technical evaluation
├── 📄 LICENSE                   # MIT License
├── 🔧 start-faciliauto.bat      # Windows Script
├── 🔧 start-faciliauto.sh       # Linux/Mac Script
└── 🔧 stop-faciliauto.sh        # Stop services script
```

---

## 🤝 **Contributing**

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### **Development Workflow**

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### **Code Standards**

- **Backend:** Black + Flake8 + MyPy
- **Frontend:** ESLint + Prettier
- **Commits:** Conventional Commits

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 **Contact**

For questions or commercial partnerships:

- **Demo:** Schedule a 15-minute demonstration
- **Support:** Consult the [troubleshooting documentation](docs/troubleshooting/)
- **Contribution:** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

<div align="center">

**🚀 FacilIAuto - Transforming the car buying experience in Brazil**

*Developed with ❤️ using XP methodology + TDD*

</div>
