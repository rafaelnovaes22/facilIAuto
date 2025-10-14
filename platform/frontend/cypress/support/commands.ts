// Cypress custom commands
/// <reference types="cypress" />

// Command para preencher questionário
Cypress.Commands.add('fillQuestionnaire', (data = {}) => {
  const defaults = {
    orcamentoMin: 50000,
    orcamentoMax: 100000,
    city: 'São Paulo',
    state: 'SP',
    usoPrincipal: 'familia',
    tamanhoFamilia: 4,
    temCriancas: true,
    temIdosos: false,
  }

  const config = { ...defaults, ...data }

  // Step 1: Orçamento
  cy.get('input[type="number"]').first().clear().type(String(config.orcamentoMin))
  cy.get('input[type="number"]').eq(1).clear().type(String(config.orcamentoMax))
  
  if (config.state) {
    cy.get('select').first().select(config.state)
  }
  
  if (config.city) {
    cy.get('input[placeholder*="São Paulo"]').type(config.city)
  }

  cy.contains('button', 'Próximo').click()

  // Step 2: Uso e Família
  cy.contains(`label`, config.usoPrincipal === 'familia' ? 'Família' : 'Trabalho').click()
  
  cy.get('input[type="number"]').clear().type(String(config.tamanhoFamilia))

  if (config.temCriancas) {
    cy.contains('Tem crianças?').parent().find('button').click()
  }

  if (config.temIdosos) {
    cy.contains('Tem idosos?').parent().find('button').click()
  }

  cy.contains('button', 'Próximo').click()

  // Step 3: Prioridades (usar valores default)
  cy.contains('button', 'Próximo').click()

  // Step 4: Preferências (pular)
  // Clicar em "Ver Recomendações"
  cy.contains('button', 'Ver Recomendações').should('be.visible')
})

// Declaração de tipos TypeScript
declare global {
  namespace Cypress {
    interface Chainable {
      fillQuestionnaire(data?: Partial<{
        orcamentoMin: number
        orcamentoMax: number
        city: string
        state: string
        usoPrincipal: string
        tamanhoFamilia: number
        temCriancas: boolean
        temIdosos: boolean
      }>): Chainable<void>
    }
  }
}

export {}

