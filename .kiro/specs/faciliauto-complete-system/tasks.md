# Implementation Plan - FacilIAuto Complete System

Este plano de implementação detalha as tarefas necessárias para completar o sistema FacilIAuto de 84% para 100%. Cada task é focada em código e pode ser executada por um agente de desenvolvimento.

## Task Overview

- **Total Tasks:** 45 tasks organizadas em 5 fases
- **Estimated Time:** 15 dias úteis (3 semanas)
- **Current Status:** Backend 97%, Frontend 40%, Overall 84%
- **Target Status:** 100% completo e production-ready

---

## Phase 1: Frontend Pages Implementation

### 1. HomePage Implementation

- [ ] 1.1 Implement HeroSection component
  - Create HeroSection.tsx with headline, subheadline, and CTA button
  - Add responsive layout (mobile: stacked, desktop: side-by-side)
  - Implement navigation to /questionario on CTA click
  - Add unit tests for rendering and navigation
  - _Requirements: 1.1, 1.2, 10.1, 10.2, 10.3_

- [ ] 1.2 Implement FeaturesGrid component
  - Create FeaturesGrid.tsx with 3-4 feature cards
  - Use Chakra UI Grid for responsive layout
  - Add icons and descriptions for each feature
  - Implement hover effects
  - Add unit tests for rendering
  - _Requirements: 1.1, 10.1, 10.2, 10.3_

- [ ] 1.3 Implement SocialProof component
  - Create SocialProof.tsx with testimonials or logos
  - Add carousel or grid layout
  - Ensure mobile responsiveness
  - Add unit tests
  - _Requirements: 1.1, 10.1, 10.2, 10.3_

- [ ] 1.4 Implement PricingPreview component
  - Create PricingPreview.tsx with pricing tiers
  - Display 3 plans (Free, Premium, Enterprise)
  - Add "Começar" buttons for each plan
  - Add unit tests
  - _Requirements: 1.1, 10.1, 10.2, 10.3_

- [ ] 1.5 Implement Footer component
  - Create Footer.tsx with links and contact info
  - Add social media icons
  - Ensure responsive layout
  - Add unit tests
  - _Requirements: 1.1, 10.1, 10.2, 10.3_

- [ ] 1.6 Assemble HomePage with all components
  - Import and compose all sub-components in HomePage.tsx
  - Ensure smooth scrolling between sections
  - Test navigation flow
  - Add integration tests
  - _Requirements: 1.1, 1.2, 10.1, 10.2, 10.3_

### 2. QuestionnairePage - Step Components

- [ ] 2.1 Implement StepIndicator component
  - Create StepIndicator.tsx showing current step (1/4, 2/4, etc.)
  - Add visual progress bar
  - Highlight current step
  - Add unit tests
  - _Requirements: 1.3, 1.4, 5.1_

- [ ] 2.2 Implement BudgetStep component (Step 0)
  - Create BudgetStep.tsx with two number inputs (min/max)
  - Add validation: min < max, both > 0
  - Display error messages inline
  - Format currency display (R$)
  - Add unit tests for validation logic
  - _Requirements: 1.3, 1.4, 8.4, 9.4_

- [ ] 2.3 Implement UsageStep component (Step 1)
  - Create UsageStep.tsx with dropdown for uso_principal
  - Add number input for tamanho_familia
  - Add validation for required fields
  - Add unit tests
  - _Requirements: 1.3, 1.4, 8.4, 9.4_

- [ ] 2.4 Implement PrioritiesStep component (Step 2)
  - Create PrioritiesStep.tsx with 4 sliders (economia, espaco, performance, tecnologia)
  - Use Chakra UI Slider components
  - Set range 1-5 for each slider
  - Display current value above each slider
  - Add unit tests
  - _Requirements: 1.3, 1.4, 5.2_

- [ ] 2.5 Implement PreferencesStep component (Step 3)
  - Create PreferencesStep.tsx with checkboxes for marcas_preferidas
  - Add color selection (optional)
  - Add transmissao radio buttons (manual/automatica/ambas)
  - Add unit tests
  - _Requirements: 1.3, 1.4, 8.4_

### 3. QuestionnairePage - State Management

