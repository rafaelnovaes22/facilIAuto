# Design Document - FacilIAuto Complete System

## Overview

Este documento descreve o design técnico para completar os 16% restantes do projeto FacilIAuto, transformando-o de um sistema 84% completo para 100% funcional e demonstrável. O design foca em três pilares principais:

1. **Frontend Completo**: Finalizar as 3 páginas principais com componentes funcionais e responsivos
2. **Integração Validada**: Garantir comunicação robusta entre frontend e backend
3. **Qualidade Assegurada**: Implementar testes E2E e garantir cobertura adequada

### Current State Analysis

**Backend (97/100):**
- FastAPI com 10 endpoints funcionais
- 60+ testes com 87% coverage
- Arquitetura multi-tenant implementada
- 3 concessionárias, 129+ carros no banco
- Production-ready com Docker, CI/CD, Monitoring

**Frontend (40/100):**
- Estrutura básica: React + TypeScript + Vite + Chakra UI
- React Router configurado
- Zustand store implementado
- ~20 testes unitários existentes
- Componentes parcialmente implementados

**Gaps Identificados:**
- Páginas principais não 100% funcionais
- Integração frontend-backend não validada
- Testes E2E incompletos (Cypress configurado mas não implementado)
- Scripts de execução não testados

## Architecture

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  HomePage  │  │Questionnaire│  │  Results   │            │
│  └─────┬──────┘  └──────┬─────┘  └──────┬─────┘            │
│        │                 │                │                  │
│        └─────────────────┴────────────────┘                  │
│                          │                                   │
│                    React Router                              │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ React Query │  ← Cache & State
                    │   + Zustand │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ API Service │  ← axios + error handling
                    │  (api.ts)   │
                    └──────┬──────┘
                           │ HTTP/REST
┌──────────────────────────┼───────────────────────────────────┐
│                    ┌─────▼─────┐                             │
│                    │   Nginx   │  ← CORS, Rate Limit         │
│                    └─────┬─────┘                             │
│                          │                                   │
│                    ┌─────▼─────┐                             │
│                    │  FastAPI  │  ← 10 endpoints             │
│                    │  Backend  │                             │
│                    └─────┬─────┘                             │
│                          │                                   │
│              ┌───────────┴───────────┐                       │
│              │                       │                       │
│        ┌─────▼─────┐         ┌──────▼──────┐                │
│        │   Engine  │         │    Data     │                │
│        │Recommend  │         │ 3 dealers   │                │
│        │           │         │ 129+ cars   │                │
│        └───────────┘         └─────────────┘                │
│                                                              │
│                    Backend (97/100)                          │
└──────────────────────────────────────────────────────────────┘
```

### Frontend Architecture (Target State)


```
src/
├── pages/                      # Page Components
│   ├── HomePage.tsx           # Landing + CTA
│   ├── QuestionnairePage.tsx  # 4-step form
│   └── ResultsPage.tsx        # Recommendations list
│
├── components/
│   ├── common/                # Reusable UI
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorMessage.tsx
│   │
│   ├── questionnaire/         # Form components
│   │   ├── StepIndicator.tsx
│   │   ├── BudgetStep.tsx
│   │   ├── UsageStep.tsx
│   │   ├── PrioritiesStep.tsx
│   │   └── PreferencesStep.tsx
│   │
│   └── results/               # Results components
│       ├── CarCard.tsx
│       ├── ScoreVisual.tsx
│       └── FilterBar.tsx
│
├── services/
│   └── api.ts                 # API client with error handling
│
├── hooks/
│   ├── useApi.ts              # Generic API hook
│   ├── useQuestionnaire.ts    # Form state management
│   └── useRecommendations.ts  # Results fetching
│
├── store/
│   └── questionnaireStore.ts  # Zustand store
│
├── types/
│   ├── api.ts                 # API types
│   ├── questionnaire.ts       # Form types
│   └── car.ts                 # Car types
│
└── utils/
    ├── validation.ts          # Form validation
    ├── formatting.ts          # Price, date formatting
    └── constants.ts           # App constants
```

### Data Flow

**User Journey Flow:**
```
1. User lands on HomePage
   └─> Clicks "Começar" button
       └─> Router navigates to /questionario

2. User fills questionnaire (4 steps)
   ├─> Step 0: Budget (min/max)
   ├─> Step 1: Usage + family size
   ├─> Step 2: Priorities (sliders 1-5)
   └─> Step 3: Preferences (brands, colors)
       └─> Zustand stores all data
           └─> On submit: POST /recommend
               └─> Router navigates to /resultados

3. User views results
   ├─> React Query caches response
   ├─> Displays car cards with scores
   └─> Can filter/sort results
       └─> Click WhatsApp → Opens chat
       └─> Click "Nova busca" → Back to step 0
```

## Components and Interfaces

### 1. HomePage Component

**Purpose:** Landing page with value proposition and CTA

**Interface:**
```typescript
// No props - standalone page
export const HomePage: FC = () => {
  const navigate = useNavigate()
  
  return (
    <Box>
      <HeroSection onCTAClick={() => navigate('/questionario')} />
      <FeaturesGrid features={FEATURES} />
      <SocialProof testimonials={TESTIMONIALS} />
      <PricingPreview plans={PRICING_PLANS} />
      <Footer />
    </Box>
  )
}
```

**Sub-components:**
- `HeroSection`: Hero with headline, subheadline, CTA button
- `FeaturesGrid`: 3-4 feature cards in grid
- `SocialProof`: Logos or testimonials
- `PricingPreview`: Pricing tiers preview
- `Footer`: Links and contact info

**Responsive Behavior:**
- Mobile: Single column, stacked sections
- Tablet: 2-column grid for features
- Desktop: Full-width hero, 3-4 column features



### 2. QuestionnairePage Component

**Purpose:** Multi-step form to collect user preferences

**Interface:**
```typescript
interface QuestionnairePageProps {}

