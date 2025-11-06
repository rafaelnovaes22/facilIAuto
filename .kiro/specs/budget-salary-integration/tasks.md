# Implementation Plan

## Overview

Este plano de implementação detalha as tarefas necessárias para corrigir a integração entre a faixa de salário e o cálculo de TCO. As tarefas estão organizadas em 4 fases sequenciais, com cada fase construindo sobre a anterior.

## Tasks

- [x] 1. Frontend: Criar componente de seleção de faixa salarial





  - Criar novo componente `SalaryRangeSelector.tsx` com radio buttons para as 5 faixas salariais
  - Adicionar opção "Prefiro não informar" que retorna `null`
  - Exibir TCO máximo recomendado (30% da renda média) ao selecionar uma faixa
  - Adicionar tooltip explicando por que pedimos essa informação
  - Estilizar com Chakra UI seguindo design system existente
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Frontend: Implementar lógica de cálculo de capacidade financeira





  - [x] 2.1 Criar helper function `calculateFinancialCapacity()`


    - Implementar mapeamento de faixas salariais para intervalos numéricos
    - Calcular renda média: `(min + max) / 2`
    - Calcular TCO máximo: `renda_média * 0.30`
    - Retornar objeto `FinancialCapacity` ou `null`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 2.2 Atualizar `toUserProfile()` no Questionnaire Store


    - Chamar `calculateFinancialCapacity(formData.faixa_salarial)`
    - Adicionar resultado ao campo `financial_capacity` do `UserProfile`
    - Garantir que `financial_capacity` seja `null` quando não informado
    - _Requirements: 2.1, 2.6_


  - [x] 2.3 Atualizar tipos TypeScript

    - Adicionar interface `FinancialCapacity` em `types/index.ts`
    - Adicionar campo `financial_capacity` ao tipo `UserProfile`
    - Garantir compatibilidade com backend Python
    - _Requirements: 6.1_

- [x] 3. Frontend: Integrar seletor no Step1Budget





  - Importar `SalaryRangeSelector` component
  - Adicionar handler `handleSalaryChange` que atualiza `formData.faixa_salarial`
  - Posicionar seletor após `YearSelector` e antes de `LocationSelector`
  - Adicionar `Divider` para separação visual
  - _Requirements: 1.1, 1.5_

- [x] 4. Backend: Adicionar validação de financial_capacity






  - Adicionar validação no endpoint `POST /recommend` em `api/main.py`
  - Validar que `monthly_income_range` está em lista de opções válidas
  - Validar que `max_monthly_tco` é positivo quando fornecido
  - Validar consistência: se `is_disclosed=true`, `monthly_income_range` deve existir
  - Retornar HTTP 400 com mensagens descritivas para erros de validação
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 5. Frontend: Atualizar exibição de resultados





  - [x] 5.1 Adicionar tags de status de orçamento no CarCard


    - Exibir badge verde "✓ Dentro do orçamento" quando `fits_budget === true`
    - Exibir badge amarelo "⚠ Acima do orçamento" quando `fits_budget === false`
    - Não exibir badge quando `fits_budget === null`
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 5.2 Adicionar tooltip com detalhamento de TCO


    - Criar tooltip que exibe breakdown completo do TCO
    - Mostrar: Financiamento, Combustível, Manutenção, Seguro, IPVA, Total
    - Exibir tooltip ao passar mouse sobre ícone de informação
    - _Requirements: 4.4_

  - [x] 5.3 Adicionar indicador de saúde financeira


    - Exibir ícone verde quando `financial_health.status === "healthy"`
    - Exibir ícone amarelo quando `financial_health.status === "caution"`
    - Exibir ícone vermelho quando `financial_health.status === "high_commitment"`
    - Adicionar tooltip explicando o status
    - _Requirements: 4.5_

