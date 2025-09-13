import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 15000,
    responseTimeout: 15000,
    
    // Spec patterns
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.ts',
    fixturesFolder: 'cypress/fixtures',
    screenshotsFolder: 'cypress/screenshots',
    videosFolder: 'cypress/videos',
    
    // Environment variables
    env: {
      API_URL: 'http://localhost:5000/api/v1',
      TEST_USER_EMAIL: 'test@carmatch.com',
      TEST_USER_PASSWORD: 'TestPassword123!',
    },
    
    setupNodeEvents(on, config) {
      // Task for database seeding
      on('task', {
        // Seed test data
        seedDatabase() {
          return require('./cypress/tasks/seedDatabase').seedTestData();
        },
        
        // Clear test data
        clearDatabase() {
          return require('./cypress/tasks/seedDatabase').clearTestData();
        },
        
        // Get test data
        getTestCars() {
          return require('./cypress/fixtures/cars.json');
        },
        
        // Log to console during tests
        log(message) {
          console.log(message);
          return null;
        },
      });
      
      // Code coverage
      require('@cypress/code-coverage/task')(on, config);
      
      return config;
    },
  },
  
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
    specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/component.ts',
  },
  
  // Global configuration
  experimentalStudio: true,
  chromeWebSecurity: false,
  retries: {
    runMode: 2,
    openMode: 0,
  },
});
