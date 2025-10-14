// Cypress E2E support file
/// <reference types="cypress" />

// Import commands
import './commands'

// Custom error handling
Cypress.on('uncaught:exception', (err, runnable) => {
  // Returning false prevents Cypress from failing the test
  // Ajustar conforme necessário
  return false
})

