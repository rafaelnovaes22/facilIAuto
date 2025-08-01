/**
 * 🧪 Playwright Configuration - FacilIAuto E2E Tests
 * Configuração para testes end-to-end
 */

const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  // Diretório de testes E2E
  testDir: './tests/e2e',
  
  // Timeout global
  timeout: 30000,
  
  // Timeout para expect
  expect: {
    timeout: 5000
  },
  
  // Configurações globais
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }]
  ],
  
  // Configurações de uso
  use: {
    // URL base da aplicação
    baseURL: 'http://localhost:8000',
    
    // Trace em caso de falha
    trace: 'on-first-retry',
    
    // Screenshot em falhas
    screenshot: 'only-on-failure',
    
    // Video em falhas
    video: 'retain-on-failure',
    
    // Locale brasileiro
    locale: 'pt-BR',
    timezoneId: 'America/Sao_Paulo'
  },
  
  // Projetos para diferentes navegadores
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    // Testes mobile
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
    
    // Tablet
    {
      name: 'Tablet',
      use: { ...devices['iPad Pro'] },
    }
  ],
  
  // Servidor local para testes
  webServer: {
    command: 'python main.py',
    port: 8000,
    reuseExistingServer: !process.env.CI,
    timeout: 120000
  }
});