export const QuestionnairePage: FC<QuestionnairePageProps> = () => {
  const { currentStep, formData, nextStep, prevStep, submitForm } = 
    useQuestionnaire()
  
  const steps = [
    <BudgetStep />,
    <UsageStep />,
    <PrioritiesStep />,
    <PreferencesStep />
  ]
  
  return (
    <Container>
      <StepIndicator current={currentStep} total={4} />
      {steps[currentStep]}
      <NavigationButtons 
        onNext={nextStep}
        onPrev={prevStep}
        onSubmit={submitForm}
        isLastStep={currentStep === 3}
      />
    </Container>
  )
}
```

**Step Components:**

**BudgetStep (Step 0):**
```typescript
interface BudgetStepProps {
  value: { min: number; max: number }
  onChange: (value: { min: number; max: number }) => void
  errors?: { min?: string; max?: string }
}

// Validation: min < max, both > 0
```

**UsageStep (Step 1):**
```typescript
interface UsageStepProps {
  value: {
    uso_principal: 'trabalho' | 'familia' | 'lazer'
    tamanho_familia: number
  }
  onChange: (value: UsageStepData) => void
}
```

**PrioritiesStep (Step 2):**
```typescript
interface PrioritiesStepProps {
  value: {
    economia: number      // 1-5
    espaco: number        // 1-5
    performance: number   // 1-5
    tecnologia: number    // 1-5
  }
  onChange: (value: PrioritiesData) => void
}

// Uses Chakra UI Slider components
```

**PreferencesStep (Step 3):**
```typescript
interface PreferencesStepProps {
  value: {
    marcas_preferidas?: string[]
    cores_preferidas?: string[]
    transmissao?: 'manual' | 'automatica' | 'ambas'
  }
  onChange: (value: PreferencesData) => void
}
```

**State Management (Zustand):**
```typescript
interface QuestionnaireStore {
  currentStep: number
  formData: QuestionnaireData
  errors: Record<string, string>
  
  setStep: (step: number) => void
  updateFormData: (data: Partial<QuestionnaireData>) => void
  validateStep: (step: number) => boolean
  submitQuestionnaire: () => Promise<void>
  reset: () => void
}
```

### 3. ResultsPage Component

**Purpose:** Display car recommendations with scores

**Interface:**
```typescript
interface ResultsPageProps {}

export const ResultsPage: FC<ResultsPageProps> = () => {
  const { data: recommendations, isLoading, error } = 
    useRecommendations()
  
  const [filters, setFilters] = useState<Filters>({})
  const [sortBy, setSortBy] = useState<SortOption>('score')
  
  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage error={error} />
  
  const filteredCars = applyFilters(recommendations, filters)
  const sortedCars = sortCars(filteredCars, sortBy)
  
  return (
    <Container>
      <ResultsHeader count={sortedCars.length} />
      <FilterBar filters={filters} onChange={setFilters} />
      <SortControls value={sortBy} onChange={setSortBy} />
      <CarGrid>
        {sortedCars.map(rec => (
          <CarCard key={rec.car.id} recommendation={rec} />
        ))}
      </CarGrid>
      <Button onClick={handleNewSearch}>Nova Busca</Button>
    </Container>
  )
}
```

**CarCard Component:**
```typescript
interface CarCardProps {
  recommendation: {
    car: Car
    score: number
    justification: string
  }
  onWhatsAppClick?: (car: Car) => void
}

interface Car {
  id: string
  nome: string
  marca: string
  preco: number
  ano: number
  imagem_url?: string
  categoria: string
  // ... other fields
}
```

**ScoreVisual Component:**
```typescript
interface ScoreVisualProps {
  score: number  // 0-100
  size?: 'sm' | 'md' | 'lg'
}

// Displays circular progress or bar with color coding:
// 0-50: red, 51-70: yellow, 71-100: green
```

### 4. API Service Layer

**api.ts Implementation:**
```typescript
import axios, { AxiosError } from 'axios'
import { QueryClient } from '@tanstack/react-query'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for logging
apiClient.interceptors.request.use(
  config => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  (error: AxiosError) => {
    if (error.response) {
      // Server responded with error
      const status = error.response.status
      const data = error.response.data as any
      
      if (status === 422) {
        // Validation error
        throw new ValidationError(data.detail)
      } else if (status >= 500) {
        // Server error
        throw new ServerError('Erro no servidor. Tente novamente.')
      }
    } else if (error.request) {
      // No response received
      throw new NetworkError('Erro de conexão. Verifique sua internet.')
    }
    
    throw error
  }
)

export const api = {
  health: () => apiClient.get('/health'),
  
  stats: () => apiClient.get('/stats'),
  
  recommend: (data: QuestionnaireData) => 
    apiClient.post<Recommendation[]>('/recommend', data),
  
  dealerships: () => apiClient.get('/dealerships'),
  
  cars: (params?: { marca?: string; categoria?: string }) =>
    apiClient.get('/cars', { params })
}

