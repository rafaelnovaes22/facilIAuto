# Requirements Document

## Introduction

This specification defines the requirements for completing the FacilIAuto frontend from its current 40% state to a production-ready MVP (90%+) within 2-3 weeks. The frontend must deliver the superior mobile-first UX that is our primary competitive differentiator, enabling us to maintain our 6-12 month market advantage.

The system must provide a complete, demonstrable user journey from landing page through questionnaire to personalized car recommendations, with full backend integration and mobile-optimized experience.

## Glossary

- **FacilIAuto Frontend**: React + TypeScript single-page application providing the user interface for car recommendations
- **Questionnaire Flow**: 4-step mobile-optimized user profiling process (Budget → Usage → Priorities → Location)
- **Results Page**: Display of personalized car recommendations with filtering, sorting, and detailed views
- **Mobile-First**: Design approach where mobile experience is primary, desktop is enhancement
- **Backend API**: FastAPI service at localhost:8000 providing recommendations and data
- **Chakra UI**: Component library used for consistent, accessible UI components
- **User Profile**: Collection of user preferences (budget, usage, priorities, location) used for recommendations
- **Car Card**: Visual component displaying car summary (image, name, price, score, key features)
- **Recommendation Score**: 0.0-1.0 value indicating car match quality based on user profile
- **WhatsApp Integration**: Direct contact mechanism linking users to dealerships via WhatsApp
- **Simplified Language**: Non-technical, grandmother-friendly terminology for all user-facing content

## Requirements

### Requirement 1: Complete Questionnaire Flow

**User Story:** As a potential car buyer, I want to complete a simple 4-step questionnaire on my mobile phone, so that I can receive personalized car recommendations without needing technical knowledge.

#### Acceptance Criteria

1. WHEN the user accesses the questionnaire, THE FacilIAuto Frontend SHALL display Step 1 (Budget) with clear budget range options (R$ 30k-200k+) in a mobile-optimized layout
2. WHEN the user selects a budget range, THE FacilIAuto Frontend SHALL validate the selection and enable navigation to Step 2 (Usage)
3. WHEN the user is on Step 2, THE FacilIAuto Frontend SHALL display 6 usage profile options (Família, Trabalho, Lazer, Comercial, Primeiro Carro, Transporte Passageiros) with simplified descriptions
4. WHEN the user selects a usage profile, THE FacilIAuto Frontend SHALL display Step 3 (Priorities) with 5 priority sliders (Economia, Espaço, Performance, Conforto, Segurança) defaulted to profile-specific values
5. WHEN the user adjusts priority sliders, THE FacilIAuto Frontend SHALL update values in real-time and highlight the top 3 priorities visually
6. WHEN the user completes Step 3, THE FacilIAuto Frontend SHALL display Step 4 (Location) with city/state selection and optional distance radius
7. WHEN the user completes all 4 steps, THE FacilIAuto Frontend SHALL enable the "Ver Recomendações" button and store the complete user profile
8. WHILE the user is in the questionnaire, THE FacilIAuto Frontend SHALL display progress indicators showing current step (1/4, 2/4, 3/4, 4/4)
9. WHEN the user navigates between steps, THE FacilIAuto Frontend SHALL preserve previously entered data
10. IF the user attempts to proceed without completing required fields, THEN THE FacilIAuto Frontend SHALL display clear validation messages in simplified language

### Requirement 2: Results Page with Recommendations

**User Story:** As a user who completed the questionnaire, I want to see personalized car recommendations with clear explanations, so that I can understand why each car matches my needs.

#### Acceptance Criteria

