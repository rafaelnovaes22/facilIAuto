# 🎨 Frontend FacilIAuto

Frontend React + TypeScript desenvolvido com **metodologia XP** e **desenvolvimento colaborativo multi-agentes**.

---

## 🚀 **Quick Start**

### **1. Instalar Dependências**
```bash
npm install
```

### **2. Rodar Desenvolvimento**
```bash
npm run dev
```

Abrir http://localhost:3000

### **3. Build para Produção**
```bash
npm run build
npm run preview
```

---

## 📦 **Stack Tecnológico**

### **Core**
- ⚛️ **React 18** - UI library
- 📘 **TypeScript** - Type safety
- ⚡ **Vite** - Build tool
- 🛣️ **React Router** - Navegação

### **UI/UX**
- 🎨 **Chakra UI** - Component library
- 🎭 **Framer Motion** - Animações (integrado ao Chakra)
- 🎯 **React Icons** - Ícones

### **Estado e Dados**
- 🔄 **React Query** - Data fetching e cache
- 📡 **Axios** - HTTP client
- 🐻 **Zustand** - State management

### **Qualidade**
- ✅ **Vitest** - Unit tests
- 🧪 **Testing Library** - Component tests
- 🌲 **Cypress** - E2E tests
- 📏 **ESLint** - Linting
- 💅 **Prettier** - Formatação

---

## 📁 **Estrutura do Projeto**

```
platform/frontend/
├── public/                    # Assets estáticos
├── src/
│   ├── components/           # Componentes reutilizáveis
│   │   ├── common/          # Botões, Cards, etc
│   │   ├── questionnaire/   # Componentes do questionário
│   │   └── results/         # Componentes de resultados
│   ├── pages/               # Páginas principais
│   │   ├── HomePage.tsx
│   │   ├── QuestionnairePage.tsx
│   │   └── ResultsPage.tsx
│   ├── services/            # API calls
│   │   └── api.ts
│   ├── hooks/               # Custom hooks
│   ├── types/               # TypeScript types
│   ├── utils/               # Utilities
│   ├── theme/               # Chakra UI theme
│   ├── App.tsx              # App principal
│   └── main.tsx             # Entry point
├── tests/                    # Testes
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md                 # Este arquivo
```

---

## 🤖 **Desenvolvimento Multi-Agentes**

Este frontend está sendo desenvolvido de forma **colaborativa** usando o framework de agentes especializados:

### **👥 Agentes Envolvidos**

| Agente | Responsabilidade | Entregas |
|--------|------------------|----------|
| 🎨 **UX Especialist** | Design, usabilidade, acessibilidade | Componentes, user flows, testes UX |
| 💻 **Tech Lead** | Arquitetura, padrões, code reviews | Estrutura, setup, quality gates |
| 🤖 **AI Engineer** | Integração API, guardrails | Service layer, error handling |
| 📊 **Product Manager** | Priorização, user stories | Backlog, acceptance criteria |
| 📈 **Data Analyst** | Analytics, métricas | Tracking events, dashboards |
| ✍️ **Content Creator** | Copywriting, microcopy | Textos de interface, ajuda |

Ver documentação completa em: [`DESENVOLVIMENTO-COLABORATIVO-AGENTES.md`](./DESENVOLVIMENTO-COLABORATIVO-AGENTES.md)

---

## 🔄 **Metodologia XP Aplicada**

### **Pair Programming**
- Design Pairs: UX + Tech Lead
- Code Pairs: Tech Lead + AI Engineer
- Validação: Product Manager + UX

### **Test-Driven Development (TDD)**
```typescript
// 1. RED: Teste falha
test('should render car name', () => {
  render(<CarCard car={mockCar} />)
  expect(screen.getByText('Fiat Cronos')).toBeInTheDocument()
})

// 2. GREEN: Implementação mínima
export const CarCard = ({ car }) => <div>{car.nome}</div>

// 3. REFACTOR: Melhorar mantendo testes verdes
export const CarCard: FC<Props> = ({ car }) => (
  <Card><Heading>{car.nome}</Heading></Card>
)
```

### **Continuous Integration**
- ✅ Tests automáticos em PRs
- ✅ Linting e type checking
- ✅ Build automático
- ✅ Deploy preview

---

## 📊 **Scripts NPM**

```bash
# Desenvolvimento
npm run dev              # Rodar servidor de desenvolvimento

# Build
npm run build            # Build para produção
npm run preview          # Preview do build

# Testes
npm test                 # Rodar testes unitários
npm run test:ui          # UI de testes (Vitest)
npm run test:coverage    # Coverage report
npm run e2e              # Testes E2E (Cypress)
npm run e2e:open         # Cypress UI

# Qualidade
npm run lint             # Rodar ESLint
npm run format           # Formatar com Prettier
```

