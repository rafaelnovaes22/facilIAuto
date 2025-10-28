# FacilIAuto - Estrutura do Projeto

## 📁 Estrutura Profissional da Raiz

A raiz do projeto foi organizada para apresentação profissional a recrutadores técnicos e stakeholders.

### Arquivos Essenciais na Raiz

```
FacilIAuto/
├── README.md                    # Documentação principal do projeto
├── FOR-RECRUITERS.md            # Avaliação técnica para recrutadores
├── CONTRIBUTING.md              # Guia de contribuição
├── LICENSE                      # MIT License
├── .gitignore                   # Configuração Git
│
├── start-faciliauto.bat         # Iniciar backend + frontend (Windows)
├── start-faciliauto.sh          # Iniciar backend + frontend (Linux/Mac)
├── start-faciliauto-simple.bat  # Iniciar simplificado (Windows)
├── stop-faciliauto.sh           # Parar serviços (Linux/Mac)
│
├── platform/                    # Código principal da plataforma
├── agents/                      # Framework de 12 agentes especializados
├── docs/                        # Documentação organizada
├── examples/                    # Protótipos e exemplos de referência
│
├── .archive/                    # Arquivos históricos/temporários (gitignored)
├── .git/                        # Controle de versão
├── .kiro/                       # Configuração Kiro IDE
└── .vscode/                     # Configuração VS Code
```

## 🎯 Princípios de Organização

### 1. Minimalismo na Raiz
- **Apenas 9 arquivos** visíveis na raiz
- Fácil navegação para recrutadores
- Estrutura clara e profissional

### 2. Documentação Acessível
- **README.md**: Visão geral completa do projeto
- **FOR-RECRUITERS.md**: Avaliação técnica detalhada (97/100 backend)
- **CONTRIBUTING.md**: Guia para contribuidores

### 3. Scripts de Execução Rápida
- Scripts na raiz para iniciar o sistema rapidamente
- Suporte para Windows, Linux e Mac
- Nomes descritivos e auto-explicativos

### 4. Separação de Concerns
- **platform/**: Código de produção (backend + frontend)
- **agents/**: Framework de agentes especializados
- **docs/**: Documentação categorizada
- **examples/**: Protótipos históricos
- **.archive/**: Arquivos temporários e históricos

## 📚 Estrutura de Documentação

A pasta `docs/` está organizada por categoria:

```
docs/
├── business/              # Estratégia de negócio
│   ├── PERFIS-USO-DETALHADOS.md
│   ├── CARROS-TRANSPORTE-APP.md
│   └── ...
│
├── technical/             # Arquitetura técnica
│   ├── ARQUITETURA-MULTI-TENANT.md
│   └── ...
│
├── implementation/        # Guias de implementação
│   ├── XP-TDD-GUIDE.md
│   └── ...
│
├── guides/                # Guias práticos
│   ├── LINGUAGEM-SIMPLIFICADA.md
│   └── ...
│
└── PROJECT-STRUCTURE.md   # Este arquivo
```

## 🗂️ Pasta .archive

Contém arquivos históricos e temporários que não são relevantes para avaliação:

- Relatórios de status antigos
- Planos de ação executados
- Documentos de validação temporários
- Scripts de organização
- Arquivos de teste/debug

**Nota**: A pasta `.archive/` está no `.gitignore` e não é versionada.

## 🎨 Estrutura da Plataforma

### Backend (`platform/backend/`)
```
backend/
├── api/                   # FastAPI REST API
├── models/                # Modelos Pydantic
├── services/              # Lógica de negócio
├── data/                  # Dados (JSON)
├── tests/                 # 60+ testes (87% coverage)
├── scripts/               # Scripts utilitários
├── utils/                 # Utilitários
├── monitoring/            # Prometheus/Grafana
└── README.md
```

### Frontend (`platform/frontend/`)
```
frontend/
├── src/
│   ├── components/        # Componentes React
│   ├── pages/             # Páginas principais
│   ├── services/          # API client
│   ├── store/             # State management (Zustand)
│   ├── hooks/             # Custom hooks
│   ├── types/             # TypeScript types
│   └── theme/             # Chakra UI theme
├── cypress/               # Testes E2E
├── tests/                 # Testes unitários
└── README.md
```

## 🤖 Framework de Agentes

12 agentes especializados fornecem contexto e expertise:

```
agents/
├── ai-engineer/           # IA e ML
├── tech-lead/             # Liderança técnica
├── ux-especialist/        # UX/UI
├── system-architecture/   # Arquitetura de sistemas
├── business-analyst/      # Análise de negócios
├── product-manager/       # Gestão de produto
├── marketing-strategist/  # Marketing e growth
├── financial-advisor/     # Estratégia financeira
├── sales-coach/           # Otimização de vendas
├── operations-manager/    # Operações e processos
├── data-analyst/          # Análise de dados
├── content-creator/       # Conteúdo e storytelling
├── agent-cli.py           # CLI tool
├── orchestrator.py        # Orquestração
└── README.md
```

## 📊 Exemplos e Protótipos

```
examples/
├── CarRecommendationSite/ # Exemplo completo XP/TDD/E2E
├── RobustCar/             # POC single-tenant
└── README.md
```

## ✅ Checklist de Organização

Para manter a estrutura profissional:

- [ ] Raiz com máximo 10 arquivos visíveis
- [ ] README.md atualizado e completo
- [ ] FOR-RECRUITERS.md com avaliação honesta
- [ ] Scripts de execução funcionais
- [ ] Documentação categorizada em `docs/`
- [ ] Arquivos temporários em `.archive/`
- [ ] .gitignore configurado corretamente
- [ ] Estrutura clara e navegável

## 🔄 Manutenção

### Quando adicionar novos arquivos na raiz:
1. Pergunte: "Este arquivo é essencial para entender o projeto?"
2. Se não, mova para `docs/` ou `.archive/`
3. Mantenha a raiz limpa e profissional

### Quando criar nova documentação:
1. Categorize em `docs/business/`, `docs/technical/`, etc.
2. Adicione referência no README principal se relevante
3. Use nomes descritivos e em CAPS para documentos importantes

### Quando arquivar:
1. Mova para `.archive/cleanup_YYYYMMDD_HHMMSS/`
2. Mantenha organizado por data
3. Não versione no Git (já está no .gitignore)

## 🎯 Objetivo

Apresentar um projeto **profissional, organizado e fácil de avaliar** para:
- Recrutadores técnicos
- Tech leads
- Potenciais investidores
- Colaboradores futuros

**Primeira impressão importa. Uma raiz limpa demonstra profissionalismo.**
