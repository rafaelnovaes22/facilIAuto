/// <reference types="cypress" />

describe('CarMatch - Complete User Journey', () => {
  beforeEach(() => {
    // Seed database with test data
    cy.seedDatabase();
    
    // Visit home page
    cy.visitHomePage();
  });
  
  afterEach(() => {
    // Clear test data after each test
    cy.clearDatabase();
  });

  context('Landing Page Experience', () => {
    it('should display main value proposition and start button', () => {
      // Validate hero section
      cy.get('[data-cy="hero-title"]').should('contain.text', 'Encontre o carro ideal');
      cy.get('[data-cy="hero-subtitle"]').should('be.visible');
      cy.get('[data-cy="start-questionnaire-button"]').should('be.visible');
      
      // Validate trust indicators
      cy.get('[data-cy="trust-indicators"]').should('be.visible');
      cy.get('[data-cy="testimonials"]').should('have.length.at.least', 3);
      
      // Take screenshot for visual regression
      cy.takeNamedScreenshot('landing-page');
    });

    it('should have proper SEO elements', () => {
      cy.title().should('contain', 'CarMatch');
      cy.get('meta[name="description"]').should('have.attr', 'content');
      cy.get('meta[property="og:title"]').should('exist');
    });
  });

  context('Questionnaire Flow - Happy Path', () => {
    beforeEach(() => {
      cy.startQuestionnaire();
    });

    it('should complete full questionnaire for family profile', () => {
      // Step 1: Budget and Location
      cy.validateStep(0);
      cy.fillBudgetStep(50000, 80000, 'São Paulo', 'SP');
      cy.clickNext();
      
      // Step 2: Usage Profile
      cy.validateStep(1);
      cy.fillUsageStep('familia', 'diaria');
      cy.clickNext();
      
      // Step 3: Family Needs
      cy.validateStep(2);
      cy.fillFamilyStep(4, true);
      cy.clickNext();
      
      // Step 4: Priorities
      cy.validateStep(3);
      cy.fillPrioritiesStep({
        fuelEconomy: 4,
        safety: 5,
        reliability: 5,
        comfort: 4,
        resaleValue: 3
      });
      cy.clickNext();
      
      // Step 5: Preferences
      cy.validateStep(4);
      cy.fillPreferencesStep(['Toyota', 'Honda', 'Chevrolet'], ['suv', 'sedan']);
      
      // Submit questionnaire
      cy.submitQuestionnaire();
      
      // Validate results
      cy.waitForRecommendations();
      cy.checkRecommendationCount(5);
      
      // Validate first recommendation is appropriate for family
      cy.get('[data-cy="car-recommendation"]').first().within(() => {
        cy.get('[data-cy="car-seats"]').invoke('text').then(seats => {
          expect(parseInt(seats)).to.be.at.least(5);
        });
        cy.get('[data-cy="recommendation-score"]').should('be.visible');
        cy.get('[data-cy="justification"]').should('contain.text', 'família');
      });
      
      cy.takeNamedScreenshot('family-recommendations');
    });

    it('should complete questionnaire for economic profile', () => {
      // Economic user journey
      cy.fillBudgetStep(25000, 45000, 'Belo Horizonte', 'MG');
      cy.clickNext();
      
      cy.fillUsageStep('trabalho', 'diaria');
      cy.clickNext();
      
      cy.fillFamilyStep(2, false);
      cy.clickNext();
      
      cy.fillPrioritiesStep({
        fuelEconomy: 5,
        maintenance: 5,
        resaleValue: 4,
        performance: 2
      });
      cy.clickNext();
      
      cy.fillPreferencesStep(['Volkswagen', 'Fiat', 'Hyundai'], ['hatch', 'compacto']);
      cy.submitQuestionnaire();
      
      // Validate economic recommendations
      cy.waitForRecommendations();
      cy.get('[data-cy="car-recommendation"]').first().within(() => {
        cy.get('[data-cy="fuel-consumption"]').invoke('text').then(consumption => {
          expect(parseFloat(consumption)).to.be.at.least(12); // Good fuel economy
        });
        cy.get('[data-cy="justification"]').should('contain.text', 'econômico');
      });
    });
  });

  context('Navigation and UX', () => {
    beforeEach(() => {
      cy.startQuestionnaire();
    });

    it('should allow backward navigation through steps', () => {
      // Go to step 2
      cy.fillBudgetStep(40000, 70000, 'Rio de Janeiro', 'RJ');
      cy.clickNext();
      
      // Go back to step 1
      cy.clickPrevious();
      cy.validateStep(0);
      
      // Data should be preserved
      cy.get('[data-cy="city-input"]').should('have.value', 'Rio de Janeiro');
    });

    it('should validate required fields', () => {
      // Try to proceed without filling required fields
      cy.clickNext();
      
      // Should show validation message
      cy.get('[data-cy="validation-message"]').should('be.visible');
      cy.get('[data-cy="next-button"]').should('be.disabled');
    });

    it('should save progress automatically', () => {
      // Fill first step
      cy.fillBudgetStep(60000, 100000, 'Curitiba', 'PR');
      cy.clickNext();
      
      // Refresh page
      cy.reload();
      
      // Should return to correct step with data preserved
      cy.validateStep(1);
      cy.clickPrevious();
      cy.get('[data-cy="city-input"]').should('have.value', 'Curitiba');
    });
  });

  context('Results and Interaction', () => {
    beforeEach(() => {
      // Complete questionnaire quickly
      cy.startQuestionnaire();
      cy.fillBudgetStep(50000, 80000, 'São Paulo', 'SP');
      cy.clickNext();
      cy.fillUsageStep('familia', 'regular');
      cy.clickNext();
      cy.fillFamilyStep(3, true);
      cy.clickNext();
      cy.fillPrioritiesStep({ fuelEconomy: 4, safety: 5, reliability: 4 });
      cy.clickNext();
      cy.fillPreferencesStep(['Toyota'], ['suv']);
      cy.submitQuestionnaire();
      cy.waitForRecommendations();
    });

    it('should display detailed car information', () => {
      // Click on first recommendation
      cy.selectCar(0);
      
      // Validate modal content
      cy.get('[data-cy="car-details-modal"]').within(() => {
        cy.get('[data-cy="car-gallery"]').should('be.visible');
        cy.get('[data-cy="specifications"]').should('be.visible');
        cy.get('[data-cy="pros-cons"]').should('be.visible');
        cy.get('[data-cy="financing-info"]').should('be.visible');
      });
      
      // Close modal
      cy.get('[data-cy="close-modal"]').click();
      cy.get('[data-cy="car-details-modal"]').should('not.exist');
    });

    it('should allow car comparison', () => {
      // Select 2 cars for comparison
      cy.compareCars([0, 1]);
      
      // Validate comparison table
      cy.get('[data-cy="comparison-table"]').within(() => {
        cy.get('[data-cy="compared-car"]').should('have.length', 2);
        cy.get('[data-cy="specification-row"]').should('have.length.at.least', 10);
      });
      
      // Should highlight differences
      cy.get('[data-cy="difference-highlight"]').should('exist');
    });

    it('should allow filtering and sorting results', () => {
      // Apply price filter
      cy.get('[data-cy="price-filter"]').within(() => {
        cy.get('input[type="range"]').first().invoke('val', 55000).trigger('change');
      });
      
      // Results should update
      cy.get('[data-cy="car-recommendation"]').each($card => {
        cy.wrap($card).within(() => {
          cy.get('[data-cy="car-price"]').invoke('text').then(priceText => {
            const price = parseInt(priceText.replace(/\D/g, ''));
            expect(price).to.be.at.least(55000);
          });
        });
      });
      
      // Sort by price
      cy.get('[data-cy="sort-select"]').select('price-asc');
      
      // Validate sorting
      cy.get('[data-cy="car-price"]').then($prices => {
        const prices = Array.from($prices).map(el => 
          parseInt(el.textContent?.replace(/\D/g, '') || '0')
        );
        const sortedPrices = [...prices].sort((a, b) => a - b);
        expect(prices).to.deep.equal(sortedPrices);
      });
    });
  });

  context('Error Handling', () => {
    it('should handle API errors gracefully', () => {
      // Mock API error
      cy.intercept('POST', '**/recommendations', {
        statusCode: 500,
        body: { error: 'Internal server error' }
      }).as('apiError');
      
      // Complete questionnaire
      cy.startQuestionnaire();
      cy.fillBudgetStep(50000, 80000, 'São Paulo', 'SP');
      cy.clickNext();
      cy.fillUsageStep('trabalho', 'diaria');
      cy.clickNext();
      cy.fillFamilyStep(2, false);
      cy.clickNext();
      cy.fillPrioritiesStep({ fuelEconomy: 4 });
      cy.clickNext();
      cy.fillPreferencesStep([], []);
      cy.submitQuestionnaire();
      
      // Should show error message
      cy.get('[data-cy="error-message"]').should('be.visible');
      cy.get('[data-cy="retry-button"]').should('be.visible');
    });

    it('should handle slow API responses', () => {
      // Mock slow API
      cy.intercept('POST', '**/recommendations', {
        delay: 20000,
        body: { recommendations: [] }
      }).as('slowApi');
      
      cy.startQuestionnaire();
      cy.fillBudgetStep(50000, 80000, 'São Paulo', 'SP');
      cy.clickNext();
      cy.fillUsageStep('trabalho', 'diaria');
      cy.clickNext();
      cy.fillFamilyStep(2, false);
      cy.clickNext();
      cy.fillPrioritiesStep({ fuelEconomy: 4 });
      cy.clickNext();
      cy.fillPreferencesStep([], []);
      cy.submitQuestionnaire();
      
      // Should show loading state
      cy.get('[data-cy="loading-recommendations"]').should('be.visible');
      cy.get('[data-cy="loading-message"]').should('contain.text', 'Analisando');
    });
  });

  context('Mobile Responsiveness', () => {
    beforeEach(() => {
      cy.viewport('iphone-x');
    });

    it('should work on mobile devices', () => {
      cy.startQuestionnaire();
      
      // Mobile-specific interactions
      cy.get('[data-cy="mobile-menu"]').should('be.visible');
      cy.get('[data-cy="questionnaire-container"]').should('be.visible');
      
      // Complete questionnaire on mobile
      cy.fillBudgetStep(40000, 60000, 'Porto Alegre', 'RS');
      cy.clickNext();
      
      // Should adapt layout for mobile
      cy.get('[data-cy="step-content"]').should('have.css', 'flex-direction', 'column');
    });
  });

  context('Accessibility', () => {
    it('should be accessible with keyboard navigation', () => {
      cy.startQuestionnaire();
      
      // Navigate with keyboard
      cy.get('body').tab();
      cy.focused().should('have.attr', 'data-cy', 'city-input');
      
      // Complete form with keyboard
      cy.focused().type('Salvador');
      cy.get('body').tab();
      cy.focused().select('BA');
    });

    it('should have proper ARIA labels', () => {
      cy.startQuestionnaire();
      
      cy.get('[data-cy="budget-slider"]').should('have.attr', 'aria-label');
      cy.get('[data-cy="next-button"]').should('have.attr', 'aria-describedby');
    });
  });

  context('Performance', () => {
    it('should load quickly', () => {
      const start = Date.now();
      
      cy.visitHomePage();
      cy.get('[data-cy="hero-title"]').should('be.visible');
      
      cy.then(() => {
        const loadTime = Date.now() - start;
        expect(loadTime).to.be.lessThan(3000); // 3 seconds max
      });
    });

    it('should handle large datasets efficiently', () => {
      // Mock large dataset
      cy.fixture('large-car-dataset.json').then(cars => {
        cy.intercept('POST', '**/recommendations', {
          body: { recommendations: cars.slice(0, 100) }
        });
      });
      
      cy.startQuestionnaire();
      cy.fillBudgetStep(20000, 200000, 'São Paulo', 'SP');
      cy.clickNext();
      cy.fillUsageStep('trabalho', 'diaria');
      cy.clickNext();
      cy.fillFamilyStep(2, false);
      cy.clickNext();
      cy.fillPrioritiesStep({ fuelEconomy: 3 });
      cy.clickNext();
      cy.fillPreferencesStep([], []);
      cy.submitQuestionnaire();
      
      // Should render without performance issues
      cy.waitForRecommendations();
      cy.get('[data-cy="car-recommendation"]').should('have.length.at.least', 10);
    });
  });

  context('Analytics and Tracking', () => {
    it('should track user interactions', () => {
      // Mock analytics
      cy.window().then(win => {
        win.analytics = {
          track: cy.stub().as('analyticsTrack')
        };
      });
      
      cy.startQuestionnaire();
      cy.get('@analyticsTrack').should('have.been.calledWith', 'questionnaire_started');
      
      cy.fillBudgetStep(50000, 80000, 'São Paulo', 'SP');
      cy.clickNext();
      cy.get('@analyticsTrack').should('have.been.calledWith', 'step_completed', { step: 1 });
    });
  });
});
