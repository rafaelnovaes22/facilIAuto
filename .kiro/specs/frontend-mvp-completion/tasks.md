# Implementation Plan - Frontend MVP Completion

This implementation plan breaks down the frontend completion into discrete, actionable coding tasks. Each task builds incrementally on previous work, with the goal of reaching 90%+ production-ready state in 2-3 weeks.

## Task List

- [x] 1. Setup error boundaries and loading infrastructure





  - Create root error boundary component with fallback UI
  - Create page-level error boundary wrapper
  - Implement LoadingSpinner component (sm, md, lg sizes)
  - Implement SkeletonCard component for car cards
  - Create ErrorMessage component with retry functionality
  - _Requirements: 4.3, 4.4, 4.5, 4.6, 4.7, 8.3, 8.4_

- [x] 2. Implement common UI components





  - [x] 2.1 Create Button component with variants and loading states


    - Implement solid, outline, ghost variants
    - Add loading state with spinner
    - Add icon support (left/right positioning)
    - Ensure 44px minimum tap target for mobile
    - _Requirements: 3.2, 9.2_

  - [x] 2.2 Create Card component with hover effects


    - Implement base card with Chakra UI
    - Add hover animations (translateY, boxShadow)
    - Add click handling and active states
    - Ensure mobile-optimized touch feedback
    - _Requirements: 3.2, 3.9_

  - [x] 2.3 Create EmptyState component


    - Implement with icon, message, and action button
    - Add illustration support
    - Make responsive for mobile/desktop
    - _Requirements: 2.8_

  - [ ]* 2.4 Write unit tests for common components
    - Test Button variants and loading states
    - Test Card hover and click behavior
    - Test EmptyState rendering
    - _Requirements: 10.2_

- [x] 3. Complete HomePage implementation




  - [x] 3.1 Implement hero section with CTA

    - Create hero layout with heading and description
    - Add "Começar" button navigating to /questionario
    - Implement mobile-first responsive design
    - Add simple animations (fade-in on load)
    - _Requirements: 1.1, 3.1, 3.4_

  - [x] 3.2 Add platform statistics display

    - Fetch stats from GET /stats endpoint using React Query
    - Display total cars, dealerships, avg price
    - Handle loading and error states
    - Make stats responsive (stack on mobile)
    - _Requirements: 4.1, 8.2_

  - [ ]* 3.3 Write E2E test for homepage navigation
    - Test "Começar" button navigation
    - Test stats loading
    - _Requirements: 10.4_

- [x] 4. Implement questionnaire Step 1 (Budget & Location)


  - [x] 4.1 Create BudgetSlider component


    - Implement dual-handle range slider using Chakra UI
    - Add currency formatting (R$)
    - Display min/max values in real-time
    - Ensure mobile-friendly touch interaction
    - _Requirements: 1.1, 3.2, 3.3_

  - [x] 4.2 Create LocationSelector component


    - Implement city text input with autocomplete
    - Add state dropdown (27 Brazilian states)
    - Make optional (user can skip)
    - Integrate with Zustand store
    - _Requirements: 1.6, 7.1, 7.2_

  - [x] 4.3 Implement Step 1 page layout


    - Create step container with progress indicator
    - Add BudgetSlider and LocationSelector
    - Implement "Próximo" button with validation
    - Connect to Zustand store (updateFormData)
    - _Requirements: 1.1, 1.2, 1.8, 7.1_

  - [ ]* 4.4 Write component tests for Step 1
    - Test budget slider value changes
    - Test location input
    - Test validation logic
    - _Requirements: 10.2_


