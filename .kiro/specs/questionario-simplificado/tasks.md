# Implementation Plan: Questionário com Capacidade Financeira

## Visão Geral

Adicionar pergunta sobre faixa salarial mensal no questionário existente (Step 2) para calcular TCO e recomendar carros dentro do orçamento do usuário.

---

## Tasks

- [x] 1. Adicionar campo de faixa salarial no frontend





  - Modificar Step2Usage.tsx para incluir nova seção de capacidade financeira
  - Adicionar campo `faixa_salarial` no questionnaireStore
  - Implementar UI com Radio buttons e mensagem de privacidade
  - Garantir que campo seja opcional (pode pular)
  - _Requirements: 6.1, 6.5_

- [x] 2. Implementar modelos de dados no backend






  - Criar classe `FinancialCapacity` em models/user_profile.py
  - Adicionar campo `financial_capacity` ao `UserProfile`
  - Criar classe `TCOBreakdown` para detalhamento de custos
  - Atualizar `CarRecommendation` para incluir informações de TCO
  - _Requirements: 6.2, 6.4_

- [x] 3. Implementar calculadora de TCO






  - Criar módulo `services/tco_calculator.py`
  - Implementar cálculo de financiamento (Tabela Price)
  - Implementar cálculo de combustível mensal
  - Implementar estimativa de manutenção por categoria
  - Implementar estimativa de seguro
  - Implementar cálculo de IPVA por estado
  - _Requirements: 6.2, 6.4_

- [x] 4. Integrar TCO no motor de recomendação






  - Modificar `UnifiedRecommendationEngine` para calcular TCO
  - Implementar filtragem por capacidade financeira (max_tco)
  - Aplicar bonus de score para carros que cabem no orçamento
  - Adicionar TCO breakdown nas recomendações retornadas
  - _Requirements: 6.2, 6.3_

- [x] 5. Exibir TCO nos resultados





  - Criar componente `TCOBreakdownCard` no frontend
  - Adicionar badge "Cabe no orçamento" nos cards de carros
  - Exibir detalhamento de custos (expansível)
  - Mostrar percentual do orçamento usado
  - _Requirements: 6.4_

- [x] 6. Implementar garantias de privacidade
  - Garantir que dados financeiros não sejam persistidos
  - Adicionar modal de política de privacidade
  - Implementar logs anônimos (apenas analytics)
  - Adicionar texto de consentimento claro
  - _Requirements: 6.6_

- [ ]* 7. Testes e validação
  - Escrever testes unitários para cálculos de TCO
  - Escrever testes de integração para filtragem financeira
  - Escrever testes E2E para fluxo completo
  - Validar cálculos com dados reais de mercado
  - _Requirements: 6.2, 6.3, 6.4_

- [ ]* 8. Documentação e métricas
  - Documentar API de TCO
  - Adicionar métricas de disclosure rate
  - Configurar tracking de conversão com/sem TCO
  - Criar dashboard de analytics
  - _Requirements: 6.4_

---

## Notas de Implementação

### Prioridade de Execução

1. **Tasks 1-2**: Estrutura de dados (frontend + backend)
2. **Task 3**: Lógica de cálculo de TCO
3. **Task 4**: Integração com motor de recomendação
4. **Task 5**: Exibição nos resultados
5. **Task 6**: Privacidade e compliance
6. **Tasks 7-8**: Testes e documentação (opcional)

### Dados de Mercado Necessários

- **Consumo de combustível**: Já existe no modelo `Car`
- **Custos de manutenção**: Criar tabela por categoria
- **Taxas de seguro**: Criar estimativas por categoria e preço
- **Alíquotas de IPVA**: Criar tabela por estado
- **Taxa de financiamento**: Usar 12% a.a. como padrão

### Arquivos a Modificar

**Frontend**:
- `platform/frontend/src/components/questionnaire/Step2Usage.tsx`
- `platform/frontend/src/store/questionnaireStore.ts`
- `platform/frontend/src/types/index.ts`
- `platform/frontend/src/components/results/` (novos componentes)

**Backend**:
- `platform/backend/models/user_profile.py`
- `platform/backend/services/tco_calculator.py` (novo)
- `platform/backend/services/unified_recommendation_engine.py`
- `platform/backend/api/main.py` (atualizar response models)

---

**Criado em**: 5 de Novembro, 2025  
**Versão**: 1.0  
**Status**: 📋 TASKS DEFINIDAS
