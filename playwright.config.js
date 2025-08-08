// 🎭 Configuração Playwright - Smoke Test Apenas
// Configuração minimalista para 1 teste crítico

module.exports = {
  testDir: './tests/e2e',
  timeout: 60000, // 60s timeout total
  expect: {
    timeout: 30000 // 30s timeout para expects
  },
  fullyParallel: false, // Apenas 1 teste, não precisa de paralelismo
  forbidOnly: !!process.env.CI, // Não permitir .only em CI
  retries: process.env.CI ? 2 : 1, // Retry em CI
  workers: 1, // Apenas 1 worker para smoke test
  reporter: [
    ['list'],
    ['html', { outputFolder: 'smoke-test-results' }]
  ],
  
  // Configuração global
  use: {
    baseURL: 'http://localhost:8000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 30000,
    navigationTimeout: 30000,
  },

  // Configuração de browsers - apenas Chromium para smoke test
  projects: [
    {
      name: 'chromium',
      use: { ...require('@playwright/test').devices['Desktop Chrome'] },
    }
  ],

  // Servidor local (opcional)
  webServer: {
    command: 'python main.py',
    port: 8000,
    reuseExistingServer: !process.env.CI,
    timeout: 120000, // 2 minutos para iniciar
  },
};