- [x] 5. Implement questionnaire Step 2 (Usage Profile)


  - [x] 5.1 Create UsageProfileCard component


    - Implement card with icon, title, description
    - Add selected state styling
    - Ensure 44px minimum tap target
    - Add hover/active states for feedback
    - _Requirements: 1.3, 3.2, 3.9_

  - [x] 5.2 Implement Step 2 page layout


    - Create grid layout for 6 usage profiles
    - Add profile cards: Família, Trabalho, Lazer, Comercial, Primeiro Carro, Transporte Passageiros
    - Implement single selection (radio button behavior)
    - Connect to Zustand store
    - Make responsive (1 column mobile, 2 columns tablet, 3 columns desktop)
    - _Requirements: 1.3, 1.4, 3.5, 3.6, 3.7, 6.1, 6.2_

  - [x] 5.3 Add simplified descriptions for each profile


    - Write grandmother-friendly descriptions
    - Add icons for visual clarity
    - Implement tooltips with examples
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.6, 6.10_

  - [ ]* 5.4 Write component tests for Step 2
    - Test profile selection
    - Test single selection behavior
    - Test Zustand store integration
    - _Requirements: 10.2_

- [x] 6. Implement questionnaire Step 3 (Priorities)


  - [x] 6.1 Create PrioritySlider component


    - Implement slider with 1-5 scale
    - Add visual highlighting for top 3 priorities
    - Display label and current value
    - Add tooltip with simplified explanation
    - _Requirements: 1.5, 1.6, 6.3, 6.6_

  - [x] 6.2 Implement Step 3 page layout


    - Create layout for 5 priority sliders
    - Add sliders: Economia, Espaço, Performance, Conforto, Segurança
    - Implement real-time top 3 calculation and highlighting
    - Set default values based on selected usage profile
    - Connect to Zustand store
    - _Requirements: 1.5, 1.6, 7.1, 7.2_

  - [x] 6.3 Add simplified labels and tooltips


    - Use everyday language for priorities
    - Add visual examples in tooltips
    - Avoid technical jargon
    - _Requirements: 6.1, 6.2, 6.3, 6.6, 6.7, 6.8_

  - [ ]* 6.4 Write component tests for Step 3
    - Test slider value changes
    - Test top 3 calculation
    - Test default values from usage profile
    - _Requirements: 10.2_

- [x] 7. Implement questionnaire Step 4 (Location confirmation)


  - [x] 7.1 Create final location confirmation UI


    - Display city/state if entered in Step 1
    - Allow editing or adding location
    - Add optional distance radius slider
    - _Requirements: 1.7, 7.2_

  - [x] 7.2 Implement "Ver Recomendações" button


    - Enable only when form is complete (isComplete())
    - Add loading state during navigation
    - Convert form data to UserProfile (toUserProfile())
    - Navigate to /resultados with profile
    - _Requirements: 1.7, 7.1, 7.3_

  - [ ]* 7.3 Write integration test for complete questionnaire flow
    - Test all 4 steps completion
    - Test data persistence across steps
    - Test navigation to results
    - _Requirements: 10.3, 10.4_

- [x] 8. Implement step navigation and progress indicators


  - [x] 8.1 Create StepIndicator component


    - Display current step (1/4, 2/4, 3/4, 4/4)
    - Show visual progress bar
    - Add step labels
    - Make responsive for mobile
    - _Requirements: 1.8, 3.4_

  - [x] 8.2 Implement navigation controls


    - Add "Próximo" and "Anterior" buttons
    - Implement validation before allowing next step (canGoNext())
    - Preserve data when navigating back (previousStep())
    - Add keyboard navigation (Enter for next, Escape for back)
    - _Requirements: 1.2, 1.9, 7.2, 7.6, 9.2_

  - [x] 8.3 Add browser back/forward support


    - Update URL with current step (/questionario?step=1)
    - Handle browser back/forward buttons
    - Restore step from URL on page load
    - _Requirements: 7.9_

  - [ ]* 8.4 Write tests for navigation logic
    - Test step validation
    - Test data persistence
    - Test browser navigation
    - _Requirements: 10.1, 10.2_