- [ ] 3.1 Implement questionnaireStore with Zustand
  - Create questionnaireStore.ts with state interface
  - Implement actions: setStep, updateFormData, validateStep, submitQuestionnaire, reset
  - Add validation logic for each step
  - Write unit tests for store actions
  - _Requirements: 1.4, 8.1, 8.2, 8.3_

- [ ] 3.2 Implement useQuestionnaire custom hook
  - Create useQuestionnaire.ts hook
  - Connect to questionnaireStore
  - Implement nextStep, prevStep, submitForm functions
  - Add navigation logic
  - Write unit tests for hook
  - _Requirements: 1.4, 8.1, 8.2_

- [ ] 3.3 Implement NavigationButtons component
  - Create NavigationButtons.tsx with Anterior/Próximo/Submeter buttons
  - Disable buttons based on validation state
  - Show loading state during submission
  - Add unit tests
  - _Requirements: 1.4, 9.6_

- [ ] 3.4 Assemble QuestionnairePage with all steps
  - Import all step components in QuestionnairePage.tsx
  - Implement step switching logic
  - Connect to useQuestionnaire hook
  - Add integration tests for full flow
  - _Requirements: 1.3, 1.4, 1.5_

### 4. ResultsPage Implementation

- [ ] 4.1 Implement CarCard component
  - Create CarCard.tsx displaying car photo, name, price, score
  - Add WhatsApp button with click handler
  - Format price as R$ XX.XXX
  - Add hover effects
  - Write unit tests
  - _Requirements: 1.6, 5.3_

- [ ] 4.2 Implement ScoreVisual component
  - Create ScoreVisual.tsx with circular progress or bar
  - Color code: 0-50 red, 51-70 yellow, 71-100 green
  - Support sizes: sm, md, lg
  - Add unit tests
  - _Requirements: 1.6, 5.3_

- [ ] 4.3 Implement FilterBar component
  - Create FilterBar.tsx with filters for marca, price range, year
  - Update filters state on change
  - Add "Limpar Filtros" button
  - Write unit tests
  - _Requirements: 1.6_

- [ ] 4.4 Implement SortControls component
  - Create SortControls.tsx with dropdown for sorting (score, price, year)
  - Update sort state on change
  - Add unit tests
  - _Requirements: 1.6_

- [ ] 4.5 Implement useRecommendations custom hook
  - Create useRecommendations.ts hook
  - Get recommendations from location state
  - Implement filtering logic
  - Implement sorting logic
  - Write unit tests
  - _Requirements: 1.6_

- [ ] 4.6 Assemble ResultsPage with all components
  - Import all components in ResultsPage.tsx
  - Connect to useRecommendations hook
  - Handle loading and error states
  - Add "Nova Busca" button
  - Add integration tests
  - _Requirements: 1.6, 1.8, 1.9_

---

## Phase 2: API Integration

### 5. API Service Layer

- [ ] 5.1 Implement base API client with axios
  - Create api.ts with axios instance
  - Configure base URL from environment variable
  - Set timeout to 10 seconds
  - Add request/response interceptors for logging
  - Write unit tests with mocked axios
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 5.2 Implement error handling in API client
  - Create custom error classes (ValidationError, ServerError, NetworkError)
  - Add response interceptor for error handling
  - Handle 422 (validation), 500+ (server), network errors
  - Write unit tests for each error type
  - _Requirements: 2.5, 9.1, 9.2, 9.3_

- [ ] 5.3 Implement API endpoint functions
  - Add health() function for GET /health
  - Add stats() function for GET /stats
  - Add recommend() function for POST /recommend
  - Add dealerships() function for GET /dealerships
  - Add cars() function for GET /cars with query params
  - Write unit tests for all functions
  - _Requirements: 2.2, 2.3, 2.4_

- [ ] 5.4 Implement retry logic with exponential backoff
  - Add retry interceptor to axios instance
  - Implement exponential backoff (1s, 2s, 4s)
  - Retry only on network errors and 5xx
  - Add max retry limit (3 attempts)
  - Write unit tests
  - _Requirements: 2.6, 2.7, 9.9_

### 6. React Query Integration

- [ ] 6.1 Set up React Query QueryClient
  - Install @tanstack/react-query
  - Create QueryClient with default options
  - Wrap App with QueryClientProvider
  - Configure staleTime and cacheTime
  - _Requirements: 2.8, 6.5_

