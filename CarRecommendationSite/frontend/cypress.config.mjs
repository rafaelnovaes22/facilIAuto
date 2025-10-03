import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    // Remove baseUrl para testes offline
    // baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 5000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    
    // Spec patterns
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: false,
    fixturesFolder: 'cypress/fixtures',
    screenshotsFolder: 'cypress/screenshots',
    videosFolder: 'cypress/videos',
    
    // Environment variables
    env: {
      API_URL: 'http://localhost:5000/api/v1',
    },
    
    setupNodeEvents(on, config) {
      // Simple task setup
      on('task', {
        log(message) {
          console.log(message);
          return null;
        },
      });
      
      return config;
    },
  },
  
  // Global configuration
  chromeWebSecurity: false,
  retries: {
    runMode: 0,
    openMode: 0,
  },
});