- [x] 9. Implement ResultsPage core functionality

  - [x] 9.1 Create ProfileSummary component


    - Display user's top 3 priorities with icons
    - Show budget range (formatted as R$)
    - Show location if provided
    - Add "Editar" button to return to questionnaire
    - Make responsive for mobile
    - _Requirements: 2.5, 6.9, 7.6_

  - [x] 9.2 Implement recommendations API integration

    - Read user profile from Zustand store
    - Call POST /recommend using React Query
    - Handle loading state (show skeleton cards)
    - Handle error state (show ErrorMessage with retry)
    - Handle empty state (no recommendations)
    - Track interaction via POST /api/interactions/track
    - _Requirements: 2.1, 2.2, 4.1, 4.2, 4.3, 4.4, 4.10, 8.3, 8.4_

  - [x] 9.3 Create ResultsPage layout


    - Add ProfileSummary at top
    - Add FilterPanel (sidebar on desktop, bottom sheet on mobile)
    - Add SortDropdown
    - Add car grid container
    - Implement responsive layout (1 column mobile, 2 tablet, 3-4 desktop)
    - _Requirements: 2.5, 3.5, 3.6, 3.7_

  - [ ]* 9.4 Write integration tests for results loading
    - Test API call with user profile
    - Test loading state
    - Test error handling
    - Test empty state
    - _Requirements: 10.3_

- [x] 10. Implement CarCard component



  - [x] 10.1 Create CarCard layout

    - Display car image with lazy loading
    - Show car name (marca + modelo + ano)
    - Display price (formatted as R$)
    - Show match score badge (0-100%)
    - Display top 3 matching features in simplified language
    - Add hover effects (translateY, boxShadow)
    - Ensure 44px minimum tap target
    - _Requirements: 2.3, 3.2, 3.9, 6.2, 6.3, 6.4, 8.7_

  - [x] 10.2 Implement image handling

    - Add lazy loading with Intersection Observer
    - Display placeholder until image loads
    - Handle image load errors (fallback placeholder)
    - Add fade-in animation when loaded
    - _Requirements: 8.7, 8.8_

  - [x] 10.3 Add click handler for modal

    - Implement onClick to open CarDetailsModal
    - Pass car data to modal
    - Track click interaction
    - _Requirements: 2.4_

  - [ ]* 10.4 Write component tests for CarCard
    - Test car data display
    - Test image lazy loading
    - Test click handler
    - Test fallback image
    - _Requirements: 10.2_

- [x] 11. Implement CarDetailsModal component


  - [x] 11.1 Create modal layout

    - Implement full-screen modal on mobile, centered on desktop
    - Add close button (X icon and Escape key)
    - Display car image gallery (swipeable on mobile)
    - Show complete car specifications
    - Display justification text in simplified language
    - Show dealership information
    - Make responsive (full screen mobile, 60% width desktop)
    - _Requirements: 2.4, 3.7, 3.8, 6.4, 9.8_

  - [x] 11.2 Implement WhatsApp contact button

    - Create "Falar no WhatsApp" button
    - Generate WhatsApp URL with pre-filled message
    - Include car name, match score, user name in message
    - Use dealership WhatsApp number from car data
    - Handle missing WhatsApp number (show phone/email fallback)
    - Track contact_initiated interaction
    - Open WhatsApp in new tab (mobile app if available)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10_

  - [x] 11.3 Add accessibility features

    - Trap focus within modal
    - Restore focus on close
    - Add ARIA labels and roles
    - Support Escape key to close
    - _Requirements: 9.2, 9.3, 9.8_

  - [ ]* 11.4 Write component tests for modal
    - Test modal open/close
    - Test WhatsApp URL generation
    - Test keyboard navigation
    - Test focus trap
    - _Requirements: 10.2_


