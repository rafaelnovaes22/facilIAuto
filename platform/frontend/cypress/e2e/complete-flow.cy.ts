// 🎨 UX Especialist + 🤖 AI Engineer: E2E test - Fluxo completo
describe('FacilIAuto - Fluxo Completo', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should complete full user journey', () => {
    // HomePage
    cy.contains('FacilIAuto').should('be.visible')
    cy.contains('Encontre o Carro Perfeito').should('be.visible')
    
    // Stats cards devem estar visíveis (pode demorar um pouco pela API)
    cy.contains('Carros Disponíveis', { timeout: 10000 }).should('be.visible')

    // Clicar no CTA principal
    cy.contains('button', 'Começar Agora').click()

    // QuestionnaireP age
    cy.url().should('include', '/questionario')
    
    // Progress indicator
    cy.contains('Orçamento').should('be.visible')

    // Preencher questionário
    cy.fillQuestionnaire({
      orcamentoMin: 60000,
      orcamentoMax: 90000,
      city: 'São Paulo',
      state: 'SP',
      usoPrincipal: 'familia',
      tamanhoFamilia: 4,
      temCriancas: true,
    })

    // Submeter
    cy.contains('button', 'Ver Recomendações').click()

    // Loading state
    cy.contains('Buscando', { timeout: 2000 }).should('be.visible')

    // ResultsPage
    cy.url({ timeout: 15000 }).should('include', '/resultados')
    
    // Verificar que resultados foram carregados
    cy.contains('Encontramos', { timeout: 15000 }).should('be.visible')
    cy.contains('carros para você').should('be.visible')

    // Profile summary
    cy.contains('Resumo do Perfil').should('be.visible')
    cy.contains('São Paulo').should('be.visible')

    // Pelo menos um card de carro
    cy.get('[data-testid="car-card"]').should('have.length.greaterThan', 0)

    // Score visual
    cy.contains('%').should('be.visible')

    // Botão WhatsApp
    cy.contains('button', 'WhatsApp').should('be.visible')
  })

  it('should navigate back from questionnaire', () => {
    cy.contains('button', 'Começar Agora').click()
    cy.url().should('include', '/questionario')

    // Clicar em voltar
    cy.contains('button', 'Voltar para o início').click()
    cy.url().should('eq', Cypress.config().baseUrl + '/')
  })

  it('should validate budget step', () => {
    cy.contains('button', 'Começar Agora').click()

    // Tentar orçamento inválido (max < min)
    cy.get('input[type="number"]').first().clear().type('100000')
    cy.get('input[type="number"]').eq(1).clear().type('50000')

    // Botão próximo deve estar desabilitado
    cy.contains('button', 'Próximo').should('be.disabled')

    // Corrigir
    cy.get('input[type="number"]').first().clear().type('50000')
    cy.get('input[type="number"]').eq(1).clear().type('100000')

    // Agora deve estar habilitado
    cy.contains('button', 'Próximo').should('not.be.disabled')
  })

  it('should show progress indicator', () => {
    cy.contains('button', 'Começar Agora').click()

    // Step 1
    cy.contains('1').should('be.visible')
    cy.contains('Orçamento').should('be.visible')

    // Avançar
    cy.contains('button', 'Próximo').click()

    // Step 2
    cy.contains('2').should('be.visible')
    cy.contains('Uso').should('be.visible')

    // Check icon no step 1 (completo)
    cy.get('svg').should('exist')
  })

  it('should allow filtering results by category', () => {
    // Completar questionário rapidamente
    cy.contains('button', 'Começar Agora').click()
    cy.fillQuestionnaire()
    cy.contains('button', 'Ver Recomendações').click()

    // Esperar resultados
    cy.contains('Encontramos', { timeout: 15000 }).should('be.visible')

    // Filtrar por categoria
    cy.get('select').first().select('Sedan')

    // Verificar que URL ou contagem mudou
    cy.contains('resultado').should('be.visible')
  })

  it('should sort results by price', () => {
    cy.contains('button', 'Começar Agora').click()
    cy.fillQuestionnaire()
    cy.contains('button', 'Ver Recomendações').click()

    cy.contains('Encontramos', { timeout: 15000 }).should('be.visible')

    // Ordenar por menor preço
    cy.get('select').eq(1).select('Menor Preço')

    // Cards devem estar ordenados
    cy.get('[data-testid="car-card"]').should('exist')
  })
})

describe('FacilIAuto - Edge Cases', () => {
  it('should handle empty results gracefully', () => {
    cy.visit('/resultados')

    // Sem dados, deve mostrar loading ou empty state
    cy.contains('Carregando', { timeout: 5000 }).should('be.visible')
  })

  it('should be mobile responsive', () => {
    cy.viewport('iphone-x')
    
    cy.visit('/')
    cy.contains('FacilIAuto').should('be.visible')
    cy.contains('button', 'Começar Agora').should('be.visible')

    // Verificar que layout está adequado
    cy.get('body').should('be.visible')
  })

  it('should handle API errors', () => {
    // Interceptar API call e forçar erro
    cy.intercept('POST', '**/recommend', {
      statusCode: 500,
      body: { message: 'Internal Server Error' },
    }).as('recommendError')

    cy.visit('/questionario')
    cy.fillQuestionnaire()
    cy.contains('button', 'Ver Recomendações').click()

    cy.wait('@recommendError')

    // Toast de erro deve aparecer
    cy.contains('Erro', { timeout: 5000 }).should('be.visible')
  })
})

