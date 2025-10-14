// 🎨 UX Especialist: E2E test - HomePage
describe('HomePage', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should render homepage correctly', () => {
    // Hero section
    cy.contains('FacilIAuto').should('be.visible')
    cy.contains('Encontre o Carro Perfeito em 3 Minutos').should('be.visible')
    cy.contains('Recomendação inteligente').should('be.visible')

    // CTA button
    cy.contains('button', 'Começar Agora').should('be.visible')

    // Trust indicators
    cy.contains('3 minutos').should('be.visible')
    cy.contains('100% gratuito').should('be.visible')
    cy.contains('Personalizado').should('be.visible')
  })

  it('should load and display stats from API', () => {
    // Stats cards (podem demorar pela API)
    cy.contains('Carros Disponíveis', { timeout: 10000 }).should('be.visible')
    cy.contains('Concessionárias').should('be.visible')
    cy.contains('Preço Médio').should('be.visible')
  })

  it('should navigate to questionnaire on CTA click', () => {
    cy.contains('button', 'Começar Agora').first().click()
    cy.url().should('include', '/questionario')
  })

  it('should show "Como Funciona" section', () => {
    cy.contains('Como Funciona?').should('be.visible')
    cy.contains('Responda o Questionário').should('be.visible')
    cy.contains('IA Analisa e Recomenda').should('be.visible')
    cy.contains('Receba Recomendações').should('be.visible')
  })

  it('should show features section', () => {
    cy.contains('Por Que FacilIAuto?').should('be.visible')
    cy.contains('Recomendações Personalizadas').should('be.visible')
    cy.contains('Rápido e Fácil').should('be.visible')
    cy.contains('Múltiplas Concessionárias').should('be.visible')
    cy.contains('Contato Direto').should('be.visible')
  })

  it('should show footer', () => {
    cy.contains('FacilIAuto').should('be.visible')
    cy.contains('2024 FacilIAuto').should('be.visible')
  })

  it('should have both CTAs working', () => {
    // CTA principal (hero)
    cy.contains('button', 'Começar Agora').first().click()
    cy.url().should('include', '/questionario')

    // Voltar
    cy.go('back')

    // Scroll até CTA final
    cy.scrollTo('bottom')

    // CTA final
    cy.contains('button', 'Começar Gratuitamente').click()
    cy.url().should('include', '/questionario')
  })

  it('should be responsive on mobile', () => {
    cy.viewport('iphone-x')

    cy.contains('FacilIAuto').should('be.visible')
    cy.contains('Começar Agora').should('be.visible')

    // Verificar que layout está adequado
    cy.get('body').should('be.visible')
  })

  it('should be responsive on tablet', () => {
    cy.viewport('ipad-2')

    cy.contains('FacilIAuto').should('be.visible')
    cy.contains('Começar Agora').should('be.visible')
  })
})