- [x] 12. Implement filtering functionality


  - [x] 12.1 Create FilterPanel component

    - Implement price range filter (dual slider)
    - Add category filter (checkboxes: Hatch, Sedan, SUV, etc.)
    - Add brand filter (checkboxes with search)
    - Add dealership filter (checkboxes)
    - Add "Limpar filtros" button
    - Make responsive (sidebar desktop, bottom sheet mobile)
    - _Requirements: 2.6, 3.5, 3.6_

  - [x] 12.2 Implement client-side filtering logic

    - Filter recommendations array based on selected filters
    - Update displayed cars in real-time (no API call)
    - Preserve filter state in URL query parameters
    - Restore filters from URL on page load
    - _Requirements: 2.6, 7.4, 7.5_

  - [x] 12.3 Add filter state management

    - Store filters in local component state
    - Sync filters with URL query parameters
    - Persist filters to localStorage
    - _Requirements: 7.4, 7.5, 7.10_

  - [ ]* 12.4 Write tests for filtering logic
    - Test price range filtering
    - Test category filtering
    - Test multiple filters combined
    - Test clear filters
    - _Requirements: 10.1, 10.3_

- [x] 13. Implement sorting functionality


  - [x] 13.1 Create SortDropdown component

    - Add sort options: Score (default), Price (low-high), Price (high-low), Year (newest)
    - Display current sort with icon
    - Make mobile-friendly (large tap targets)
    - _Requirements: 2.7, 3.2_

  - [x] 13.2 Implement client-side sorting logic

    - Sort recommendations array based on selected option
    - Update displayed cars immediately with smooth animation
    - Preserve sort order in URL query parameters
    - _Requirements: 2.7, 7.4, 8.6_

  - [ ]* 13.3 Write tests for sorting logic
    - Test each sort option
    - Test sort order persistence
    - _Requirements: 10.1_

- [x] 14. Implement empty and error states



  - [x] 14.1 Add empty state for no recommendations

    - Display when API returns 0 recommendations
    - Show helpful message
    - Suggest returning to questionnaire
    - _Requirements: 2.8_

  - [x] 14.2 Add empty state for no filtered results

    - Display when filters exclude all cars
    - Show current filters
    - Suggest adjusting filters
    - Add "Limpar filtros" button
    - _Requirements: 2.8_

  - [x] 14.3 Implement error handling for API failures

    - Display ErrorMessage component on API error
    - Show user-friendly message (not technical details)
    - Add retry button
    - Log technical details to console
    - _Requirements: 2.10, 4.3, 4.4, 4.5, 4.6, 6.5_

  - [ ]* 14.4 Write tests for error scenarios
    - Test API timeout
    - Test network error
    - Test 500 error
    - Test retry functionality
    - _Requirements: 10.3_

- [x] 15. Implement performance optimizations


  - [x] 15.1 Add code splitting for routes

    - Lazy load HomePage, QuestionnairePage, ResultsPage
    - Add Suspense boundaries with loading fallbacks
    - _Requirements: 8.1, 8.2, 10.10_

  - [x] 15.2 Add code splitting for heavy components

    - Lazy load CarDetailsModal
    - Lazy load FilterPanel
    - Add loading fallbacks
    - _Requirements: 8.2, 10.10_

  - [x] 15.3 Optimize image loading

    - Implement lazy loading with Intersection Observer
    - Add blur-up placeholder effect
    - Optimize image sizes (responsive images)
    - _Requirements: 8.7, 8.8_

  - [x] 15.4 Implement debouncing for filters

    - Debounce filter changes (300ms)
    - Avoid excessive re-renders
    - _Requirements: 8.9_

  - [ ]* 15.5 Run Lighthouse audit and optimize
    - Target: Performance 90+, Accessibility 95+
    - Fix any issues identified
    - _Requirements: 3.10, 8.1, 8.5, 8.6_


- [x] 16. Implement accessibility features


  - [x] 16.1 Add semantic HTML structure

    - Use proper heading hierarchy (h1, h2, h3)
    - Add landmark elements (header, nav, main, aside, footer)
    - Use semantic elements (button, form, label)
    - _Requirements: 9.1, 9.7_

  - [x] 16.2 Implement keyboard navigation

    - Ensure all interactive elements are keyboard accessible
    - Add visible focus indicators (2px solid outline)
    - Support Tab, Enter, Escape keys
    - Add skip links for main content
    - _Requirements: 9.2, 9.3_

  - [x] 16.3 Add ARIA labels and roles

    - Add aria-label for icon-only buttons
    - Add aria-describedby for form errors
    - Add role="status" for dynamic content
    - Add aria-live regions for announcements
    - _Requirements: 9.3, 9.4, 9.9_

  - [x] 16.4 Ensure color contrast compliance

    - Verify all text meets 4.5:1 contrast ratio
    - Verify UI components meet 3:1 contrast ratio
    - Add non-color indicators where needed
    - _Requirements: 9.5, 9.6_

  - [ ]* 16.5 Run accessibility audit
    - Use axe DevTools or Lighthouse
    - Fix all critical and serious issues
    - Target: Accessibility score 95+
    - _Requirements: 9.1-9.10_

