# Design Document - Frontend MVP Completion

## Overview

This design document outlines the architecture and implementation strategy for completing the FacilIAuto frontend from 40% to 90%+ production-ready state. The frontend is a React 18 + TypeScript single-page application using Chakra UI for mobile-first design, Zustand for state management, and React Query for server state.

### Current State (40%)
- ✅ Project structure and tooling configured
- ✅ Basic routing (3 pages: Home, Questionnaire, Results)
- ✅ Type definitions synchronized with backend
- ✅ API service layer with error handling
- ✅ Zustand store for questionnaire state
- ✅ Chakra UI theme with brand colors
- ⚠️ Components partially implemented
- ⚠️ Pages incomplete (skeleton only)
- ⚠️ No error boundaries or loading states
- ⚠️ Limited mobile optimization
- ⚠️ No E2E tests

### Target State (90%+)
- ✅ Complete 4-step questionnaire flow
- ✅ Full results page with filtering/sorting
- ✅ Car detail modal with WhatsApp integration
- ✅ Comprehensive error handling
- ✅ Loading states and skeleton screens
- ✅ Mobile-first responsive design (320px-1920px)
- ✅ Accessibility (WCAG AA)
- ✅ E2E test coverage for critical flows
- ✅ Performance optimizations (code splitting, lazy loading)

## Architecture

### Technology Stack

**Core Framework**
- React 18.2 (with hooks and concurrent features)
- TypeScript 5.3 (strict mode)
- Vite 5.0 (build tool and dev server)

**UI & Styling**
- Chakra UI 2.8 (component library)
- Emotion (CSS-in-JS)
- Framer Motion 10.16 (animations)
- React Icons 4.12 (icon library)

**State Management**
- Zustand 4.4 (global state)
- TanStack React Query 5.12 (server state)
- React Router 6.20 (routing)

**HTTP & API**
- Axios 1.6 (HTTP client)
- Custom API service layer with interceptors

**Testing**
- Vitest 1.0 (unit tests)
- Testing Library (component tests)
- Cypress 13.6 (E2E tests)

### Application Structure

```
src/
├── components/          # Reusable UI components
│   ├── common/         # Generic components (Button, Card, etc.)
│   ├── questionnaire/  # Questionnaire-specific components
│   ├── results/        # Results page components
│   └── dealership/     # Dealership-specific components
├── pages/              # Route-level page components
│   ├── HomePage.tsx
│   ├── QuestionnairePage.tsx
│   └── ResultsPage.tsx
├── services/           # API and external services
│   ├── api.ts
│   └── InteractionTracker.ts
├── store/              # Zustand stores
│   └── questionnaireStore.ts
├── hooks/              # Custom React hooks
│   └── useApi.ts
├── types/              # TypeScript type definitions
│   └── index.ts
├── theme/              # Chakra UI theme customization
│   └── index.ts
├── utils/              # Utility functions
│   └── imagePlaceholder.ts
├── App.tsx             # Root component
└── main.tsx            # Application entry point
```


## Components and Interfaces

### Page Components

#### 1. HomePage
**Purpose**: Landing page with call-to-action to start questionnaire

**Key Features**:
- Hero section with value proposition
- "Começar" button navigating to /questionario
- Platform statistics (total cars, dealerships)
- Mobile-optimized layout

**State**: None (stateless)

**API Calls**: GET /stats (optional, for displaying platform stats)

#### 2. QuestionnairePage
**Purpose**: 4-step user profiling flow

**Key Features**:
- Step indicator (1/4, 2/4, 3/4, 4/4)
- Progress bar
- Step navigation (Next, Previous)
- Form validation per step
- Data persistence in Zustand store

**Steps**:
1. **Budget & Location** (Step 0)
   - Budget range slider (R$ 30k - R$ 200k+)
   - City/State selection (optional)
   
2. **Usage Profile** (Step 1)
   - 6 usage options with icons and descriptions
   - Single selection (radio buttons styled as cards)
   
3. **Priorities** (Step 2)
   - 5 priority sliders (Economia, Espaço, Performance, Conforto, Segurança)
   - Real-time top 3 highlighting
   - Default values based on usage profile
   
4. **Location** (Step 3)
   - City/State selection
   - Distance radius (optional)
   - "Ver Recomendações" button

**State**: Zustand questionnaireStore

**API Calls**: None (all client-side until submission)

#### 3. ResultsPage
**Purpose**: Display personalized car recommendations