// Custom error classes
export class ValidationError extends Error {
  constructor(public details: any) {
    super('Validation error')
    this.name = 'ValidationError'
  }
}

export class ServerError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ServerError'
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'NetworkError'
  }
}
```



### 5. Custom Hooks

**useApi Hook:**
```typescript
import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '../services/api'

export const useApi = () => {
  const healthQuery = useQuery({
    queryKey: ['health'],
    queryFn: api.health,
    staleTime: 60000 // 1 minute
  })
  
  const statsQuery = useQuery({
    queryKey: ['stats'],
    queryFn: api.stats,
    staleTime: 300000 // 5 minutes
  })
  
  return { healthQuery, statsQuery }
}
```

**useQuestionnaire Hook:**
```typescript
import { useQuestionnaireStore } from '../store/questionnaireStore'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { api } from '../services/api'

export const useQuestionnaire = () => {
  const navigate = useNavigate()
  const store = useQuestionnaireStore()
  
  const submitMutation = useMutation({
    mutationFn: api.recommend,
    onSuccess: (data) => {
      // Store recommendations and navigate
      navigate('/resultados', { state: { recommendations: data } })
    },
    onError: (error) => {
      // Handle error
      console.error('Submit error:', error)
    }
  })
  
  const nextStep = () => {
    if (store.validateStep(store.currentStep)) {
      store.setStep(store.currentStep + 1)
    }
  }
  
  const prevStep = () => {
    store.setStep(Math.max(0, store.currentStep - 1))
  }
  
  const submitForm = async () => {
    if (store.validateStep(store.currentStep)) {
      await submitMutation.mutateAsync(store.formData)
    }
  }
  
  return {
    currentStep: store.currentStep,
    formData: store.formData,
    errors: store.errors,
    nextStep,
    prevStep,
    submitForm,
    isSubmitting: submitMutation.isPending
  }
}
```

**useRecommendations Hook:**
```typescript
import { useLocation } from 'react-router-dom'
import { useState, useMemo } from 'react'

export const useRecommendations = () => {
  const location = useLocation()
  const recommendations = location.state?.recommendations || []
  
  const [filters, setFilters] = useState({})
  const [sortBy, setSortBy] = useState<'score' | 'price' | 'year'>('score')
  
  const filtered = useMemo(() => {
    let result = [...recommendations]
    
    // Apply filters
    if (filters.marca) {
      result = result.filter(r => r.car.marca === filters.marca)
    }
    if (filters.minPrice) {
      result = result.filter(r => r.car.preco >= filters.minPrice)
    }
    if (filters.maxPrice) {
      result = result.filter(r => r.car.preco <= filters.maxPrice)
    }
    
    // Apply sorting
    result.sort((a, b) => {
      switch (sortBy) {
        case 'score':
          return b.score - a.score
        case 'price':
          return a.car.preco - b.car.preco
        case 'year':
          return b.car.ano - a.car.ano
        default:
          return 0
      }
    })
    
    return result
  }, [recommendations, filters, sortBy])
  
  return {
    data: filtered,
    isLoading: false,
    error: null,
    filters,
    setFilters,
    sortBy,
    setSortBy
  }
}
```

## Data Models

### Frontend Types

**Questionnaire Types:**
```typescript
export interface QuestionnaireData {
  // Step 0: Budget
  orcamento_min: number
  orcamento_max: number
  
  // Step 1: Usage
  uso_principal: 'trabalho' | 'familia' | 'lazer'
  tamanho_familia: number
  
  // Step 2: Priorities (1-5 scale)
  prioridades: {
    economia: number
    espaco: number
    performance: number
    tecnologia: number
  }
  
  // Step 3: Preferences
  marcas_preferidas?: string[]
  cores_preferidas?: string[]
  transmissao?: 'manual' | 'automatica' | 'ambas'
  
  // Location (optional)
  city?: string
  state?: string
}

export interface ValidationErrors {
  [field: string]: string
}
```

**Car Types:**
```typescript
export interface Car {
  id: string
  nome: string
  marca: string
  modelo: string
  ano: number
  preco: number
  categoria: 'hatch' | 'sedan' | 'suv' | 'pickup'
  combustivel: 'flex' | 'gasolina' | 'diesel' | 'eletrico'
  transmissao: 'manual' | 'automatica'
  cor?: string
  km?: number
  imagem_url?: string
  concessionaria_id: string
  concessionaria_nome: string
  created_at: string
  updated_at: string
}

export interface Recommendation {
  car: Car
  score: number  // 0-100
  justification: string
  breakdown: {
    economia: number
    espaco: number
    performance: number
    tecnologia: number
  }
}
```

**API Response Types:**
```typescript
export interface HealthResponse {
  status: 'ok' | 'error'
  timestamp: string
  version: string
}

export interface StatsResponse {
  total_cars: number
  total_dealerships: number
  categories: Record<string, number>
  brands: Record<string, number>
}