- [ ]* 6. Testes: Frontend unit tests
  - Criar `calculateFinancialCapacity.test.ts` com testes para todas as faixas
  - Testar cálculo correto de `max_monthly_tco` para cada faixa
  - Testar retorno de `null` quando faixa não é informada
  - Testar comportamento com faixas inválidas
  - Garantir cobertura >= 80%
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 7. Testes: Backend integration tests
  - Criar `test_budget_salary_integration.py`
  - Testar recomendações com `financial_capacity.is_disclosed = true`
  - Testar recomendações com `financial_capacity.is_disclosed = false`
  - Testar validação de API com faixas inválidas
  - Testar que `fits_budget` é calculado corretamente
  - Garantir cobertura >= 80%
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 8. Testes: E2E tests com Cypress
  - Criar `budget-salary-flow.cy.ts`
  - Testar fluxo completo: selecionar salário → ver tags de orçamento
  - Testar fluxo sem salário: pular → não ver tags
  - Testar que TCO é exibido corretamente nos tooltips
  - Testar que indicadores de saúde financeira aparecem
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 9. Validação e QA
  - Executar todos os testes (unit, integration, E2E)
  - Testar manualmente fluxo completo no navegador
  - Verificar que tags aparecem apenas quando salário é informado
  - Verificar cálculos de TCO máximo para todas as faixas
  - Testar com diferentes perfis de usuário
  - Verificar logs de erro no backend
  - Validar que não há regressões em funcionalidades existentes
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3_

## Implementation Notes

### Ordem de Execução

As tarefas devem ser executadas na ordem apresentada:
1. **Tasks 1-3:** Frontend data collection (pode ser feito em paralelo)
2. **Task 4:** Backend validation (depende de 2.3 para tipos)
3. **Task 5:** Frontend display (depende de 1-4)
4. **Tasks 6-8:** Testing (pode ser feito em paralelo após 1-5)
5. **Task 9:** Final validation (depende de tudo)

### Testing Strategy

- **Unit tests** são opcionais mas recomendados para garantir qualidade
- **Integration tests** são opcionais mas recomendados para validar API
- **E2E tests** são opcionais mas recomendados para validar fluxo completo
- Todos os testes marcados com `*` podem ser pulados para MVP mais rápido

### Key Files to Modify

**Frontend:**
- `platform/frontend/src/components/questionnaire/SalaryRangeSelector.tsx` (novo)
- `platform/frontend/src/store/questionnaireStore.ts` (modificar)
- `platform/frontend/src/types/index.ts` (modificar)
- `platform/frontend/src/components/questionnaire/Step1Budget.tsx` (modificar)
- `platform/frontend/src/components/results/CarCard.tsx` (modificar)

**Backend:**
- `platform/backend/api/main.py` (modificar)

**Tests:**
- `platform/frontend/src/store/__tests__/questionnaireStore.test.ts` (novo)
- `platform/backend/tests/test_budget_salary_integration.py` (novo)
- `platform/frontend/cypress/e2e/budget-salary-flow.cy.ts` (novo)

### Estimated Time

- Task 1: 2-3 hours
- Task 2: 2-3 hours
- Task 3: 1 hour
- Task 4: 1-2 hours
- Task 5: 2-3 hours
- Task 6: 2 hours (opcional)
- Task 7: 2 hours (opcional)
- Task 8: 2 hours (opcional)
- Task 9: 2 hours

**Total:** 12-16 hours (core) + 6 hours (tests) = 18-22 hours (~3-4 days)

### Success Criteria

- [ ] Usuário pode selecionar faixa salarial no Step 1
- [ ] TCO máximo é calculado corretamente (30% da renda média)
- [ ] `financial_capacity` é enviado ao backend quando informado
- [ ] Tags de orçamento aparecem apenas quando salário é informado
- [ ] Tags mostram "Dentro" ou "Acima" do orçamento corretamente
- [ ] Tooltips exibem breakdown completo do TCO
- [ ] Indicadores de saúde financeira aparecem corretamente
- [ ] Backend valida `financial_capacity` e retorna erros apropriados
- [ ] Todos os testes passam (se implementados)
- [ ] Não há regressões em funcionalidades existentes
