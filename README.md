# 🚗 **FacilIAuto - Plataforma Inteligente de Vendas Automotivas**

> 🇺🇸 [**Read this in English**](README_EN.md)

> ⚠️ **AVISO DE LICENÇA PROPRIETÁRIA:** Este repositório é disponibilizado exclusivamente para fins de avaliação técnica por recrutadores e potenciais empregadores. Uso comercial, cópia ou redistribuição são estritamente proibidos. Veja [LICENSE](LICENSE) para detalhes.

<div align="center">

![FacilIAuto Logo](platform/frontend/src/faciliauto-logo.png)

**Plataforma SaaS B2B de recomendação automotiva com IA conversacional via WhatsApp**

[![Backend Status](https://img.shields.io/badge/Backend-Production--Ready-success?style=for-the-badge)]()
[![Frontend Status](https://img.shields.io/badge/Frontend-Production--Ready-success?style=for-the-badge)]()
[![Chatbot Status](https://img.shields.io/badge/Chatbot-Production--Ready-success?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](LICENSE)

</div>

---

## 📋 **Índice**

- [Visão Geral](#-visão-geral)
- [Status do Projeto](#-status-do-projeto)
- [Arquitetura](#-arquitetura)
- [Componentes](#-componentes)
  - [Backend](#backend-api-rest-python--fastapi)
  - [Frontend](#frontend-react--typescript--chakra-ui)
  - [Chatbot WhatsApp](#chatbot-whatsapp-langgraph--pydantic-ai)
  - [Scrapers](#scrapers-extração-de-dados)
  - [Agentes IA](#framework-de-12-agentes-especializados)
- [Como Executar](#-como-executar)
- [Stack Tecnológico](#-stack-tecnológico)
- [Documentação](#-documentação)
- [Contribuindo](#-contribuindo)

---

## 🎯 **Visão Geral**

O **FacilIAuto** é uma solução completa para concessionárias e lojas de veículos que integra:

1. **🌐 Website de Recomendação** - Interface web mobile-first para captura de leads
2. **🤖 Chatbot WhatsApp** - Assistente inteligente com IA conversacional
3. **📊 Engine de Recomendação** - Algoritmo de matching com scoring inteligente
4. **📱 Painel Administrativo** - Gestão de estoque e leads

### ✨ **Diferenciais**

| Aspecto | **FacilIAuto** | Concorrentes |
|---------|----------------|--------------|
| **UX Mobile** | ✅ Mobile-first nativo | ❌ Desktop adaptado |
| **Setup** | ✅ 30 minutos | ❌ 2-4 semanas |
| **Preço** | ✅ R$ 497-1.997/mês | ❌ R$ 8k-15k/mês |
| **IA Conversacional** | ✅ WhatsApp integrado | ❌ Não disponível |
| **Customização** | ✅ White-label completo | ❌ Logo apenas |

---

## 📊 **Status do Projeto**

### ✅ **Componentes Prontos para Produção**

```
┌────────────────────────────────────────────────────────────────┐
│                    FACILIAUTO - STATUS ATUAL                   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  🔧 Backend API:           ✅ Production-Ready                  │
│     • FastAPI + Python 3.11                                    │
│     • 23+ arquivos de teste                                    │
│     • Engine de recomendação unificado                         │
│     • Docker + CI/CD configurado                               │
│                                                                │
│  🎨 Frontend Web:          ✅ Production-Ready                  │
│     • React 18 + TypeScript                                    │
│     • Chakra UI + Framer Motion                                │
│     • 4 páginas principais implementadas                       │
│     • 46+ componentes reutilizáveis                            │
│     • Testes Vitest + Cypress E2E                              │
│                                                                │
│  💬 Chatbot WhatsApp:      ✅ Production-Ready                  │
│     • LangGraph para fluxo conversacional                      │
│     • Integração Meta WhatsApp Business API                    │
│     • Qualificação inteligente de leads                        │
│     • Transcrição de áudio com Whisper                         │
│     • Redis para sessões + PostgreSQL                          │
│                                                                │
│  🕷️ Scrapers:              ✅ Funcionando                       │
│     • Extração automática de estoque                           │
│     • Suporte a múltiplas concessionárias                      │
│     • Validação e transformação de dados                       │
│                                                                │
│  🤖 Framework de Agentes:  ✅ Completo                          │
│     • 12 agentes especializados                                │
│     • CLI para orquestração                                    │
│     • Templates escaláveis                                     │
│                                                                │
│  📚 Documentação:          ✅ Extensa                           │
│     • 134+ arquivos de documentação                            │
│     • Business, Technical, Implementation                      │
│     • Guias e Troubleshooting                                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ **Arquitetura**

```
                     ┌─────────────────────┐
                     │   Cliente Final     │
                     │    (WhatsApp)       │
                     └─────────┬───────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                         FACILIAUTO                                │
├───────────────────┬───────────────────┬──────────────────────────┤
│                   │                   │                          │
│  ┌─────────────┐  │  ┌─────────────┐  │  ┌─────────────────────┐ │
│  │  Frontend   │  │  │   Backend   │  │  │  Chatbot WhatsApp   │ │
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

## 🧩 **Componentes**

### **Backend (API REST Python + FastAPI)**
📁 `platform/backend/`

| Funcionalidade | Descrição | Status |
|----------------|-----------|--------|
| **API REST** | 13+ endpoints documentados (OpenAPI/Swagger) | ✅ |
| **Recommendation Engine** | Algoritmo de matching com scoring multi-critério | ✅ |
| **TCO Calculator** | Cálculo de Custo Total de Propriedade | ✅ |
| **Car Classifier** | Classificação automática de veículos | ✅ |
| **Financial Health** | Validação de capacidade financeira | ✅ |
| **Feedback Engine** | Sistema de feedback iterativo | ✅ |
| **Multi-Tenant** | Suporte a múltiplas concessionárias | ✅ |
| **Docker/CI-CD** | Containerização e deploy automatizado | ✅ |
| **Monitoring** | Prometheus + Grafana | ✅ |

**Serviços Implementados:**
- `unified_recommendation_engine.py` - Engine principal de recomendação
- `tco_calculator.py` - Calculadora de custo total
- `car_classifier.py` - Classificador de veículos
- `feedback_engine.py` - Sistema de feedback
- `fuel_price_service.py` - Serviço de preços de combustível

---

### **Frontend (React + TypeScript + Chakra UI)**
📁 `platform/frontend/`

| Página | Funcionalidade | Status |
|--------|----------------|--------|
| **HomePage** | Landing page com CTA, depoimentos, badges | ✅ |
| **QuestionnairePage** | Questionário interativo de 4 etapas | ✅ |
| **ResultsPage** | Exibição de recomendações com galeria | ✅ |
| **DealershipInventoryPage** | Página de estoque da concessionária | ✅ |

**Componentes Principais (46+):**
- `common/` - Header, Footer, LoadingSpinner, ErrorBoundary, etc.
- `questionnaire/` - Steps, ProgressBar, BrandSelector, etc.
- `results/` - CarCard, Comparison, Financing, Gallery, etc.
- `CarHighlights.tsx` - Destaques de veículos
- `Testimonials.tsx` - Depoimentos de clientes
- `TrustBadges.tsx` - Selos de confiança
- `PartnerLogos.tsx` - Logos de parceiros

**Tecnologias:**
- React 18 + TypeScript
- Chakra UI + Framer Motion (animações)
- Zustand (state management)
- React Query (data fetching)
- Vitest + Cypress (testes)

---

### **Chatbot WhatsApp (LangGraph + Pydantic AI)**
📁 `platform/chatbot/`

| Feature | Descrição | Status |
|---------|-----------|--------|
| **Integração Meta API** | WhatsApp Business API oficial | ✅ |
| **LangGraph Flow** | Fluxo conversacional com estados | ✅ |
| **NLP em PT-BR** | Processamento de linguagem natural | ✅ |
| **Transcrição de Áudio** | Whisper + OpenAI para mensagens de voz | ✅ |
| **Qualificação de Leads** | Coleta inteligente de dados | ✅ |
| **Busca de Veículos** | Integração com engine de recomendação | ✅ |
| **Guardrails** | Proteções contra respostas inadequadas | ✅ |
| **Session Management** | Redis para persistência de sessões | ✅ |
| **Handoff to Human** | Transferência para atendente humano | ✅ |

**Fluxo Conversacional:**
```
GREETING → VEHICLE_SEARCH → QUALIFICATION → FINANCING → HANDOFF
    ↓           ↓               ↓              ↓
  Nome      Modelo/Ano     Orçamento      Financiamento
  Saudação   Preferências   UsoPrincipal   TradeIn
```

**Serviços Implementados:**
- `conversation_engine.py` - Engine principal com LangGraph
- `nlp_service.py` - Processamento de linguagem natural
- `backend_client.py` - Cliente para API do backend
- `whatsapp_client.py` - Cliente Meta WhatsApp API
- `session_manager.py` - Gerenciador de sessões
- `guardrails.py` - Sistema de guardrails

---

### **Scrapers (Extração de Dados)**
📁 `platform/scrapers/`

| Scraper | Concessionária | Status |
|---------|----------------|--------|
| `robustcar_scraper.py` | RobustCar | ✅ |
| `rpmultimarcas_scraper.py` | RP Multimarcas | ✅ |

**Funcionalidades:**
- Extração automática de estoque
- Validação de dados
- Transformação e normalização
- Exportação JSON

---

### **Framework de 12 Agentes Especializados**
📁 `agents/`

| Categoria | Agentes |
|-----------|---------|
| **Core** | AI Engineer, Tech Lead, UX Specialist, Product Manager |
| **Business** | Business Analyst, Marketing Strategist, Sales Coach, Financial Advisor |
| **Operations** | Operations Manager, System Architecture, Data Analyst, Content Creator |

**CLI Tool:**
```bash
python agent-cli.py list      # Listar agentes
python agent-cli.py validate  # Validar qualidade
python agent-cli.py create    # Criar novos agentes
```

---

## 🚀 **Como Executar**

### **Pré-requisitos**

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (opcional)
- Redis (para chatbot)
- PostgreSQL (para chatbot)

### **1. Backend**

```bash
cd platform/backend

# Instalar dependências
pip install -r requirements.txt

# Rodar API
python api/main.py

# Rodar testes
pytest tests/ -v --cov
```

**Endpoints disponíveis:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### **2. Frontend**

```bash
cd platform/frontend

# Instalar dependências
npm install

# Rodar em desenvolvimento
npm run dev

# Rodar testes
npm test

# Rodar testes E2E
npm run e2e
```

**Acesso:** http://localhost:5173

### **3. Chatbot**

```bash
cd platform/chatbot

# Copiar variáveis de ambiente
cp .env.example .env

# Configurar credenciais (editar .env)

# Rodar com Docker
docker-compose up -d

# Ou localmente com Poetry
poetry install
poetry run uvicorn src.main:app --reload --port 8001
```

### **4. Execução Completa (Windows)**

```bash
# Na raiz do projeto
start-faciliauto.bat
```

### **5. Execução Completa (Linux/Mac)**

```bash
chmod +x start-faciliauto.sh
./start-faciliauto.sh
```

---

## 🛠️ **Stack Tecnológico**

### **Backend**
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.11+ | Linguagem principal |
| FastAPI | 0.109+ | Framework API |
| Pydantic | 2.5+ | Validação de dados |
| pytest | 7.4+ | Testes |
| Docker | - | Containerização |
| Prometheus | - | Métricas |
| Grafana | - | Dashboards |

### **Frontend**
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| React | 18.2 | UI Library |
| TypeScript | 5.3 | Type safety |
| Chakra UI | 2.8 | Design System |
| Framer Motion | 10.16 | Animações |
| Zustand | 4.4 | State Management |
| React Query | 5.12 | Data Fetching |
| Vite | 5.0 | Build Tool |
| Vitest | 1.0 | Unit Tests |
| Cypress | 13.6 | E2E Tests |

### **Chatbot**
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| LangGraph | 0.0.20 | Fluxo conversacional |
| LangChain | 0.1+ | Framework LLM |
| Pydantic AI | 0.0.13 | Validação IA |
| Redis | 5.0 | Cache/Sessions |
| PostgreSQL | - | Persistência |
| DuckDB | 0.9 | Analytics |
| Celery | 5.3 | Task Queue |
| spaCy | 3.7 | NLP |
| Whisper | - | Transcrição de áudio |

---

## 📚 **Documentação**

### **Estrutura de Documentação**

```
docs/
├── business/           # Estratégia e negócios (16 docs)
├── technical/          # Arquitetura técnica (18 docs)
├── implementation/     # Guias de implementação (15 docs)
├── guides/             # Tutoriais práticos (19 docs)
├── reports/            # Relatórios (16 docs)
├── troubleshooting/    # Solução de problemas (32 docs)
├── deployment/         # Deploy e infraestrutura (4 docs)
└── ml/                 # Machine Learning (2 docs)
```

### **Documentos Principais**

| Documento | Descrição |
|-----------|-----------|
| [CONTRIBUTING.md](CONTRIBUTING.md) | Guia de contribuição |
| [FOR-RECRUITERS.md](FOR-RECRUITERS.md) | Avaliação técnica do projeto |
| [platform/README.md](platform/README.md) | Documentação da plataforma |
| [platform/chatbot/README.md](platform/chatbot/README.md) | Documentação do chatbot |
| [agents/README.md](agents/README.md) | Framework de agentes |

---

## 📁 **Estrutura do Projeto**

```
FacilIAuto/
├── 📁 platform/                 # PLATAFORMA PRINCIPAL
│   ├── 📁 backend/             # API REST (Python + FastAPI)
│   │   ├── api/               # Endpoints da API
│   │   ├── services/          # Lógica de negócio (12 serviços)
│   │   ├── models/            # Modelos Pydantic
│   │   ├── tests/             # Testes (23 arquivos)
│   │   └── data/              # Dados das concessionárias
│   │
│   ├── 📁 frontend/           # Web App (React + TypeScript)
│   │   ├── src/
│   │   │   ├── components/   # 46+ componentes
│   │   │   ├── pages/        # 4 páginas principais
│   │   │   ├── services/     # API clients
│   │   │   ├── store/        # Zustand stores
│   │   │   └── hooks/        # Custom hooks
│   │   └── cypress/          # Testes E2E
│   │
│   ├── 📁 chatbot/            # WhatsApp Bot (LangGraph)
│   │   ├── src/
│   │   │   ├── api/          # Webhooks
│   │   │   ├── services/     # 8 serviços principais
│   │   │   ├── tasks/        # Celery tasks
│   │   │   └── utils/        # Utilitários
│   │   └── tests/            # Testes unitários e E2E
│   │
│   └── 📁 scrapers/           # Extração de dados
│       ├── scraper/          # Módulos de scraping
│       └── tests/            # Testes
│
├── 📁 agents/                   # Framework de 12 agentes IA
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
├── 📁 docs/                     # Documentação extensa (134+ arquivos)
│   ├── business/
│   ├── technical/
│   ├── implementation/
│   ├── guides/
│   └── troubleshooting/
│
├── 📁 examples/                 # Protótipos de referência
│   ├── CarRecommendationSite/
│   └── RobustCar/
│
├── 📄 README.md                 # Este arquivo
├── 📄 CONTRIBUTING.md           # Guia de contribuição
├── 📄 FOR-RECRUITERS.md         # Avaliação técnica
├── 📄 LICENSE                   # MIT License
├── 🔧 start-faciliauto.bat      # Script Windows
├── 🔧 start-faciliauto.sh       # Script Linux/Mac
└── 🔧 stop-faciliauto.sh        # Parar serviços
```

---

## 🤝 **Contribuindo**

Contribuições são bem-vindas! Por favor, leia o [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre nosso código de conduta e processo de submissão de pull requests.

### **Workflow de Desenvolvimento**

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### **Padrões de Código**

- **Backend:** Black + Flake8 + MyPy
- **Frontend:** ESLint + Prettier
- **Commits:** Conventional Commits

---

## 📄 **Licença**

> ⚠️ **LICENÇA PROPRIETÁRIA - USO RESTRITO**

Este repositório é disponibilizado **EXCLUSIVAMENTE** para fins de avaliação profissional e demonstração de competências técnicas para potenciais empregadores e recrutadores.

**Usos Permitidos:**
- ✅ Visualização e análise do código para avaliação técnica
- ✅ Discussão em contexto de entrevistas de emprego
- ✅ Referência em processos seletivos

**Usos Proibidos:**
- ❌ Cópia, reprodução ou distribuição de qualquer parte do código
- ❌ Uso comercial ou incorporação em outros projetos
- ❌ Criação de trabalhos derivados

Veja o arquivo [LICENSE](LICENSE) para detalhes completos.

---

## 📞 **Contato**

Para dúvidas ou parcerias comerciais:

- **Demo:** Agende uma demonstração de 15 minutos
- **Suporte:** Consulte a [documentação de troubleshooting](docs/troubleshooting/)
- **Contribuição:** Veja [CONTRIBUTING.md](CONTRIBUTING.md)

---

<div align="center">

**🚀 FacilIAuto - Transformando a experiência de compra de veículos no Brasil**

*Desenvolvido com ❤️ usando metodologia XP + TDD*

</div>