export interface RecommendResponse {
  recommendations: Recommendation[]
  total: number
  query_time_ms: number
}
```

### Backend Integration

**API Endpoints Used:**

1. **GET /health**
   - Purpose: Health check
   - Response: `{ status: 'ok', timestamp: '...' }`

2. **GET /stats**
   - Purpose: Get system statistics
   - Response: `{ total_cars: 129, total_dealerships: 3, ... }`

3. **POST /recommend**
   - Purpose: Get car recommendations
   - Request Body: `QuestionnaireData`
   - Response: `Recommendation[]`

4. **GET /dealerships**
   - Purpose: List all dealerships
   - Response: `Dealership[]`

5. **GET /cars**
   - Purpose: List cars with optional filters
   - Query Params: `marca`, `categoria`, `min_preco`, `max_preco`
   - Response: `Car[]`

## Error Handling

### Error Types and Handling Strategy

**1. Network Errors (No connection)**
```typescript
// Detection: error.request exists but no response
// User Message: "Erro de conexão. Verifique sua internet."
// Action: Show retry button
// Retry Strategy: Exponential backoff (1s, 2s, 4s)
```

**2. Validation Errors (422)**
```typescript
// Detection: response.status === 422
// User Message: Field-specific errors from backend
// Action: Highlight invalid fields, show inline errors
// Example: "Orçamento mínimo deve ser menor que máximo"
```

**3. Server Errors (500+)**
```typescript
// Detection: response.status >= 500
// User Message: "Erro no servidor. Tente novamente em instantes."
// Action: Show generic error with retry
// Logging: Send to error tracking service
```

**4. Timeout Errors**
```typescript
// Detection: axios timeout exceeded (10s)
// User Message: "A operação está demorando. Deseja continuar?"
// Action: Show dialog with "Aguardar" or "Cancelar"
```

**5. Client-Side Validation**
```typescript
// Detection: Before API call
// User Message: Specific field errors
// Action: Prevent form submission, highlight fields
// Examples:
//   - "Campo obrigatório"
//   - "Orçamento mínimo deve ser maior que R$ 0"
//   - "Selecione pelo menos uma prioridade"
```

### Error UI Components

**ErrorMessage Component:**
```typescript
interface ErrorMessageProps {
  error: Error | string
  onRetry?: () => void
  variant?: 'inline' | 'toast' | 'page'
}

// Variants:
// - inline: Small error below field
// - toast: Chakra UI toast notification
// - page: Full-page error state
```

**LoadingSpinner Component:**
```typescript
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  message?: string
  fullPage?: boolean
}

