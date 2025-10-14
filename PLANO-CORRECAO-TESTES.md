# Plano de Correção dos Erros de Testes

## Resumo da Análise
- **Total de testes**: 27 arquivos de teste
- **Testes passando**: 22 testes (questionnaireStore, CarCard)
- **Testes falhando**: 14 testes distribuídos em 3 arquivos principais
- **Warnings**: Múltiplos warnings de `act()` e `scrollTo()`

## Problemas Identificados por Prioridade

### 🔴 CRÍTICO - Prioridade 1

#### 1. Configuração do Tema Chakra UI
**Problema**: `TypeError: Cannot use 'in' operator to search for 'colors.brand.50' in undefined`
- **Arquivos afetados**: `src/pages/__tests__/HomePage.test.tsx` (9 testes)
- **Causa**: Tema customizado não carregado nos testes
- **Impacto**: 9 testes falhando

### 🟡 MÉDIO - Prioridade 2

#### 2. Teste de Error Handling da API
**Problema**: `× should handle health check error`
- **Arquivo afetado**: `src/hooks/__tests__/useApi.test.tsx`
- **Causa**: Mock ou expectativa incorreta no tratamento de erro
- **Impacto**: 1 teste falhando

#### 3. Testes de Navegação do Questionário
**Problema**: Múltiplos testes de navegação falhando
- **Arquivo afetado**: `src/pages/__tests__/QuestionnairePage.test.tsx`
- **Testes falhando**: 4 testes
- **Causa**: Estado de navegação ou mocks incorretos

### 🟢 BAIXO - Prioridade 3

#### 4. Warnings de React Testing
**Problema**: `Warning: An update to [Component] inside a test was not wrapped in act(...)`
- **Arquivos afetados**: Múltiplos componentes
- **Causa**: Atualizações de estado não envolvidas em `act()`
- **Impacto**: Warnings (não quebra funcionalidade)

#### 5. Mock de scrollTo
**Problema**: `Not implemented: Window's scrollTo() method`
- **Causa**: Método não mockado no ambiente de teste
- **Impacto**: Warning (não quebra funcionalidade)

## Plano de Correção Detalhado

### Fase 1: Correções Críticas (Prioridade 1)

#### Tarefa 1.1: Corrigir Configuração do Tema Chakra UI
**Tempo estimado**: 30 minutos

**Ações**:
1. Verificar arquivo de tema customizado
2. Garantir que as cores `brand.50` e `brand.500` estão definidas
3. Atualizar setup de testes para incluir tema completo
4. Verificar se `ChakraProvider` está configurado corretamente nos testes

**Arquivos a modificar**:
- `src/theme/index.ts` (verificar definição das cores)
- `src/pages/__tests__/HomePage.test.tsx` (setup do teste)
- Possível arquivo de setup global de testes

### Fase 2: Correções Médias (Prioridade 2)

#### Tarefa 2.1: Corrigir Teste de Error Handling da API
**Tempo estimado**: 20 minutos

**Ações**:
1. Analisar o teste `should handle health check error`
2. Verificar mock da API e expectativas
3. Corrigir lógica de tratamento de erro
4. Validar comportamento esperado vs atual

**Arquivos a modificar**:
- `src/hooks/__tests__/useApi.test.tsx`

#### Tarefa 2.2: Corrigir Testes de Navegação do Questionário
**Tempo estimado**: 45 minutos

**Ações**:
1. Analisar cada teste falhando individualmente:
   - `should render progress indicator`
   - `should have Voltar button disabled on first step`
   - `should go back to previous step when Voltar is clicked`
   - `should show "Ver Recomendações" button on last step`
2. Verificar estado inicial do store
3. Corrigir mocks e expectativas
4. Validar lógica de navegação

**Arquivos a modificar**:
- `src/pages/__tests__/QuestionnairePage.test.tsx`

### Fase 3: Melhorias (Prioridade 3)

#### Tarefa 3.1: Corrigir Warnings de act()
**Tempo estimado**: 30 minutos

**Ações**:
1. Identificar todas as atualizações de estado nos testes
2. Envolver mudanças de estado em `act()`
3. Usar `waitFor` quando necessário para operações assíncronas

**Arquivos a modificar**:
- `src/components/questionnaire/__tests__/Step1Budget.test.tsx`
- `src/components/questionnaire/__tests__/Step2Usage.test.tsx`
- `src/components/questionnaire/__tests__/Step3Priorities.test.tsx`
- `src/pages/__tests__/QuestionnairePage.test.tsx`

#### Tarefa 3.2: Adicionar Mock para scrollTo
**Tempo estimado**: 10 minutos

**Ações**:
1. Adicionar mock global para `window.scrollTo`
2. Configurar no setup de testes

**Arquivos a modificar**:
- Setup global de testes ou arquivo de configuração do Vitest

## Cronograma de Execução

### Dia 1 (2 horas)
- ✅ Fase 1: Correção do tema Chakra UI (30 min)
- ✅ Fase 2.1: Correção do teste de API (20 min)
- ✅ Fase 2.2: Correção dos testes de navegação (45 min)
- ✅ Validação das correções (25 min)

### Dia 2 (40 minutos)
- ✅ Fase 3.1: Correção dos warnings de act() (30 min)
- ✅ Fase 3.2: Mock do scrollTo (10 min)

## Critérios de Sucesso

### Metas Quantitativas
- [ ] 100% dos testes passando (27/27)
- [ ] 0 erros críticos
- [ ] Redução de warnings para < 5

### Metas Qualitativas
- [ ] Tema Chakra UI funcionando em todos os testes
- [ ] Cobertura de error handling validada
- [ ] Navegação do questionário testada completamente
- [ ] Testes executando sem warnings desnecessários

## Validação Final

### Comandos de Teste
```bash
# Executar todos os testes
npm test -- --run

# Executar com coverage
npm test -- --run --coverage

# Executar testes específicos
npm test HomePage.test.tsx -- --run
npm test QuestionnairePage.test.tsx -- --run
npm test useApi.test.tsx -- --run
```

### Checklist de Validação
- [ ] Todos os testes passando
- [ ] Sem erros de tema/cores
- [ ] API error handling funcionando
- [ ] Navegação do questionário funcionando
- [ ] Warnings minimizados
- [ ] Performance dos testes aceitável (< 10s total)

## Riscos e Mitigações

### Risco 1: Tema complexo demais para testes
**Mitigação**: Criar tema simplificado para testes ou mock das cores

### Risco 2: Dependências de estado complexas
**Mitigação**: Usar mocks mais específicos e resetar estado entre testes

### Risco 3: Testes assíncronos instáveis
**Mitigação**: Usar `waitFor` e timeouts apropriados

## Próximos Passos

1. **Executar Fase 1** - Corrigir problema crítico do tema
2. **Validar correção** - Executar testes da HomePage
3. **Continuar com Fase 2** - Corrigir testes médios
4. **Finalizar com Fase 3** - Melhorias e warnings
5. **Documentar soluções** - Para referência futura