- [ ] 6.2 Implement useApi hook
  - Create useApi.ts with queries for health and stats
  - Use useQuery for GET endpoints
  - Configure appropriate staleTime
  - Write unit tests
  - _Requirements: 2.2, 2.3, 6.5_

- [ ] 6.3 Implement recommendation mutation in useQuestionnaire
  - Add useMutation for POST /recommend in useQuestionnaire hook
  - Handle onSuccess: navigate to /resultados with data
  - Handle onError: display error message
  - Update submitForm to use mutation
  - Write unit tests
  - _Requirements: 1.5, 2.4, 2.8_

- [ ] 6.4 Add loading and error states to components
  - Update QuestionnairePage to show loading during submission
  - Update ResultsPage to handle loading state
  - Display error messages using ErrorMessage component
  - Add retry buttons where appropriate
  - _Requirements: 1.8, 1.9, 9.1, 9.2, 9.3, 9.6_

### 7. CORS and Backend Configuration

- [ ] 7.1 Configure CORS in backend
  - Update backend/api/main.py to allow localhost:3000 and localhost:5173
  - Add appropriate CORS headers
  - Test CORS with frontend requests
  - _Requirements: 2.1_

- [ ] 7.2 Test all API endpoints from frontend
  - Manually test GET /health from frontend
  - Manually test GET /stats from frontend
  - Manually test POST /recommend with valid data
  - Manually test error scenarios (invalid data, offline)
  - Document any issues found
  - _Requirements: 2.2, 2.3, 2.4, 2.5_

- [ ] 7.3 Fix integration issues
  - Address any CORS issues found
  - Fix data format mismatches
  - Ensure error responses are handled correctly
  - Validate end-to-end data flow
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

---

## Phase 3: Testing Implementation

### 8. Unit Tests

- [ ] 8.1 Write unit tests for HomePage components
  - Test HeroSection rendering and CTA click
  - Test FeaturesGrid rendering
  - Test SocialProof rendering
  - Test PricingPreview rendering
  - Test Footer rendering
  - Achieve 80%+ coverage for HomePage
  - _Requirements: 8.2, 8.6_

- [ ] 8.2 Write unit tests for QuestionnairePage components
  - Test StepIndicator with different steps
  - Test BudgetStep validation logic
  - Test UsageStep rendering and validation
  - Test PrioritiesStep slider interactions
  - Test PreferencesStep checkbox interactions
  - Test NavigationButtons enable/disable logic
  - Achieve 80%+ coverage for QuestionnairePage
  - _Requirements: 8.2, 8.3, 8.6_

- [ ] 8.3 Write unit tests for ResultsPage components
  - Test CarCard rendering with mock data
  - Test ScoreVisual with different scores
  - Test FilterBar filter changes
  - Test SortControls sort changes
  - Test ResultsPage with empty results
  - Achieve 80%+ coverage for ResultsPage
  - _Requirements: 8.2, 8.6_

- [ ] 8.4 Write unit tests for custom hooks
  - Test useQuestionnaire step navigation
  - Test useQuestionnaire validation
  - Test useQuestionnaire form submission
  - Test useRecommendations filtering
  - Test useRecommendations sorting
  - Test useApi queries
  - _Requirements: 8.3, 8.6_

- [ ] 8.5 Write unit tests for API service
  - Test api.health() call
  - Test api.stats() call
  - Test api.recommend() with valid data
  - Test error handling for 422, 500, network errors
  - Test retry logic
  - _Requirements: 8.3, 8.6_

- [ ] 8.6 Write unit tests for Zustand store
  - Test questionnaireStore initial state
  - Test setStep action
  - Test updateFormData action
  - Test validateStep for each step
  - Test reset action
  - _Requirements: 8.1, 8.2, 8.6_

### 9. E2E Tests with Cypress

- [ ] 9.1 Set up Cypress configuration
  - Ensure Cypress is installed
  - Configure baseUrl to localhost:3000
  - Set up test data fixtures
  - Configure viewport sizes
  - _Requirements: 3.6_

- [ ] 9.2 Write E2E test for complete user journey
  - Test: Visit homepage → Click CTA → Fill all 4 steps → View results
  - Verify each step renders correctly
  - Verify navigation between steps
  - Verify results page displays recommendations
  - _Requirements: 3.1, 3.6_