// Shows Chakra UI Spinner with optional message
// fullPage: Centers in viewport
```



## Testing Strategy

### Unit Tests (Vitest + Testing Library)

**Target Coverage: 80%+**

**1. Component Tests**
```typescript
// Example: CarCard.test.tsx
describe('CarCard', () => {
  const mockCar = {
    id: '1',
    nome: 'Fiat Cronos',
    marca: 'Fiat',
    preco: 84990,
    score: 87
  }
  
  it('should render car name', () => {
    render(<CarCard recommendation={{ car: mockCar, score: 87 }} />)
    expect(screen.getByText('Fiat Cronos')).toBeInTheDocument()
  })
  
  it('should format price correctly', () => {
    render(<CarCard recommendation={{ car: mockCar, score: 87 }} />)
    expect(screen.getByText('R$ 84.990')).toBeInTheDocument()
  })
  
  it('should call onWhatsAppClick when button clicked', () => {
    const onWhatsAppClick = vi.fn()
    render(<CarCard 
      recommendation={{ car: mockCar, score: 87 }}
      onWhatsAppClick={onWhatsAppClick}
    />)
    
    fireEvent.click(screen.getByText(/WhatsApp/i))
    expect(onWhatsAppClick).toHaveBeenCalledWith(mockCar)
  })
})
```

**2. Hook Tests**
```typescript
// Example: useQuestionnaire.test.ts
describe('useQuestionnaire', () => {
  it('should initialize with step 0', () => {
    const { result } = renderHook(() => useQuestionnaire())
    expect(result.current.currentStep).toBe(0)
  })
  
  it('should advance to next step when valid', () => {
    const { result } = renderHook(() => useQuestionnaire())
    
    act(() => {
      result.current.updateFormData({
        orcamento_min: 50000,
        orcamento_max: 100000
      })
      result.current.nextStep()
    })
    
    expect(result.current.currentStep).toBe(1)
  })
  
  it('should not advance when validation fails', () => {
    const { result } = renderHook(() => useQuestionnaire())
    
    act(() => {
      result.current.updateFormData({
        orcamento_min: 100000,
        orcamento_max: 50000  // Invalid: min > max
      })
      result.current.nextStep()
    })
    
    expect(result.current.currentStep).toBe(0)
    expect(result.current.errors).toHaveProperty('orcamento_max')
  })
})
```

**3. Service Tests**
```typescript
// Example: api.test.ts
describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })
  
  it('should call /recommend with correct data', async () => {
    const mockData = { orcamento_min: 50000, orcamento_max: 100000 }
    const mockResponse = { data: [{ car: {}, score: 85 }] }
    
    vi.spyOn(axios, 'post').mockResolvedValue(mockResponse)
    
    const result = await api.recommend(mockData)
    
    expect(axios.post).toHaveBeenCalledWith('/recommend', mockData)
    expect(result.data).toEqual(mockResponse.data)
  })
  
  it('should throw ValidationError on 422', async () => {
    const error = {
      response: { status: 422, data: { detail: 'Invalid data' } }
    }
    
    vi.spyOn(axios, 'post').mockRejectedValue(error)
    
    await expect(api.recommend({})).rejects.toThrow(ValidationError)
  })
  
  it('should throw NetworkError when offline', async () => {
    const error = { request: {}, response: undefined }
    
    vi.spyOn(axios, 'post').mockRejectedValue(error)
    
    await expect(api.recommend({})).rejects.toThrow(NetworkError)
  })
})
```

**4. Store Tests**
```typescript
// Example: questionnaireStore.test.ts
describe('QuestionnaireStore', () => {
  beforeEach(() => {
    useQuestionnaireStore.getState().reset()
  })
  
  it('should update form data', () => {
    const { updateFormData } = useQuestionnaireStore.getState()
    
    updateFormData({ orcamento_min: 50000 })
    
    expect(useQuestionnaireStore.getState().formData.orcamento_min)
      .toBe(50000)
  })
  
  it('should validate budget step', () => {
    const { updateFormData, validateStep } = 
      useQuestionnaireStore.getState()
    
    updateFormData({
      orcamento_min: 50000,
      orcamento_max: 100000
    })
    
    expect(validateStep(0)).toBe(true)
  })
  
  it('should fail validation when min > max', () => {
    const { updateFormData, validateStep } = 
      useQuestionnaireStore.getState()
    
    updateFormData({
      orcamento_min: 100000,
      orcamento_max: 50000
    })
    
    expect(validateStep(0)).toBe(false)
  })
})
```

### Integration Tests (Cypress E2E)

**Target: 15+ tests covering critical user journeys**

**1. Happy Path - Complete Journey**
```typescript
// cypress/e2e/user-journey.cy.ts
describe('Complete User Journey', () => {
  it('should complete full recommendation flow', () => {
    // 1. Visit homepage
    cy.visit('/')
    cy.contains('FacilIAuto').should('be.visible')
    
    // 2. Click CTA
    cy.contains('Começar').click()
    cy.url().should('include', '/questionario')
    
    // 3. Fill Step 0 (Budget)
    cy.get('[data-testid="orcamento-min"]').type('50000')
    cy.get('[data-testid="orcamento-max"]').type('100000')
    cy.contains('Próximo').click()
    
    // 4. Fill Step 1 (Usage)
    cy.get('[data-testid="uso-principal"]').select('familia')
    cy.get('[data-testid="tamanho-familia"]').type('4')
    cy.contains('Próximo').click()
    
    // 5. Fill Step 2 (Priorities)
    cy.get('[data-testid="slider-economia"]').invoke('val', 4).trigger('change')
    cy.get('[data-testid="slider-espaco"]').invoke('val', 5).trigger('change')
    cy.get('[data-testid="slider-performance"]').invoke('val', 3).trigger('change')
    cy.contains('Próximo').click()
    
    // 6. Fill Step 3 (Preferences)
    cy.get('[data-testid="marca-fiat"]').check()
    cy.get('[data-testid="marca-toyota"]').check()
    cy.contains('Ver Recomendações').click()
    
    // 7. Verify results
    cy.url().should('include', '/resultados')
    cy.get('[data-testid="car-card"]').should('have.length.at.least', 1)
    cy.contains(/score/i).should('be.visible')
  })
})
```

**2. Validation Tests**
```typescript
// cypress/e2e/validation.cy.ts
describe('Form Validation', () => {
  beforeEach(() => {
    cy.visit('/questionario')
  })
  
  it('should show error when min > max budget', () => {
    cy.get('[data-testid="orcamento-min"]').type('100000')
    cy.get('[data-testid="orcamento-max"]').type('50000')
    cy.contains('Próximo').click()
    
    cy.contains(/mínimo deve ser menor/i).should('be.visible')
    cy.url().should('include', '/questionario')  // Should not advance
  })
  
  it('should require all mandatory fields', () => {
    cy.contains('Próximo').click()
    
    cy.contains(/campo obrigatório/i).should('be.visible')
  })
  
  it('should validate budget range', () => {
    cy.get('[data-testid="orcamento-min"]').type('-1000')
    cy.contains('Próximo').click()
    
    cy.contains(/valor inválido/i).should('be.visible')
  })
})
```

**3. Error Handling Tests**
```typescript
// cypress/e2e/error-handling.cy.ts
describe('Error Handling', () => {
  it('should handle API offline gracefully', () => {
    // Intercept and fail API call
    cy.intercept('POST', '/recommend', { forceNetworkError: true })
    
    cy.visit('/questionario')
    // Fill form...
    cy.contains('Ver Recomendações').click()
    
    cy.contains(/erro de conexão/i).should('be.visible')
    cy.contains('Tentar Novamente').should('be.visible')
  })
  
  it('should handle server error (500)', () => {
    cy.intercept('POST', '/recommend', {
      statusCode: 500,
      body: { detail: 'Internal server error' }
    })
    
    cy.visit('/questionario')
    // Fill form...
    cy.contains('Ver Recomendações').click()
    
    cy.contains(/erro no servidor/i).should('be.visible')
  })
  
  it('should handle no results found', () => {
    cy.intercept('POST', '/recommend', {
      statusCode: 200,
      body: { recommendations: [] }
    })
    
    cy.visit('/questionario')
    // Fill form...
    cy.contains('Ver Recomendações').click()
    
    cy.contains(/nenhum carro encontrado/i).should('be.visible')
    cy.contains('Nova Busca').should('be.visible')
  })
})
```

**4. Navigation Tests**
```typescript
// cypress/e2e/navigation.cy.ts
describe('Navigation', () => {
  it('should allow back navigation between steps', () => {
    cy.visit('/questionario')
    
    // Go to step 1
    cy.get('[data-testid="orcamento-min"]').type('50000')
    cy.get('[data-testid="orcamento-max"]').type('100000')
    cy.contains('Próximo').click()
    
    // Go back to step 0
    cy.contains('Anterior').click()
    cy.get('[data-testid="orcamento-min"]').should('have.value', '50000')
  })
  
  it('should preserve form data when navigating back', () => {
    cy.visit('/questionario')
    
    // Fill multiple steps
    cy.get('[data-testid="orcamento-min"]').type('50000')
    cy.get('[data-testid="orcamento-max"]').type('100000')
    cy.contains('Próximo').click()
    
    cy.get('[data-testid="uso-principal"]').select('familia')
    cy.contains('Próximo').click()
    
    // Navigate back
    cy.contains('Anterior').click()
    cy.get('[data-testid="uso-principal"]').should('have.value', 'familia')
    
    cy.contains('Anterior').click()
    cy.get('[data-testid="orcamento-min"]').should('have.value', '50000')
  })
})
```

**5. Responsive Tests**
```typescript
// cypress/e2e/responsive.cy.ts
describe('Responsive Design', () => {
  const viewports = [
    { name: 'mobile', width: 375, height: 667 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'desktop', width: 1920, height: 1080 }
  ]
  
  viewports.forEach(({ name, width, height }) => {
    it(`should be usable on ${name}`, () => {
      cy.viewport(width, height)
      cy.visit('/')
      
      // Verify key elements are visible
      cy.contains('FacilIAuto').should('be.visible')
      cy.contains('Começar').should('be.visible')
      
      // Verify navigation works
      cy.contains('Começar').click()
      cy.url().should('include', '/questionario')
    })
  })
})
```

### Performance Tests

**Lighthouse CI Integration:**
```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [push]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Lighthouse
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            http://localhost:3000
            http://localhost:3000/questionario
            http://localhost:3000/resultados
          uploadArtifacts: true