- [x] 17. Implement state persistence


  - [x] 17.1 Add localStorage persistence for user profile

    - Save questionnaire data to localStorage on each step
    - Restore data on page load
    - Clear on "Nova busca"
    - _Requirements: 7.1, 7.2, 7.5, 7.10_

  - [x] 17.2 Add URL state for filters and sort

    - Sync filters with URL query parameters
    - Sync sort order with URL
    - Enable sharing and bookmarking
    - Restore state from URL on load
    - _Requirements: 7.4, 7.5_

  - [x] 17.3 Implement "Nova busca" functionality

    - Add button to clear profile and start over
    - Clear localStorage
    - Reset Zustand store
    - Navigate to questionnaire Step 1
    - _Requirements: 7.7_

  - [ ]* 17.4 Write tests for state persistence
    - Test localStorage save/restore
    - Test URL state sync
    - Test clear functionality
    - _Requirements: 10.1_

- [x] 18. Implement loading states and animations


  - [x] 18.1 Add skeleton screens for loading

    - Create SkeletonCard for car cards
    - Show 6-12 skeleton cards while loading
    - Match actual card dimensions
    - Add shimmer animation
    - _Requirements: 8.4_

  - [x] 18.2 Add loading spinners for actions

    - Add spinner to "Ver Recomendações" button
    - Add spinner to retry buttons
    - Add spinner to WhatsApp button (brief)
    - _Requirements: 8.3, 8.4_

  - [x] 18.3 Add smooth transitions and animations

    - Fade-in for page loads
    - Slide-in for modals
    - Smooth scroll for navigation
    - Hover animations for cards
    - _Requirements: 3.9, 8.6_

  - [ ]* 18.4 Test loading states
    - Test skeleton screens display
    - Test spinner display
    - Test animations don't cause layout shift
    - _Requirements: 10.2_

- [ ] 19. Write E2E tests for critical flows
  - [ ]* 19.1 Write complete questionnaire flow test
    - Test all 4 steps completion
    - Test data persistence
    - Test validation
    - Test navigation to results
    - _Requirements: 10.4_

  - [ ]* 19.2 Write filtering and sorting test
    - Test price filter
    - Test category filter
    - Test sort by price
    - Test sort by score
    - _Requirements: 10.4_

  - [ ]* 19.3 Write car details and WhatsApp test
    - Test car card click
    - Test modal open
    - Test WhatsApp URL generation
    - Test modal close
    - _Requirements: 10.4_

  - [ ]* 19.4 Write error handling test
    - Test API timeout
    - Test retry functionality
    - Test empty state
    - _Requirements: 10.4_


- [x] 20. Implement simplified language throughout


  - [x] 20.1 Update questionnaire text

    - Replace technical terms with simplified language
    - Update step titles and descriptions
    - Update button labels
    - Update validation messages
    - _Requirements: 6.1, 6.2, 6.3, 6.5, 6.10_

  - [x] 20.2 Update results page text

    - Translate car features to benefits
    - Update justification text
    - Update filter labels
    - Update empty state messages
    - _Requirements: 6.2, 6.3, 6.4, 6.5_

  - [x] 20.3 Update error messages

    - Replace technical errors with friendly messages
    - Use positive, solution-oriented language
    - Add helpful suggestions
    - _Requirements: 6.5, 6.10_

  - [x] 20.4 Add tooltips with visual explanations

    - Add tooltips for priorities
    - Add tooltips for car features
    - Use simple language and examples
    - _Requirements: 6.6_

  - [ ]* 20.5 Review all text with "grandmother test"
    - Ensure all text is understandable without car knowledge
    - Remove any remaining jargon
    - _Requirements: 6.1-6.10_