- [ ] 9.3 Write E2E tests for form validation
  - Test: Invalid budget (min > max) shows error
  - Test: Empty required fields show errors
  - Test: Cannot advance step with invalid data
  - Test: Error messages are displayed correctly
  - _Requirements: 3.2, 3.3, 3.4_

- [ ] 9.4 Write E2E tests for error handling
  - Test: API offline shows network error message
  - Test: Server error (500) shows appropriate message
  - Test: No results found shows empty state
  - Test: Retry button works after error
  - _Requirements: 3.4, 3.5, 3.7_

- [ ] 9.5 Write E2E tests for navigation
  - Test: Back button preserves form data
  - Test: Forward navigation validates current step
  - Test: Direct URL navigation works
  - Test: "Nova Busca" button resets form
  - _Requirements: 3.1_

- [ ] 9.6 Write E2E tests for responsive design
  - Test: Mobile viewport (375px) renders correctly
  - Test: Tablet viewport (768px) renders correctly
  - Test: Desktop viewport (1920px) renders correctly
  - Test: All interactions work on mobile
  - _Requirements: 3.6, 10.1, 10.2, 10.3_

- [ ] 9.7 Ensure 15+ E2E tests are passing
  - Run all Cypress tests
  - Fix any failing tests
  - Verify coverage of critical user journeys
  - Document test results
  - _Requirements: 3.6_

---

## Phase 4: Polish and Optimization

### 10. UX Improvements

- [ ] 10.1 Add loading states to all async operations
  - Add LoadingSpinner component
  - Show spinner during API calls
  - Show skeleton loaders for car cards
  - Disable buttons during loading
  - _Requirements: 1.9, 9.6_

- [ ] 10.2 Improve error messages and user feedback
  - Create ErrorMessage component with variants (inline, toast, page)
  - Add toast notifications for success/error
  - Improve validation error messages
  - Add helpful hints for form fields
  - _Requirements: 1.8, 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 10.3 Add animations and transitions
  - Add page transition animations with Framer Motion
  - Add hover effects to buttons and cards
  - Add smooth scrolling
  - Add fade-in animations for results
  - _Requirements: 6.4_

- [ ] 10.4 Implement accessibility features
  - Add aria-labels to all interactive elements
  - Ensure keyboard navigation works (tab order)
  - Add focus states to all focusable elements
  - Test with screen reader
  - Verify color contrast ratios (4.5:1 minimum)
  - _Requirements: 10.4, 10.5, 10.6, 10.7_

### 11. Performance Optimization

- [ ] 11.1 Implement lazy loading for routes
  - Use React.lazy() for HomePage, QuestionnairePage, ResultsPage
  - Add Suspense with loading fallback
  - Test that routes load on demand
  - _Requirements: 6.3_

- [ ] 11.2 Implement code splitting
  - Configure Vite for automatic code splitting
  - Split vendor bundles
  - Verify bundle sizes with vite-bundle-visualizer
  - Ensure main bundle < 500KB gzipped
  - _Requirements: 6.3, 6.7_

- [ ] 11.3 Optimize images
  - Compress all images
  - Use WebP format where supported
  - Add lazy loading to images
  - Implement responsive images with srcset
  - _Requirements: 6.6_

- [ ] 11.4 Run Lighthouse audit and optimize
  - Run Lighthouse on all pages
  - Fix performance issues identified
  - Achieve score > 90 for Performance
  - Achieve score > 90 for Accessibility
  - Achieve score > 90 for Best Practices
  - _Requirements: 6.1, 6.2_

### 12. Code Quality

- [ ] 12.1 Refactor duplicated code
  - Identify code duplication with ESLint
  - Extract common logic into utility functions
  - Create reusable components where appropriate
  - Apply DRY principle
  - _Requirements: 7.2_

- [ ] 12.2 Improve type safety
  - Ensure all components have proper TypeScript types
  - Add types for all API responses
  - Fix any 'any' types
  - Enable strict mode in tsconfig.json
  - _Requirements: 7.1, 7.6_