---

## 🎨 **Design System**

### **Theme Customizado**
```typescript
// src/theme/index.ts
const colors = {
  brand: {
    500: '#0ea5e9',  // Sky blue
    // ... outros tons
  },
  secondary: {
    500: '#8b5cf6',  // Purple
    // ... outros tons
  }
}
```

### **Componentes Base**
- **Button**: CTAs com variantes solid/outline
- **Card**: Cards com hover effects
- **Input**: Inputs com validação visual
- **Select**: Selects customizados
- **Loading**: States de carregamento

### **Componentes de Negócio**
- **CarCard**: Card de carro com score
- **StepIndicator**: Indicador de progresso
- **ScoreVisual**: Visualização de compatibilidade

---

## 🧪 **Testes**

### **Unit Tests (Vitest)**
```typescript
describe('HomePage', () => {
  it('should render CTA button', () => {
    render(<HomePage />)
    const button = screen.getByText(/Começar Agora/i)
    expect(button).toBeInTheDocument()
  })
})
```

### **E2E Tests (Cypress)**
```typescript
describe('User Journey', () => {
  it('should complete full flow', () => {
    cy.visit('/')
    cy.contains('Começar Agora').click()
    cy.url().should('include', '/questionario')
    // ... resto do fluxo
  })
})
```

**Meta de Coverage:** > 80%

---

## 📏 **Padrões de Código**

### **TypeScript Strict**
- ✅ Type safety completo
- ✅ Interfaces bem definidas
- ✅ Props com types explícitos

### **ESLint + Prettier**
- ✅ Linting automático
- ✅ Formatação consistente
- ✅ Import order

### **Componentes**
```typescript
// Pattern: FC com props tipadas
import { FC } from 'react'

interface CarCardProps {
  car: Car
  score: number
  onSelect: (id: string) => void
}

export const CarCard: FC<CarCardProps> = ({ car, score, onSelect }) => {
  // ... implementação
}
```

---

## 🚦 **Status do Desenvolvimento**

### **Sprint 0: Setup Inicial** ✅ COMPLETO
- [x] Vite + TypeScript configurado
- [x] Chakra UI theme customizado
- [x] React Router
- [x] ESLint + Prettier
- [x] Estrutura de pastas

### **Sprint 1: Integração API** 🔄 EM ANDAMENTO
- [ ] Service layer (api.ts)
- [ ] React Query setup
- [ ] Types do backend
- [ ] Error handling

### **Próximos Sprints**
- Sprint 2: HomePage
- Sprint 3-4: Questionário
- Sprint 5: ResultsPage
- Sprint 6: Testes
- Sprint 7: Polish

Ver roadmap completo em: [`PLANO-FRONTEND.md`](./PLANO-FRONTEND.md)

---

## 📈 **Métricas de Qualidade**

### **Objetivos**
- ⚡ **Performance**: Lighthouse > 90
- ♿ **Acessibilidade**: WCAG 2.1 AA (100%)
- 📱 **Responsivo**: Mobile-first 100%
- ✅ **Tests**: Coverage > 80%
- 📦 **Bundle**: < 500KB gzipped

### **Atuais**
- Sprint 0: Setup completo ✅
- Arquitetura definida ✅
- Theme customizado ✅

---

## 🤝 **Contribuindo**

### **Workflow**
1. Pair programming (agendado)
2. TDD (sempre)
3. Code review (< 4h)
4. Deploy automático

### **Padrões**
- Commits semânticos
- Branches por feature
- PRs com descrição
- Tests obrigatórios

---

## 📚 **Documentação**

- **[PLANO-FRONTEND.md](./PLANO-FRONTEND.md)** - Plano completo de desenvolvimento
- **[DESENVOLVIMENTO-COLABORATIVO-AGENTES.md](./DESENVOLVIMENTO-COLABORATIVO-AGENTES.md)** - Framework de colaboração
- **[API-INTEGRATION.md](./API-INTEGRATION.md)** - Documentação da API (próximo)

---

## 🎯 **Próximos Passos**

1. **Sprint 1**: Integração com API backend
2. **Sprint 2**: Implementar HomePage completa
3. **Sprint 3-4**: Questionário multi-step
4. **Sprint 5**: ResultsPage com recomendações
5. **Sprint 6**: Testes completos
6. **Sprint 7**: Polish e otimizações

---

## 📞 **Contato**

Dúvidas sobre o frontend? Ver documentação dos agentes:
- 🎨 UX Especialist: `agents/ux-especialist/context.md`
- 💻 Tech Lead: `agents/tech-lead/context.md`
- 🤖 AI Engineer: `agents/ai-engineer/context.md`

---

**🚀 Frontend de alto nível desenvolvido com metodologia XP e colaboração multi-agentes!**