```

**Performance Budgets:**
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Speed Index: < 2.5s
- Total Bundle Size: < 500KB (gzipped)
- Lighthouse Score: > 90



## Deployment and Infrastructure

### Development Environment

**Prerequisites:**
- Node.js 18+ (for frontend)
- Python 3.9+ (for backend)
- npm or yarn (for frontend dependencies)
- pip (for backend dependencies)

**Environment Variables:**

**.env.development (Frontend):**
```bash
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=FacilIAuto
VITE_ENABLE_ANALYTICS=false
```

**.env (Backend):**
```bash
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
LOG_LEVEL=INFO
```

### Startup Scripts

**Windows (start-faciliauto.bat):**
```batch
@echo off
echo ========================================
echo   FacilIAuto - Iniciando Sistema
echo ========================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado
    echo Instale Python 3.9+ de https://python.org
    pause
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Node.js nao encontrado
    echo Instale Node.js 18+ de https://nodejs.org
    pause
    exit /b 1
)

REM Check if ports are available
netstat -ano | findstr :8000 >nul
if not errorlevel 1 (
    echo AVISO: Porta 8000 em uso
    echo Execute: netstat -ano | findstr :8000
    echo Depois: taskkill /PID [PID] /F
    pause
)

netstat -ano | findstr :3000 >nul
if not errorlevel 1 (
    echo AVISO: Porta 3000 em uso
    echo Execute: netstat -ano | findstr :3000
    echo Depois: taskkill /PID [PID] /F
    pause
)

REM Start Backend
echo [1/3] Iniciando Backend...
cd platform\backend
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt --quiet
start "FacilIAuto Backend" cmd /k "python api\main.py"
cd ..\..
timeout /t 5 /nobreak >nul

REM Start Frontend
echo [2/3] Iniciando Frontend...
cd platform\frontend
if not exist node_modules (
    echo Instalando dependencias...
    npm install --silent
)
start "FacilIAuto Frontend" cmd /k "npm run dev"
cd ..\..

echo [3/3] Sistema iniciado!
echo.
echo ========================================
echo   URLs de Acesso:
echo ========================================
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo ========================================
echo.
echo Pressione qualquer tecla para abrir o navegador...
pause >nul
start http://localhost:3000
```

**Linux/Mac (start-faciliauto.sh):**
```bash
#!/bin/bash

echo "========================================"
echo "  FacilIAuto - Iniciando Sistema"
echo "========================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python não encontrado"
    echo "Instale Python 3.9+ com: sudo apt install python3"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "ERRO: Node.js não encontrado"
    echo "Instale Node.js 18+ de https://nodejs.org"
    exit 1
fi

# Check ports
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "AVISO: Porta 8000 em uso"
    echo "Execute: lsof -ti:8000 | xargs kill -9"
    read -p "Continuar? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "AVISO: Porta 3000 em uso"
    echo "Execute: lsof -ti:3000 | xargs kill -9"
    read -p "Continuar? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start Backend
echo "[1/3] Iniciando Backend..."
cd platform/backend
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt --quiet
python3 api/main.py &
BACKEND_PID=$!
cd ../..
sleep 5

# Start Frontend
echo "[2/3] Iniciando Frontend..."
cd platform/frontend
if [ ! -d "node_modules" ]; then
    echo "Instalando dependências..."
    npm install --silent
fi
npm run dev &
FRONTEND_PID=$!
cd ../..