**Key Features**:
- User profile summary (top 3 priorities, budget, location)
- Car grid with filtering and sorting
- Car detail modal
- WhatsApp contact integration
- Empty state handling

**State**: 
- React Query for recommendations data
- Local state for filters and sort order

**API Calls**: 
- POST /recommend (on mount with user profile)
- POST /api/interactions/track (for ML data collection)

### Component Library

#### Common Components

**1. Button**
- Variants: solid, outline, ghost
- Sizes: sm, md, lg
- Loading state support
- Icon support (left/right)

**2. Card**
- Hover effects
- Click handling
- Image support
- Badge support

**3. LoadingSpinner**
- Sizes: sm, md, lg
- Centered or inline
- Custom colors

**4. ErrorMessage**
- User-friendly error display
- Retry button option
- Icon support

**5. SkeletonCard**
- Loading placeholder for car cards
- Matches car card dimensions
- Animated shimmer effect

#### Questionnaire Components

**1. StepIndicator**
- Props: currentStep, totalSteps
- Visual progress bar
- Step labels

**2. BudgetSlider**
- Dual-handle range slider
- Currency formatting (R$)
- Min/max labels
- Real-time value display

**3. UsageProfileCard**
- Props: profile, selected, onClick
- Icon, title, description
- Selected state styling
- Mobile-optimized tap target

**4. PrioritySlider**
- Props: label, value, onChange, isTopPriority
- 1-5 scale
- Visual highlighting for top 3
- Tooltip with explanation

**5. LocationSelector**
- City autocomplete
- State dropdown
- Distance radius slider (optional)

#### Results Components

**1. CarCard**
- Props: car, onClick
- Car image with fallback
- Name, price, year
- Match score badge (0-100%)
- Top 3 features
- Hover effects

**2. CarDetailsModal**
- Props: car, isOpen, onClose
- Full car specifications
- Image gallery
- Justification text
- WhatsApp contact button
- Dealership information

**3. FilterPanel**
- Price range filter
- Category filter (Hatch, Sedan, SUV, etc.)
- Brand filter
- Dealership filter
- Clear filters button

**4. SortDropdown**
- Sort options: Score (default), Price (low-high), Price (high-low), Year (newest)
- Dropdown with icons

**5. ProfileSummary**
- Display user's top 3 priorities
- Budget range
- Location (if provided)
- Edit button (returns to questionnaire)

**6. EmptyState**
- Props: message, actionButton
- Illustration or icon
- Helpful message
- Suggested actions


## Data Models

### Frontend-Specific Models

#### QuestionnaireState
```typescript
interface QuestionnaireState {
  currentStep: number              // 0-3
  formData: QuestionnaireFormData
  canGoNext: () => boolean
  isComplete: () => boolean
  toUserProfile: () => UserProfile
}
```

#### ResultsState
```typescript
interface ResultsState {
  recommendations: Recommendation[]
  filters: {
    priceMin?: number
    priceMax?: number
    categories: string[]
    brands: string[]
    dealerships: string[]
  }
  sortBy: 'score' | 'price_asc' | 'price_desc' | 'year'
  isLoading: boolean
  error: ApiError | null
}
```

#### UIState
```typescript
interface UIState {
  selectedCarId: string | null
  isModalOpen: boolean
  isMobileMenuOpen: boolean
  toast: {
    message: string
    type: 'success' | 'error' | 'info'
    isVisible: boolean
  }
}
```

### Data Flow

```
User Input → Zustand Store → UserProfile → Backend API → Recommendations → React Query Cache → UI
     ↓                                                                              ↓
  localStorage                                                              InteractionTracker
```

**Step-by-Step Flow**:

1. **Questionnaire Flow**
   - User fills Step 1 → updateFormData() → Zustand store
   - User clicks Next → canGoNext() validates → nextStep()
   - Repeat for Steps 2-4
   - User clicks "Ver Recomendações" → toUserProfile() → navigate to /resultados

2. **Results Flow**
   - ResultsPage mounts → read user profile from Zustand
   - Call POST /recommend with profile → React Query manages request
   - Display loading state (skeleton cards)
   - Receive recommendations → render car cards
   - User applies filters → filter locally (no API call)
   - User clicks car → open modal with details
   - User clicks WhatsApp → track interaction → open WhatsApp

3. **Error Handling Flow**
   - API call fails → React Query error state
   - Display ErrorMessage component
   - User clicks Retry → React Query refetch
   - If retry fails 3x → suggest returning to questionnaire

