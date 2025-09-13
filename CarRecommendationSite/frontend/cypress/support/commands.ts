/// <reference types="cypress" />

// Custom Commands for CarMatch E2E Tests

// Type definitions for custom commands
declare global {
  namespace Cypress {
    interface Chainable {
      // Database commands
      seedDatabase(): Chainable<void>;
      clearDatabase(): Chainable<void>;
      
      // Authentication commands
      login(email?: string, password?: string): Chainable<void>;
      logout(): Chainable<void>;
      
      // Navigation commands
      visitHomePage(): Chainable<void>;
      startQuestionnaire(): Chainable<void>;
      goToStep(stepNumber: number): Chainable<void>;
      
      // Questionnaire commands
      fillBudgetStep(min: number, max: number, city: string, state: string): Chainable<void>;
      fillUsageStep(purpose: string, frequency: string): Chainable<void>;
      fillFamilyStep(size: number, hasChildren: boolean): Chainable<void>;
      fillPrioritiesStep(priorities: Record<string, number>): Chainable<void>;
      fillPreferencesStep(brands: string[], types: string[]): Chainable<void>;
      
      // Results commands
      waitForRecommendations(): Chainable<void>;
      checkRecommendationCount(expectedCount: number): Chainable<void>;
      selectCar(carIndex: number): Chainable<void>;
      compareCars(carIndices: number[]): Chainable<void>;
      
      // Interaction commands
      clickNext(): Chainable<void>;
      clickPrevious(): Chainable<void>;
      submitQuestionnaire(): Chainable<void>;
      
      // Validation commands
      validateStep(stepNumber: number): Chainable<void>;
      validateCarCard(carData: any): Chainable<void>;
      validateRecommendationScore(minScore: number): Chainable<void>;
      
      // Utility commands
      takeNamedScreenshot(name: string): Chainable<void>;
      mockApiResponse(endpoint: string, response: any): Chainable<void>;
      waitForPageLoad(): Chainable<void>;
    }
  }
}

// Database commands
Cypress.Commands.add('seedDatabase', () => {
  cy.task('seedDatabase');
});

Cypress.Commands.add('clearDatabase', () => {
  cy.task('clearDatabase');
});

// Authentication commands
Cypress.Commands.add('login', (email = Cypress.env('TEST_USER_EMAIL'), password = Cypress.env('TEST_USER_PASSWORD')) => {
  cy.session([email, password], () => {
    cy.visit('/login');
    cy.get('[data-cy="email-input"]').type(email);
    cy.get('[data-cy="password-input"]').type(password, { log: false });
    cy.get('[data-cy="login-button"]').click();
    cy.url().should('not.include', '/login');
  });
});

Cypress.Commands.add('logout', () => {
  cy.get('[data-cy="user-menu"]').click();
  cy.get('[data-cy="logout-button"]').click();
  cy.url().should('include', '/');
});

// Navigation commands
Cypress.Commands.add('visitHomePage', () => {
  cy.visit('/');
  cy.waitForPageLoad();
});

Cypress.Commands.add('startQuestionnaire', () => {
  cy.get('[data-cy="start-questionnaire-button"]').click();
  cy.url().should('include', '/questionnaire');
  cy.get('[data-cy="questionnaire-container"]').should('be.visible');
});

Cypress.Commands.add('goToStep', (stepNumber: number) => {
  cy.get(`[data-cy="step-${stepNumber}"]`).click();
  cy.get(`[data-cy="step-${stepNumber}-content"]`).should('be.visible');
});

// Questionnaire commands
Cypress.Commands.add('fillBudgetStep', (min: number, max: number, city: string, state: string) => {
  cy.get('[data-cy="budget-slider"]').within(() => {
    // Set minimum value
    cy.get('.chakra-slider__thumb').first().click();
    cy.get('.chakra-slider__thumb').first().type(`{leftarrow}`.repeat(50));
    for (let i = 0; i < Math.floor((min - 20000) / 5000); i++) {
      cy.get('.chakra-slider__thumb').first().type('{rightarrow}');
    }
    
    // Set maximum value
    cy.get('.chakra-slider__thumb').last().click();
    cy.get('.chakra-slider__thumb').last().type(`{leftarrow}`.repeat(50));
    for (let i = 0; i < Math.floor((max - 20000) / 5000); i++) {
      cy.get('.chakra-slider__thumb').last().type('{rightarrow}');
    }
  });
  
  cy.get('[data-cy="city-input"]').type(city);
  cy.get('[data-cy="state-select"]').select(state);
});

Cypress.Commands.add('fillUsageStep', (purpose: string, frequency: string) => {
  cy.get(`[data-cy="purpose-${purpose}"]`).click();
  cy.get(`[data-cy="frequency-${frequency}"]`).click();
});