echo "[3/3] Sistema iniciado!"
echo ""
echo "========================================"
echo "  URLs de Acesso:"
echo "========================================"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Pressione Ctrl+C para parar"

# Cleanup on exit
cleanup() {
    echo ""
    echo "Encerrando serviços..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Sistema encerrado."
    exit 0
}

trap cleanup INT TERM

# Wait for user interrupt
wait
```

### Docker Deployment (Production)

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./platform/backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - CORS_ORIGINS=https://faciliauto.com
    volumes:
      - ./platform/backend/data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  frontend:
    build: ./platform/frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=https://api.faciliauto.com
    depends_on:
      - backend
    restart: unless-stopped
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
  
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped
  
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=faciliauto2024
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped

volumes:
  grafana-data:
```

### CI/CD Pipeline

**GitHub Actions (.github/workflows/ci.yml):**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          cd platform/backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd platform/backend
          pytest tests/ -v --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./platform/backend/coverage.xml
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd platform/frontend
          npm ci
      
      - name: Run unit tests
        run: |
          cd platform/frontend
          npm test
      
      - name: Run E2E tests
        run: |
          cd platform/frontend
          npm run e2e:headless
  
  build:
    needs: [backend-tests, frontend-tests]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker-compose build
      
      - name: Push to registry
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker-compose push
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/faciliauto
            docker-compose pull
            docker-compose up -d
            docker-compose exec backend python scripts/health_check.py
```

### Monitoring and Observability

**Health Check Endpoint:**
```python
# backend/api/main.py
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "checks": {
            "database": "ok",
            "cache": "ok",
            "api": "ok"
        }
    }
```

**Prometheus Metrics:**
```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    request_count.inc()
    with request_duration.time():
        response = await call_next(request)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

**Grafana Dashboards:**
- API Request Rate
- Response Time (P50, P95, P99)
- Error Rate
- Active Users
- Recommendation Success Rate

### Security Considerations

**CORS Configuration:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://faciliauto.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Rate Limiting:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/recommend")
@limiter.limit("10/minute")
async def recommend(request: Request, data: QuestionnaireData):
    # Implementation
    pass
```

**Input Validation:**
```python
from pydantic import BaseModel, validator

class QuestionnaireData(BaseModel):
    orcamento_min: int
    orcamento_max: int
    
    @validator('orcamento_min')
    def validate_min_budget(cls, v):
        if v < 0:
            raise ValueError('Orçamento mínimo deve ser positivo')
        return v
    
    @validator('orcamento_max')
    def validate_max_budget(cls, v, values):
        if 'orcamento_min' in values and v < values['orcamento_min']:
            raise ValueError('Orçamento máximo deve ser maior que mínimo')
        return v