## Error Handling

### Error Types

**1. Network Errors**
- Timeout (30s)
- Connection refused
- DNS resolution failure

**Strategy**: Display "Sem conexão" message with retry button

**2. Validation Errors (400)**
- Invalid user profile
- Missing required fields

**Strategy**: Display field-specific error messages, highlight invalid fields

**3. Server Errors (500)**
- Backend crash
- Database unavailable

**Strategy**: Display generic "Algo deu errado" message, log details to console

**4. Not Found (404)**
- Car or dealership not found

**Strategy**: Display "Não encontrado" message, suggest alternatives

### Error Boundaries

**Root Error Boundary**
- Catches unhandled React errors
- Displays fallback UI
- Logs error to console (future: send to monitoring service)
- Provides "Recarregar página" button

**Page-Level Error Boundaries**
- Wrap each page component
- Allows other pages to continue working
- Provides navigation back to home

### Loading States

**1. Initial Page Load**
- Full-page spinner with logo
- Duration: < 2s

**2. API Requests**
- Skeleton screens for lists (car cards)
- Inline spinners for actions (buttons)
- Progress indicators for multi-step processes

**3. Image Loading**
- Placeholder images (gray background with car icon)
- Lazy loading with Intersection Observer
- Fade-in animation when loaded

**4. Optimistic Updates**
- Filters apply immediately (local state)
- Sort changes apply immediately
- No loading state for client-side operations


## Mobile-First Responsive Design

### Breakpoints

```typescript
const breakpoints = {
  mobile: '320px',      // Small phones
  mobileLg: '428px',    // Large phones (iPhone 14 Pro Max)
  tablet: '768px',      // Tablets
  desktop: '1024px',    // Small desktops
  desktopLg: '1440px',  // Large desktops
}
```

### Layout Strategy

**Mobile (320px - 767px)**
- Single column layout
- Full-width components
- Stacked navigation
- Bottom-fixed CTAs
- Touch-optimized (44px min tap target)
- Vertical scrolling

**Tablet (768px - 1023px)**
- 2-column grid for car cards
- Side-by-side filters (collapsible)
- Larger touch targets (48px)
- Horizontal + vertical scrolling

**Desktop (1024px+)**
- 3-4 column grid for car cards
- Persistent filter sidebar
- Hover effects
- Mouse-optimized interactions
- Horizontal scrolling for image galleries

### Component Responsiveness

**CarCard**
- Mobile: Full width, vertical layout
- Tablet: 2 per row, compact layout
- Desktop: 3-4 per row, expanded layout

**FilterPanel**
- Mobile: Bottom sheet (slide up)
- Tablet: Collapsible sidebar
- Desktop: Persistent sidebar

**CarDetailsModal**
- Mobile: Full screen
- Tablet: 80% width, centered
- Desktop: 60% width, centered

**Questionnaire Steps**
- Mobile: Full screen, one question at a time
- Tablet: Centered card (600px max width)
- Desktop: Centered card (800px max width)

### Touch Optimization

**Tap Targets**
- Minimum: 44px × 44px (Apple HIG)
- Recommended: 48px × 48px (Material Design)
- Spacing: 8px minimum between targets

**Gestures**
- Swipe: Navigate between questionnaire steps
- Pull-to-refresh: Reload recommendations
- Pinch-to-zoom: Image galleries (disabled for UI)

**Feedback**
- Immediate visual feedback on tap
- Haptic feedback (where supported)
- Loading indicators within 100ms

## Performance Optimization

### Code Splitting

**Route-Based Splitting**
```typescript
const HomePage = lazy(() => import('@/pages/HomePage'))
const QuestionnairePage = lazy(() => import('@/pages/QuestionnairePage'))
const ResultsPage = lazy(() => import('@/pages/ResultsPage'))
```

**Component-Based Splitting**
```typescript
const CarDetailsModal = lazy(() => import('@/components/results/CarDetailsModal'))
```

### Lazy Loading

**Images**
- Use Intersection Observer
- Load images as they enter viewport
- Placeholder images until loaded
- Progressive image loading (blur-up)

**Components**
- Modal components loaded on demand
- Heavy components (charts, maps) lazy loaded

### Bundle Optimization

**Target Bundle Sizes**
- Initial bundle: < 200KB (gzipped)
- Total bundle: < 500KB (gzipped)
- Vendor bundle: < 150KB (gzipped)