1. WHEN the user submits the questionnaire, THE FacilIAuto Frontend SHALL call the Backend API POST /recommend endpoint with the complete user profile
2. WHEN the Backend API returns recommendations, THE FacilIAuto Frontend SHALL display cars in a mobile-optimized grid layout with Car Cards
3. WHEN displaying each Car Card, THE FacilIAuto Frontend SHALL show car image, name, price, recommendation score (0-100%), and top 3 matching features
4. WHEN the user taps a Car Card, THE FacilIAuto Frontend SHALL open a detailed modal with full car specifications, justification text, and contact options
5. WHILE displaying recommendations, THE FacilIAuto Frontend SHALL show the user's top 3 priorities prominently at the top of the page
6. WHEN the user applies filters (price range, category, dealership), THE FacilIAuto Frontend SHALL update the displayed cars in real-time without page reload
7. WHEN the user changes sort order (score, price, year), THE FacilIAuto Frontend SHALL reorder cars immediately with smooth animation
8. WHEN no cars match the current filters, THE FacilIAuto Frontend SHALL display a helpful message suggesting filter adjustments
9. WHEN the user scrolls the results page, THE FacilIAuto Frontend SHALL implement infinite scroll or pagination for performance with 20+ cars
10. IF the Backend API call fails, THEN THE FacilIAuto Frontend SHALL display a user-friendly error message with retry option

### Requirement 3: Mobile-First Responsive Design

**User Story:** As a mobile user, I want the entire application to work perfectly on my smartphone, so that I can find my ideal car while on the go.

#### Acceptance Criteria

1. THE FacilIAuto Frontend SHALL render all pages with mobile viewport (320px-428px) as the primary design target
2. WHEN the user accesses any page on mobile, THE FacilIAuto Frontend SHALL display touch-optimized controls with minimum 44px tap targets
3. WHEN the user interacts with forms, THE FacilIAuto Frontend SHALL use appropriate mobile keyboards (numeric for budget, text for location)
4. WHEN the user views the questionnaire on mobile, THE FacilIAuto Frontend SHALL display one question per screen with clear navigation
5. WHEN the user views results on mobile, THE FacilIAuto Frontend SHALL display one car per row in a vertical scrolling layout
6. WHEN the user accesses the site on tablet (768px-1024px), THE FacilIAuto Frontend SHALL adapt to 2-column layouts where appropriate
7. WHEN the user accesses the site on desktop (1024px+), THE FacilIAuto Frontend SHALL enhance the layout with multi-column grids while maintaining mobile-first principles
8. WHEN the user rotates their device, THE FacilIAuto Frontend SHALL adapt the layout smoothly without losing state
9. WHILE the user interacts with any component, THE FacilIAuto Frontend SHALL provide immediate visual feedback (loading states, hover effects, active states)
10. THE FacilIAuto Frontend SHALL load the initial page in under 2 seconds on 3G mobile connections

### Requirement 4: Backend Integration and Error Handling

**User Story:** As a user, I want the application to work reliably and handle problems gracefully, so that I have a smooth experience even when issues occur.

#### Acceptance Criteria

1. WHEN the FacilIAuto Frontend starts, THE FacilIAuto Frontend SHALL verify Backend API availability by calling GET /health endpoint
2. IF the Backend API is unavailable at startup, THEN THE FacilIAuto Frontend SHALL display a maintenance message with retry option
3. WHEN making any Backend API call, THE FacilIAuto Frontend SHALL include proper error handling with timeout (10 seconds)
4. WHEN a Backend API call times out, THE FacilIAuto Frontend SHALL display a user-friendly error message and log technical details to console
5. WHEN the Backend API returns validation errors, THE FacilIAuto Frontend SHALL display field-specific error messages in simplified language
6. WHEN the Backend API returns 500 errors, THE FacilIAuto Frontend SHALL display a generic error message without exposing technical details
7. WHEN network connectivity is lost, THE FacilIAuto Frontend SHALL detect the condition and display an offline message
8. WHEN network connectivity is restored, THE FacilIAuto Frontend SHALL automatically retry the last failed request
9. WHILE waiting for Backend API responses, THE FacilIAuto Frontend SHALL display loading indicators (spinners, skeleton screens) appropriate to the context
10. WHEN the user submits the questionnaire, THE FacilIAuto Frontend SHALL track the interaction via POST /api/interactions/track for ML data collection

### Requirement 5: WhatsApp Contact Integration

**User Story:** As a user interested in a car, I want to contact the dealership directly via WhatsApp, so that I can get more information and schedule a visit easily.

#### Acceptance Criteria