- [ ] 12.3 Add missing tests to reach 80% coverage
  - Run coverage report
  - Identify uncovered code
  - Write tests for uncovered branches
  - Achieve 80%+ coverage overall
  - _Requirements: 8.5, 8.6_

- [ ] 12.4 Code review and cleanup
  - Remove commented code
  - Remove unused imports
  - Fix ESLint warnings
  - Format code with Prettier
  - Add missing JSDoc comments
  - _Requirements: 7.3, 7.4, 7.5_

---

## Phase 5: Documentation and Deployment

### 13. Startup Scripts

- [ ] 13.1 Create and test start-faciliauto.bat for Windows
  - Write batch script to check Python and Node.js
  - Add logic to check if ports 8000 and 3000 are available
  - Start backend in separate terminal
  - Start frontend in separate terminal
  - Display URLs and instructions
  - Test script on Windows machine
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.8_

- [ ] 13.2 Create and test start-faciliauto.sh for Linux/Mac
  - Write bash script to check Python and Node.js
  - Add logic to check if ports are available
  - Start backend and frontend processes
  - Implement graceful shutdown on Ctrl+C
  - Display URLs and instructions
  - Test script on Linux/Mac machine
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [ ] 13.3 Create troubleshooting guide for startup scripts
  - Document common errors (port in use, missing dependencies)
  - Add solutions for each error
  - Include commands to check Python/Node versions
  - Add instructions to kill processes on ports
  - _Requirements: 4.8_

### 14. Documentation Updates

- [ ] 14.1 Update README.md with accurate status
  - Update scores: Backend 97%, Frontend 100%, Overall 100%
  - Update "Como Executar" section with tested commands
  - Add troubleshooting section
  - Update feature list to reflect completed work
  - _Requirements: 7.1, 7.2, 7.5_

- [ ] 14.2 Create COMO-EXECUTAR.md guide
  - Write step-by-step guide for running the system
  - Include prerequisites (Python, Node.js versions)
  - Add commands for Windows and Linux/Mac
  - Include screenshots or examples
  - Add troubleshooting section
  - _Requirements: 7.3_

- [ ] 14.3 Update STATUS-REAL-ATUAL.md
  - Update all scores to 100%
  - Mark all gaps as resolved
  - Update "O Que Está Pronto" section
  - Remove "O Que Falta" section
  - Add "Conquistas" section
  - _Requirements: 7.2, 7.4_

- [ ] 14.4 Create CHANGELOG.md
  - Document all changes made during implementation
  - Use semantic versioning format
  - Group changes by type (Added, Changed, Fixed)
  - Include dates for each version
  - _Requirements: 7.7_

- [ ] 14.5 Document API integration
  - Create API-INTEGRATION.md guide
  - Document all API endpoints used
  - Include request/response examples
  - Document error handling
  - Add code examples
  - _Requirements: 7.6_

### 15. Deployment Preparation

- [ ] 15.1 Test Docker setup
  - Run docker-compose up in platform/backend
  - Verify all services start correctly
  - Test health checks
  - Verify Grafana dashboards load
  - Document any issues
  - _Requirements: 11.1, 11.2_

- [ ] 15.2 Configure environment variables
  - Create .env.example files for frontend and backend
  - Document all required environment variables
  - Add descriptions for each variable
  - Test with different configurations
  - _Requirements: 11.3_

- [ ] 15.3 Set up CI/CD pipeline
  - Configure GitHub Actions workflow
  - Add jobs for backend tests
  - Add jobs for frontend tests
  - Add jobs for E2E tests
  - Add build and deploy jobs
  - Test pipeline with a commit
  - _Requirements: 11.5_

- [ ] 15.4 Configure monitoring
  - Verify Prometheus is collecting metrics
  - Create Grafana dashboards for key metrics
  - Set up alerts for errors and downtime
  - Test monitoring with sample data
  - _Requirements: 11.7_

- [ ] 15.5 Create deployment checklist
  - List all pre-deployment checks
  - Include testing checklist
  - Add rollback procedures
  - Document deployment steps
  - _Requirements: 11.6_

- [ ] 15.6 Final system validation
  - Run all tests (unit, integration, E2E)
  - Verify all features work end-to-end
  - Test on multiple browsers
  - Test on mobile devices
  - Verify performance metrics
  - Confirm 100% completion
  - _Requirements: All requirements_