Cypress.Commands.add('fillFamilyStep', (size: number, hasChildren: boolean) => {
  cy.get('[data-cy="family-size-input"]').clear().type(size.toString());
  if (hasChildren) {
    cy.get('[data-cy="has-children-switch"]').click();
  }
});

Cypress.Commands.add('fillPrioritiesStep', (priorities: Record<string, number>) => {
  Object.entries(priorities).forEach(([priority, value]) => {
    cy.get(`[data-cy="priority-${priority}-slider"]`)
      .within(() => {
        cy.get('.chakra-slider__thumb').click();
        cy.get('.chakra-slider__thumb').type('{leftarrow}'.repeat(5));
        for (let i = 0; i < value - 1; i++) {
          cy.get('.chakra-slider__thumb').type('{rightarrow}');
        }
      });
  });
});

Cypress.Commands.add('fillPreferencesStep', (brands: string[], types: string[]) => {
  brands.forEach(brand => {
    cy.get('[data-cy="brand-search"]').type(brand);
    cy.get(`[data-cy="brand-option-${brand}"]`).click();
  });
  
  types.forEach(type => {
    cy.get(`[data-cy="vehicle-type-${type}"]`).click();
  });
});

// Results commands
Cypress.Commands.add('waitForRecommendations', () => {
  cy.get('[data-cy="loading-recommendations"]', { timeout: 30000 }).should('not.exist');
  cy.get('[data-cy="recommendations-container"]').should('be.visible');
});

Cypress.Commands.add('checkRecommendationCount', (expectedCount: number) => {
  cy.get('[data-cy="car-recommendation"]').should('have.length', expectedCount);
});

Cypress.Commands.add('selectCar', (carIndex: number) => {
  cy.get('[data-cy="car-recommendation"]').eq(carIndex).click();
  cy.get('[data-cy="car-details-modal"]').should('be.visible');
});

Cypress.Commands.add('compareCars', (carIndices: number[]) => {
  carIndices.forEach(index => {
    cy.get('[data-cy="car-recommendation"]').eq(index).within(() => {
      cy.get('[data-cy="compare-checkbox"]').click();
    });
  });
  
  cy.get('[data-cy="compare-button"]').click();
  cy.get('[data-cy="comparison-table"]').should('be.visible');
});

// Interaction commands
Cypress.Commands.add('clickNext', () => {
  cy.get('[data-cy="next-button"]').click();
});

Cypress.Commands.add('clickPrevious', () => {
  cy.get('[data-cy="previous-button"]').click();
});

Cypress.Commands.add('submitQuestionnaire', () => {
  cy.get('[data-cy="submit-questionnaire-button"]').click();
  cy.waitForRecommendations();
});

// Validation commands
Cypress.Commands.add('validateStep', (stepNumber: number) => {
  cy.get(`[data-cy="step-${stepNumber}-indicator"]`).should('have.class', 'active');
  cy.get('[data-cy="step-progress"]').should('contain.text', `${stepNumber + 1}/5`);
});

Cypress.Commands.add('validateCarCard', (carData: any) => {
  cy.get('[data-cy="car-recommendation"]').first().within(() => {
    cy.get('[data-cy="car-brand"]').should('contain.text', carData.marca);
    cy.get('[data-cy="car-model"]').should('contain.text', carData.modelo);
    cy.get('[data-cy="car-year"]').should('contain.text', carData.ano);
    cy.get('[data-cy="car-price"]').should('contain.text', carData.preco);
  });
});

Cypress.Commands.add('validateRecommendationScore', (minScore: number) => {
  cy.get('[data-cy="recommendation-score"]').first().then($score => {
    const score = parseFloat($score.text().replace('%', ''));
    expect(score).to.be.at.least(minScore);
  });
});

// Utility commands
Cypress.Commands.add('takeNamedScreenshot', (name: string) => {
  cy.screenshot(name, { capture: 'fullPage' });
});

Cypress.Commands.add('mockApiResponse', (endpoint: string, response: any) => {
  cy.intercept('GET', `${Cypress.env('API_URL')}${endpoint}`, response).as('mockedRequest');
});

Cypress.Commands.add('waitForPageLoad', () => {
  cy.get('[data-cy="loading-spinner"]', { timeout: 10000 }).should('not.exist');
  cy.get('[data-cy="page-content"]').should('be.visible');
});

// Add command to preserve cookies
Cypress.Commands.add('preserveLogin', () => {
  Cypress.Cookies.preserveOnce('session-token', 'refresh-token');
});

// Custom command for API requests
Cypress.Commands.add('apiRequest', (method: string, url: string, body?: any) => {
  return cy.request({
    method,
    url: `${Cypress.env('API_URL')}${url}`,
    body,
    headers: {
      'Content-Type': 'application/json',
    },
  });
});

// Command for waiting for API calls to complete
Cypress.Commands.add('waitForApiCalls', () => {
  cy.intercept('**').as('apiCall');
  cy.wait('@apiCall', { timeout: 10000 });
});

export {};