1. WHEN the user views a car's detailed modal, THE FacilIAuto Frontend SHALL display a prominent "Falar no WhatsApp" button
2. WHEN the user taps the WhatsApp button, THE FacilIAuto Frontend SHALL construct a pre-filled WhatsApp message including car name, user name, and interest statement
3. WHEN opening WhatsApp, THE FacilIAuto Frontend SHALL use the dealership's WhatsApp number from the car data
4. WHEN the WhatsApp link is generated, THE FacilIAuto Frontend SHALL use the wa.me URL format for cross-platform compatibility
5. WHEN the user taps the WhatsApp button, THE FacilIAuto Frontend SHALL track the interaction as a "contact_initiated" event via Backend API
6. IF the car data does not include a WhatsApp number, THEN THE FacilIAuto Frontend SHALL display an alternative contact method (phone, email)
7. WHEN the WhatsApp message is pre-filled, THE FacilIAuto Frontend SHALL include the recommendation score to help the dealership understand match quality
8. WHEN opening WhatsApp on mobile, THE FacilIAuto Frontend SHALL use the native WhatsApp app if installed, otherwise web.whatsapp.com
9. WHEN the user contacts multiple dealerships, THE FacilIAuto Frontend SHALL track each contact separately for analytics
10. THE FacilIAuto Frontend SHALL format the WhatsApp message in simplified language matching the application's tone

### Requirement 6: Simplified Language Implementation

**User Story:** As a non-technical user, I want all text in the application to be in simple everyday language, so that I can understand everything without car expertise.

#### Acceptance Criteria

1. THE FacilIAuto Frontend SHALL display all user-facing text using simplified, non-technical language as defined in the Glossary
2. WHEN displaying car features, THE FacilIAuto Frontend SHALL translate technical terms to benefits (e.g., "ISOFIX" → "Protege crianças", "ESP" → "Evita derrapagens")
3. WHEN showing priority labels, THE FacilIAuto Frontend SHALL use everyday terms (Economia, Espaço, Performance, Conforto, Segurança) without technical jargon
4. WHEN displaying justification text, THE FacilIAuto Frontend SHALL explain why a car matches using situation-based language (e.g., "Perfeito para levar a família" not "Alto score em segurança")
5. WHEN showing error messages, THE FacilIAuto Frontend SHALL use friendly, helpful language (e.g., "Ops! Algo deu errado" not "Error 500: Internal Server Error")
6. WHEN displaying tooltips or help text, THE FacilIAuto Frontend SHALL provide visual examples or analogies instead of technical definitions
7. THE FacilIAuto Frontend SHALL avoid acronyms (ABS, ESP, ISOFIX) in all user-facing text
8. THE FacilIAuto Frontend SHALL avoid automotive jargon (torque, cv, suspension types, transmission types) in all user-facing text
9. WHEN displaying numerical values, THE FacilIAuto Frontend SHALL use Brazilian Portuguese formatting (R$ 50.000,00 not $50,000.00)
10. THE FacilIAuto Frontend SHALL use informal, friendly tone throughout (você, not senhor/senhora)

### Requirement 7: State Management and Navigation

**User Story:** As a user, I want to navigate through the application smoothly with my data preserved, so that I don't lose my progress or have to re-enter information.

#### Acceptance Criteria

1. WHEN the user enters data in the questionnaire, THE FacilIAuto Frontend SHALL store the data in Zustand state management
2. WHEN the user navigates between questionnaire steps, THE FacilIAuto Frontend SHALL preserve all previously entered data
3. WHEN the user completes the questionnaire and views results, THE FacilIAuto Frontend SHALL maintain the user profile in state
4. WHEN the user applies filters on the results page, THE FacilIAuto Frontend SHALL update the URL query parameters to enable sharing and bookmarking
5. WHEN the user refreshes the results page, THE FacilIAuto Frontend SHALL restore filters and user profile from URL parameters or localStorage
6. WHEN the user navigates back from results to questionnaire, THE FacilIAuto Frontend SHALL preserve the previous answers for editing
7. WHEN the user starts a new search from results page, THE FacilIAuto Frontend SHALL clear previous results and reset to questionnaire Step 1
8. WHILE the user navigates, THE FacilIAuto Frontend SHALL use React Router for client-side routing without full page reloads
9. WHEN the user uses browser back/forward buttons, THE FacilIAuto Frontend SHALL navigate correctly through the application flow
10. THE FacilIAuto Frontend SHALL persist critical user data (profile, filters) to localStorage to survive page refreshes