- [x] 21. Polish and final touches


  - [x] 21.1 Add favicon and meta tags

    - Add favicon (multiple sizes)
    - Add Open Graph meta tags
    - Add Twitter Card meta tags
    - Add description and keywords
    - _Requirements: 3.10_

  - [x] 21.2 Implement 404 page

    - Create NotFoundPage component
    - Add helpful message
    - Add navigation back to home
    - _Requirements: 4.7_

  - [x] 21.3 Add loading screen for initial load

    - Show logo and spinner on app initialization
    - Hide once React app is ready
    - Target: < 2s on 3G
    - _Requirements: 3.10, 8.1_

  - [x] 21.4 Optimize bundle size

    - Analyze bundle with Vite build analyzer
    - Remove unused dependencies
    - Optimize Chakra UI imports
    - Target: < 500KB gzipped total
    - _Requirements: 10.10_

  - [x] 21.5 Add environment variable configuration

    - Create .env.example file
    - Document required variables
    - Add validation for missing variables
    - _Requirements: 4.1_

  - [ ]* 21.6 Final manual testing on devices
    - Test on iPhone (Safari)
    - Test on Android (Chrome)
    - Test on tablet
    - Test on desktop (Chrome, Firefox, Safari)
    - _Requirements: 3.1-3.10_

- [x] 22. Documentation and deployment preparation



  - [x] 22.1 Update README.md

    - Document setup instructions
    - Document available scripts
    - Document environment variables
    - Add screenshots
    - _Requirements: N/A_

  - [x] 22.2 Create deployment guide

    - Document build process
    - Document hosting requirements
    - Document environment configuration
    - Add troubleshooting section
    - _Requirements: N/A_

  - [x] 22.3 Create component documentation

    - Document all reusable components
    - Add usage examples
    - Document props and types
    - _Requirements: N/A_

  - [ ]* 22.4 Run final test suite
    - Run all unit tests (npm test)
    - Run all E2E tests (npm run e2e)
    - Verify 80%+ coverage
    - Fix any failing tests
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ]* 22.5 Run production build and verify
    - Build for production (npm run build)
    - Verify bundle sizes
    - Test production build locally (npm run preview)
    - Verify all features work in production mode
    - _Requirements: 10.10_

## Implementation Notes

### Execution Order
Tasks are ordered to build incrementally:
1. **Tasks 1-2**: Foundation (error handling, common components)
2. **Tasks 3-8**: Questionnaire flow (complete user input)
3. **Tasks 9-14**: Results page (display and interaction)
4. **Tasks 15-18**: Polish (performance, accessibility, UX)
5. **Tasks 19-20**: Quality (testing, language)
6. **Tasks 21-22**: Finalization (deployment, documentation)

### Testing Strategy
- Optional tasks (marked with *) focus on testing and quality assurance
- Core implementation tasks are NOT optional
- Tests should be written after implementation, not before (implementation-first)
- E2E tests cover critical user flows only

### Time Estimates
- **Week 1**: Tasks 1-8 (Questionnaire complete)
- **Week 2**: Tasks 9-14 (Results page complete)
- **Week 3**: Tasks 15-22 (Polish, testing, deployment)

### Dependencies
- Backend API must be running at localhost:8000
- All tasks assume types in src/types/index.ts are correct
- Zustand store structure from src/store/questionnaireStore.ts is used throughout
- Chakra UI theme from src/theme/index.ts provides consistent styling

### Success Criteria
- All non-optional tasks completed
- E2E test for complete user flow passing
- Lighthouse scores: Performance 90+, Accessibility 95+
- Manual testing on mobile and desktop successful
- Production build under 500KB gzipped
- No TypeScript errors
- No ESLint errors