**Strategies**
- Tree shaking (Vite automatic)
- Dynamic imports for routes
- Minimize Chakra UI imports (import specific components)
- Remove unused dependencies

### Caching Strategy

**React Query Cache**
- Recommendations: 5 minutes
- Stats: 10 minutes
- Dealerships: 30 minutes
- Stale-while-revalidate pattern

**Browser Cache**
- Static assets: 1 year (with hash)
- API responses: No cache (dynamic)
- Images: 1 week

**LocalStorage**
- User profile: Persist until cleared
- Filters: Session only
- Max size: 5MB


## Accessibility (WCAG AA)

### Semantic HTML

**Heading Hierarchy**
```html
<h1>FacilIAuto</h1>
  <h2>Encontre seu carro ideal</h2>
    <h3>Passo 1: Orçamento</h3>
    <h3>Passo 2: Uso</h3>
```

**Landmarks**
- `<header>` for page header
- `<nav>` for navigation
- `<main>` for main content
- `<aside>` for filters
- `<footer>` for page footer

### Keyboard Navigation

**Tab Order**
- Logical flow (top to bottom, left to right)
- Skip links for main content
- Focus trap in modals
- Escape key closes modals

**Focus Indicators**
- Visible outline (2px solid brand.500)
- High contrast (4.5:1 minimum)
- Not removed with CSS

### Screen Reader Support

**ARIA Labels**
```typescript
<button aria-label="Próximo passo">
  <Icon as={FiArrowRight} />
</button>
```

**ARIA Live Regions**
```typescript
<div role="status" aria-live="polite">
  {recommendations.length} carros encontrados
</div>
```

**Alt Text**
```typescript
<img 
  src={car.imagens[0]} 
  alt={`${car.marca} ${car.modelo} ${car.ano}`}
/>
```

### Color Contrast

**Text Contrast**
- Normal text: 4.5:1 minimum
- Large text (18px+): 3:1 minimum
- UI components: 3:1 minimum

**Color Palette**
- Primary (brand.500): #0ea5e9 on white = 4.52:1 ✅
- Text (gray.800): #1a202c on white = 16.1:1 ✅
- Error (red.500): #ef4444 on white = 4.5:1 ✅

### Form Accessibility

**Labels**
```typescript
<FormControl>
  <FormLabel htmlFor="budget-min">Orçamento mínimo</FormLabel>
  <Input id="budget-min" type="number" />
</FormControl>
```

**Error Messages**
```typescript
<FormControl isInvalid={!!error}>
  <Input aria-describedby="error-message" />
  <FormErrorMessage id="error-message">
    {error}
  </FormErrorMessage>
</FormControl>
```

## Testing Strategy

### Unit Tests (Vitest)

**Coverage Target**: 80%+

**Test Files**:
- `src/utils/*.test.ts` - Utility functions
- `src/hooks/*.test.ts` - Custom hooks
- `src/store/*.test.ts` - Zustand stores
- `src/services/*.test.ts` - API service layer

**Example Test**:
```typescript
describe('questionnaireStore', () => {
  it('should validate budget range', () => {
    const { result } = renderHook(() => useQuestionnaireStore())
    
    act(() => {
      result.current.updateFormData({
        orcamento_min: 50000,
        orcamento_max: 100000,
      })
    })
    
    expect(result.current.canGoNext()).toBe(true)
  })
})
```

### Component Tests (Testing Library)

**Coverage Target**: Key components only

**Test Files**:
- `src/components/common/*.test.tsx`
- `src/components/questionnaire/*.test.tsx`
- `src/components/results/*.test.tsx`

**Example Test**:
```typescript
describe('CarCard', () => {
  it('should display car information', () => {
    render(<CarCard car={mockCar} onClick={jest.fn()} />)
    
    expect(screen.getByText('Toyota Corolla')).toBeInTheDocument()
    expect(screen.getByText('R$ 85.000')).toBeInTheDocument()
    expect(screen.getByText('92%')).toBeInTheDocument()
  })
  
  it('should call onClick when clicked', () => {
    const onClick = jest.fn()
    render(<CarCard car={mockCar} onClick={onClick} />)
    
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledWith(mockCar)
  })
})
```

### E2E Tests (Cypress)

**Coverage Target**: Critical user flows

**Test Scenarios**:

1. **Complete Questionnaire Flow**
```typescript
describe('Questionnaire Flow', () => {
  it('should complete all steps and see recommendations', () => {
    cy.visit('/')
    cy.contains('Começar').click()
    
    // Step 1: Budget
    cy.get('[data-testid="budget-slider"]').setSliderValue(50000, 100000)
    cy.contains('Próximo').click()
    
    // Step 2: Usage
    cy.get('[data-testid="usage-familia"]').click()
    cy.contains('Próximo').click()
    
    // Step 3: Priorities
    cy.get('[data-testid="priority-economia"]').setSliderValue(5)
    cy.contains('Próximo').click()
    
    // Step 4: Location
    cy.get('[data-testid="city-input"]').type('São Paulo')
    cy.contains('Ver Recomendações').click()
    
    // Results
    cy.url().should('include', '/resultados')
    cy.get('[data-testid="car-card"]').should('have.length.greaterThan', 0)
  })
})
```

2. **Filter and Sort Results**
```typescript
describe('Results Filtering', () => {
  it('should filter cars by price range', () => {
    cy.visit('/resultados')
    
    cy.get('[data-testid="filter-price-min"]').type('60000')
    cy.get('[data-testid="filter-price-max"]').type('90000')
    
    cy.get('[data-testid="car-card"]').each(($card) => {
      const price = $card.find('[data-testid="car-price"]').text()
      const numPrice = parseInt(price.replace(/\D/g, ''))
      expect(numPrice).to.be.within(60000, 90000)
    })
  })
})
```

3. **WhatsApp Contact**
```typescript
describe('WhatsApp Integration', () => {
  it('should open WhatsApp with pre-filled message', () => {
    cy.visit('/resultados')
    
    cy.get('[data-testid="car-card"]').first().click()
    cy.get('[data-testid="whatsapp-button"]').should('be.visible')
    
    cy.get('[data-testid="whatsapp-button"]').then(($btn) => {
      const href = $btn.attr('href')
      expect(href).to.include('wa.me')
      expect(href).to.include('text=')
    })
  })
})
```

### Performance Tests

**Lighthouse Targets**:
- Performance: 90+
- Accessibility: 95+
- Best Practices: 90+
- SEO: 90+

**Core Web Vitals**:
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1


## Simplified Language Implementation

### Translation Dictionary

**Technical → Simplified**

| Technical Term | Simplified Language |
|---------------|---------------------|
| ISOFIX | Protege crianças com segurança |
| ESP (Electronic Stability Program) | Evita derrapagens |
| ABS (Anti-lock Braking System) | Freios mais seguros |
| Airbags | Proteção em acidentes |
| Torque | Força do motor |
| CV (Cavalos) | Potência |
| Suspensão independente | Conforto em estradas ruins |
| Câmbio automático | Troca marchas sozinho |
| Câmbio manual | Você troca as marchas |
| CVT | Troca suave de marchas |
| Flex | Usa gasolina ou álcool |
| Híbrido | Economiza combustível |
| Consumo urbano | Gasta na cidade |
| Consumo rodoviário | Gasta na estrada |

### Content Guidelines

**Questions (Questionnaire)**
- ❌ "Qual é o seu orçamento disponível para aquisição?"
- ✅ "Quanto você quer gastar?"

- ❌ "Selecione as características prioritárias do veículo"
- ✅ "O que é mais importante para você?"

**Justifications (Results)**
- ❌ "Este veículo possui score elevado em segurança devido aos 6 airbags e sistema ESP"
- ✅ "Perfeito para sua família! Tem proteção completa e evita derrapagens"

- ❌ "Consumo médio de 12 km/L no ciclo urbano"
- ✅ "Econômico: gasta pouco na cidade"

**Error Messages**
- ❌ "Error 500: Internal Server Error"
- ✅ "Ops! Algo deu errado. Tente novamente"

- ❌ "Invalid input: budget_min must be greater than 0"
- ✅ "Por favor, escolha um valor maior que zero"

**Tooltips**
- ❌ "ISOFIX: Sistema de fixação de cadeirinhas infantis"
- ✅ "Mantém a cadeirinha do bebê bem presa e segura"

### Tone of Voice

**Characteristics**:
- Informal (você, not senhor/senhora)
- Friendly and encouraging
- Simple and direct
- Positive and solution-oriented
- Grandmother-friendly (if she doesn't understand, it's too technical)

**Examples**:

**Welcome Message**
```
Olá! Vamos encontrar o carro perfeito para você.
São só 4 perguntas rápidas. Vamos lá?
```

**Step Completion**
```
Ótimo! Agora me conta: como você vai usar o carro?
```

**Results Header**
```
Encontramos 12 carros perfeitos para você! 🎉
```

**Empty State**
```
Hmm, não encontramos carros com esses filtros.
Que tal ajustar um pouco? 😊
```

## WhatsApp Integration

### Message Template

**Structure**:
```
Olá! Vi o {car_name} no FacilIAuto e tenho interesse.

📊 Compatibilidade: {match_score}%
💰 Preço: R$ {price}

Meu nome é {user_name} e gostaria de mais informações.

Quando posso visitar a loja?
```

**Example**:
```
Olá! Vi o Toyota Corolla 2023 no FacilIAuto e tenho interesse.

📊 Compatibilidade: 92%
💰 Preço: R$ 85.000

Meu nome é João Silva e gostaria de mais informações.

Quando posso visitar a loja?
```

### Implementation

**URL Format**:
```typescript
const whatsappUrl = `https://wa.me/${dealership.whatsapp}?text=${encodeURIComponent(message)}`
```

**Tracking**:
```typescript
// Track interaction before opening WhatsApp
await trackInteraction({
  event_type: 'contact_initiated',
  car_id: car.id,
  dealership_id: car.dealership_id,
  match_score: recommendation.match_score,
  timestamp: new Date().toISOString(),
})

// Open WhatsApp
window.open(whatsappUrl, '_blank')
```

### Fallback Strategy

**If WhatsApp number not available**:
1. Display phone number with "Ligar" button
2. Display email with "Enviar email" button
3. Display dealership address with "Ver no mapa" button

## Deployment Considerations

### Build Configuration

**Production Build**:
```bash
npm run build
```

**Output**:
- `dist/` directory
- Optimized bundles
- Source maps (for debugging)
- Asset hashing (for cache busting)

### Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_VERSION=1.0.0
VITE_ENABLE_ANALYTICS=false
```

### Hosting Requirements

**Static Hosting** (Vercel, Netlify, AWS S3 + CloudFront):
- Serve `index.html` for all routes (SPA routing)
- Enable gzip/brotli compression
- Set cache headers (1 year for assets, no-cache for index.html)
- HTTPS required

**CDN Configuration**:
- Cache static assets (JS, CSS, images)
- Don't cache index.html
- Enable HTTP/2
- Enable compression

### Monitoring

**Error Tracking** (Future):
- Sentry or similar
- Track unhandled errors
- Track API errors
- User session replay

**Analytics** (Future):
- Google Analytics or similar
- Track page views
- Track conversions (questionnaire completion, WhatsApp clicks)
- Track user flows

**Performance Monitoring**:
- Lighthouse CI in GitHub Actions
- Core Web Vitals tracking
- Bundle size monitoring

## Design Decisions and Rationales

### Why Zustand over Redux?
- Simpler API (less boilerplate)
- Better TypeScript support
- Smaller bundle size (3KB vs 45KB)
- Sufficient for our use case (no complex middleware needed)

### Why React Query over manual state?
- Automatic caching and refetching
- Built-in loading and error states
- Optimistic updates support
- Reduces boilerplate significantly

### Why Chakra UI over Material-UI?
- Better mobile-first defaults
- More customizable theme
- Smaller bundle size
- Better accessibility out-of-the-box

### Why Vite over Create React App?
- Faster dev server (instant HMR)
- Faster builds (esbuild)
- Better tree shaking
- Modern tooling (ESM-first)

### Why client-side filtering over API calls?
- Faster user experience (no network latency)
- Reduces backend load
- Recommendations already loaded
- Typical result set size (20-50 cars) is manageable

### Why localStorage over sessionStorage?
- Better UX (persist across sessions)
- User can close tab and return later
- No sensitive data stored (just preferences)
- Easy to clear if needed

## Future Enhancements (Post-MVP)

**Phase 2 Features**:
- User accounts and saved searches
- Comparison tool (compare up to 3 cars)
- Financing calculator
- Test drive scheduling
- Favorite cars list

**Phase 3 Features**:
- Advanced filters (features, colors, etc.)
- Map view of dealerships
- Virtual tour (360° car views)
- Chat with dealership
- Push notifications

**Technical Improvements**:
- Progressive Web App (PWA)
- Offline support
- Push notifications
- Background sync
- Install prompt