### Requirement 8: Performance and Loading States

**User Story:** As a user, I want the application to feel fast and responsive, so that I have a smooth experience without frustrating delays.

#### Acceptance Criteria

1. WHEN the FacilIAuto Frontend loads initially, THE FacilIAuto Frontend SHALL display the landing page within 2 seconds on 3G connections
2. WHEN the user navigates between pages, THE FacilIAuto Frontend SHALL transition within 300ms using client-side routing
3. WHEN the user submits the questionnaire, THE FacilIAuto Frontend SHALL display a loading indicator within 100ms of the button tap
4. WHEN waiting for Backend API responses, THE FacilIAuto Frontend SHALL show contextual loading states (skeleton screens for lists, spinners for actions)
5. WHEN the Backend API responds, THE FacilIAuto Frontend SHALL render results within 500ms of receiving data
6. WHEN the user scrolls the results page, THE FacilIAuto Frontend SHALL maintain 60fps scroll performance with smooth animations
7. WHEN loading car images, THE FacilIAuto Frontend SHALL use lazy loading and display placeholders until images load
8. WHEN images fail to load, THE FacilIAuto Frontend SHALL display fallback placeholder images without breaking layout
9. WHILE the user interacts with filters, THE FacilIAuto Frontend SHALL debounce rapid changes (300ms) to avoid excessive re-renders
10. THE FacilIAuto Frontend SHALL implement code splitting to load only necessary JavaScript for each route

### Requirement 9: Accessibility and Usability

**User Story:** As a user with accessibility needs, I want the application to be usable with assistive technologies, so that I can find my ideal car regardless of my abilities.

#### Acceptance Criteria

1. THE FacilIAuto Frontend SHALL implement semantic HTML with proper heading hierarchy (h1, h2, h3)
2. WHEN the user navigates with keyboard, THE FacilIAuto Frontend SHALL provide visible focus indicators on all interactive elements
3. WHEN the user uses a screen reader, THE FacilIAuto Frontend SHALL provide descriptive ARIA labels for all controls
4. WHEN displaying images, THE FacilIAuto Frontend SHALL include descriptive alt text for car images
5. WHEN showing color-coded information, THE FacilIAuto Frontend SHALL provide additional non-color indicators (icons, text)
6. THE FacilIAuto Frontend SHALL maintain minimum 4.5:1 contrast ratio for all text (WCAG AA standard)
7. WHEN the user interacts with forms, THE FacilIAuto Frontend SHALL associate labels with inputs using proper HTML for attributes
8. WHEN displaying modals or overlays, THE FacilIAuto Frontend SHALL trap focus within the modal and restore focus on close
9. WHEN showing dynamic content updates, THE FacilIAuto Frontend SHALL announce changes to screen readers using ARIA live regions
10. THE FacilIAuto Frontend SHALL support browser zoom up to 200% without breaking layout or losing functionality

### Requirement 10: Testing and Quality Assurance

**User Story:** As a developer, I want comprehensive test coverage, so that I can confidently deploy changes without breaking existing functionality.

#### Acceptance Criteria

1. THE FacilIAuto Frontend SHALL include unit tests for all utility functions and custom hooks with 80%+ coverage
2. THE FacilIAuto Frontend SHALL include component tests for all major UI components (Questionnaire steps, Car Cards, Results page)
3. THE FacilIAuto Frontend SHALL include integration tests for Backend API calls and error handling scenarios
4. THE FacilIAuto Frontend SHALL include E2E tests for the complete user journey (landing → questionnaire → results → contact)
5. WHEN running the test suite, THE FacilIAuto Frontend SHALL complete all tests within 30 seconds
6. WHEN tests fail, THE FacilIAuto Frontend SHALL provide clear error messages indicating what broke and where
7. THE FacilIAuto Frontend SHALL use TypeScript strict mode with no type errors
8. THE FacilIAuto Frontend SHALL pass ESLint validation with no errors (warnings acceptable)
9. THE FacilIAuto Frontend SHALL pass Prettier formatting checks
10. WHEN building for production, THE FacilIAuto Frontend SHALL generate optimized bundles under 500KB (gzipped) for initial load