```



## Implementation Phases

### Phase 1: Frontend Pages (Week 1, Days 1-5)

**Goal:** Complete all 3 main pages with functional components

**Day 1-2: HomePage**
- Implement HeroSection with CTA
- Create FeaturesGrid component
- Add SocialProof section
- Implement PricingPreview
- Add Footer with links
- Ensure mobile responsiveness
- Write unit tests for all components

**Day 3: QuestionnairePage - Steps 0-1**
- Implement StepIndicator component
- Create BudgetStep (Step 0) with validation
- Create UsageStep (Step 1) with dropdowns
- Implement navigation buttons
- Add form state management with Zustand
- Write unit tests

**Day 4: QuestionnairePage - Steps 2-3**
- Create PrioritiesStep (Step 2) with sliders
- Create PreferencesStep (Step 3) with checkboxes
- Implement step validation logic
- Add error messages
- Write unit tests

**Day 5: ResultsPage**
- Implement CarCard component
- Create ScoreVisual component
- Add FilterBar for filtering results
- Implement sorting controls
- Add "Nova Busca" button
- Write unit tests

**Deliverables:**
- 3 fully functional pages
- 15+ reusable components
- 30+ unit tests
- Mobile-responsive design

### Phase 2: API Integration (Week 2, Days 6-8)

**Goal:** Connect frontend to backend with robust error handling

**Day 6: API Service Layer**
- Complete api.ts with all endpoints
- Implement axios interceptors
- Add error handling (Network, Validation, Server)
- Create custom error classes
- Add retry logic with exponential backoff
- Write service tests

**Day 7: React Query Integration**
- Set up QueryClient
- Implement useApi hook
- Implement useRecommendations hook
- Add caching strategy
- Implement optimistic updates
- Write hook tests

**Day 8: Integration Testing**
- Test all API endpoints from frontend
- Verify CORS configuration
- Test error scenarios
- Validate data flow
- Fix integration issues
- Document API usage

**Deliverables:**
- Complete API service layer
- React Query integration
- 15+ integration tests
- CORS properly configured

### Phase 3: E2E Tests (Week 2, Days 9-10)

**Goal:** Implement comprehensive E2E test suite

**Day 9: Happy Path Tests**
- Complete user journey test
- Navigation tests
- Form submission tests
- Results display tests
- Write 8+ E2E tests

**Day 10: Edge Cases & Error Handling**
- Validation error tests
- Network error tests
- Server error tests
- No results tests
- Responsive tests
- Write 7+ E2E tests

**Deliverables:**
- 15+ E2E tests passing
- Coverage of critical user journeys
- Error scenarios tested
- Responsive behavior validated

### Phase 4: Polish & Optimization (Week 3, Days 11-13)

**Goal:** Improve UX, performance, and code quality

**Day 11: UX Improvements**
- Add loading states everywhere
- Improve error messages
- Add animations and transitions
- Implement toast notifications
- Improve mobile UX
- Add accessibility features

**Day 12: Performance Optimization**
- Implement lazy loading
- Add code splitting
- Optimize images
- Reduce bundle size
- Improve Lighthouse scores
- Add performance monitoring

**Day 13: Code Quality**
- Refactor duplicated code
- Improve type safety
- Add missing tests
- Update documentation
- Code review and cleanup
- Ensure 80%+ coverage

**Deliverables:**
- Polished UX with animations
- Lighthouse score > 90
- Bundle size < 500KB
- 80%+ test coverage
- Clean, maintainable code

### Phase 5: Documentation & Deployment (Week 3, Days 14-15)

**Goal:** Update documentation and prepare for production

**Day 14: Documentation**
- Update README.md with real status
- Create COMO-EXECUTAR.md guide
- Update STATUS-REAL-ATUAL.md
- Create CHANGELOG.md
- Document API integration
- Create troubleshooting guide

**Day 15: Deployment Preparation**
- Test startup scripts
- Validate Docker setup
- Configure CI/CD
- Set up monitoring
- Create deployment checklist
- Final validation

**Deliverables:**
- Complete, accurate documentation
- Tested startup scripts
- Production-ready deployment
- Monitoring configured
- System 100% complete

## Success Criteria

### Functional Requirements

**Frontend:**
- [ ] HomePage renders correctly on all devices
- [ ] Questionnaire has 4 working steps with validation
- [ ] Results page displays recommendations with scores
- [ ] Navigation works smoothly between pages
- [ ] All forms validate correctly
- [ ] Error messages are clear and helpful

**Integration:**
- [ ] Frontend successfully calls all backend endpoints
- [ ] CORS is configured correctly
- [ ] Error handling works for all scenarios
- [ ] Loading states appear appropriately
- [ ] Data flows correctly end-to-end

**Testing:**
- [ ] 50+ unit tests passing (80%+ coverage)
- [ ] 15+ E2E tests passing
- [ ] All critical user journeys tested
- [ ] Edge cases covered
- [ ] CI/CD pipeline runs tests automatically

**Performance:**
- [ ] Page load time < 2s
- [ ] API response time < 100ms
- [ ] Lighthouse score > 90
- [ ] Bundle size < 500KB (gzipped)
- [ ] No console errors

**Deployment:**
- [ ] System starts with one command
- [ ] Scripts work on Windows and Linux/Mac
- [ ] Docker setup works correctly
- [ ] Health checks pass
- [ ] Monitoring is functional

### Non-Functional Requirements

**Code Quality:**
- [ ] TypeScript strict mode enabled
- [ ] ESLint passes with no errors
- [ ] Prettier formatting applied
- [ ] No code duplication
- [ ] Clear, descriptive variable names

**Documentation:**
- [ ] README reflects real status
- [ ] All components documented
- [ ] API integration documented
- [ ] Troubleshooting guide exists
- [ ] CHANGELOG is up to date

**Accessibility:**
- [ ] WCAG 2.1 AA compliance
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Sufficient color contrast
- [ ] Focus states visible

**Security:**
- [ ] Input validation on all forms
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] No sensitive data in logs
- [ ] HTTPS in production

## Risk Mitigation

### Technical Risks

**Risk 1: CORS Issues**
- **Probability:** Medium
- **Impact:** High (blocks integration)
- **Mitigation:** Test CORS early, have fallback proxy configuration
- **Contingency:** Use nginx proxy if direct CORS fails

**Risk 2: Performance Issues**
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:** Implement lazy loading, code splitting from start
- **Contingency:** Optimize bundle, use CDN for assets

**Risk 3: Test Flakiness**
- **Probability:** Medium
- **Impact:** Medium (slows CI/CD)
- **Mitigation:** Use proper waits in E2E tests, mock API calls
- **Contingency:** Retry failed tests, improve test stability

**Risk 4: Browser Compatibility**
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:** Use modern but widely supported features
- **Contingency:** Add polyfills if needed

### Schedule Risks

**Risk 1: Scope Creep**
- **Probability:** Medium
- **Impact:** High (delays completion)
- **Mitigation:** Strict scope definition, no new features
- **Contingency:** Defer non-critical items to post-launch

**Risk 2: Unexpected Bugs**
- **Probability:** High
- **Impact:** Medium
- **Mitigation:** Comprehensive testing, early integration
- **Contingency:** Buffer time in schedule (15 days vs 10 needed)

**Risk 3: Dependency Issues**
- **Probability:** Low
- **Impact:** Low
- **Mitigation:** Lock dependency versions, test upgrades
- **Contingency:** Rollback to known good versions

## Conclusion

This design provides a comprehensive blueprint for completing the FacilIAuto system from 84% to 100%. The architecture leverages existing strengths (excellent backend) while systematically addressing gaps (frontend completion, integration validation, E2E testing).

Key success factors:
1. **Incremental approach:** Build and test one component at a time
2. **Test-driven:** Write tests alongside implementation
3. **Integration-first:** Validate backend connection early
4. **User-focused:** Prioritize UX and error handling
5. **Quality-assured:** Maintain 80%+ test coverage throughout

The phased implementation plan provides clear milestones and deliverables, with built-in risk mitigation and contingency plans. Following this design will result in a production-ready, fully functional system that meets all requirements and quality standards.

