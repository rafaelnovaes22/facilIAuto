# Remoção de Pergunta Duplicada sobre Renda

## Problema Identificado

A pergunta sobre **faixa de renda mensal** estava aparecendo em **dois lugares diferentes** no questionário:

1. **Step 1 (Orçamento)**: Componente `SalaryRangeSelector`
2. **Step 2 (Uso e Família)**: Seção "💰 Qual sua renda mensal? (Opcional)"

Isso causava:
- ❌ Confusão para o usuário (pergunta repetida)
- ❌ Redundância no fluxo
- ❌ Experiência ruim (usuário responde 2x a mesma coisa)

## Análise Técnica

### Backend (Integrado) ✅
- Usa `financial_capacity.monthly_income_range`
- Validação em `platform/backend/api/main.py`
- Modelo em `platform/backend/models/user_profile.py`

### Frontend
- **Ambos os steps** salvavam em `formData.faixa_salarial`
- **Store** converte `faixa_salarial` → `financial_capacity.monthly_income_range`
- **Integração funcionando corretamente** ✅

## Decisão: Manter Apenas no Step 2

### Por que Step 2 é melhor?

1. **Contexto apropriado**: Está junto com informações de família e uso
2. **Marcada como opcional**: "💰 Qual sua renda mensal? (Opcional)"
3. **Explicação clara**: "Ajuda a mostrar quanto você vai gastar por mês..."
4. **Badge de privacidade**: Tranquiliza o usuário sobre segurança dos dados
5. **Mostra benefício**: Exibe custo mensal estimado para cada faixa
6. **UX superior**: Mais informações e contexto para o usuário decidir

### Por que remover do Step 1?

- Step 1 é focado em **orçamento e localização**
- Pergunta de renda não tem contexto claro ali
- Sem explicação sobre privacidade
- Sem mostrar benefício da informação

## Alterações Realizadas

### Arquivo Modificado
`platform/frontend/src/components/questionnaire/Step1Budget.tsx`

### Mudanças

1. **Removido import**:
```typescript
// ANTES
import { SalaryRangeSelector } from './SalaryRangeSelector'

// DEPOIS
// (removido)
```

2. **Removido handler**:
```typescript
// ANTES
const handleSalaryChange = (range: string | null) => {
  updateFormData({ faixa_salarial: range })
}

// DEPOIS
// (removido)
```

3. **Removido componente do JSX**:
```typescript
// ANTES
<SalaryRangeSelector
  value={formData.faixa_salarial || null}
  onChange={handleSalaryChange}
/>

// DEPOIS
// (removido)
```

## Componente Mantido

### Step 2 - Seção de Renda (Mantida)
`platform/frontend/src/components/questionnaire/Step2Usage.tsx`

Características:
- ✅ Título claro: "💰 Qual sua renda mensal? (Opcional)"
- ✅ Explicação do benefício
- ✅ Badge de privacidade com ícone de cadeado
- ✅ Opção "Prefiro não informar" (padrão)
- ✅ 5 faixas salariais com custo mensal estimado
- ✅ Modal explicativo sobre uso dos dados

## Impacto

### Usuário
- ✅ Fluxo mais limpo e direto
- ✅ Sem perguntas repetidas
- ✅ Melhor contexto para decidir informar renda
- ✅ Mais confiança (privacidade explicada)

### Sistema
- ✅ Integração mantida (backend funciona igual)
- ✅ Store continua convertendo corretamente
- ✅ Nenhuma quebra de funcionalidade
- ✅ Código mais limpo

## Testes

### Validação
```bash
npm run build
```
✅ Build sem erros

### Diagnósticos
```bash
getDiagnostics(['Step1Budget.tsx'])
```
✅ Sem erros TypeScript

## Componente SalaryRangeSelector

O componente `SalaryRangeSelector.tsx` **não foi deletado** porque:
- Pode ser útil no futuro
- Tem testes unitários
- É um componente reutilizável
- Não causa problemas se não for usado

Se quiser deletar no futuro:
```bash
rm platform/frontend/src/components/questionnaire/SalaryRangeSelector.tsx
rm platform/frontend/src/components/questionnaire/__tests__/SalaryRangeSelector.test.tsx
```

## Próximos Passos

1. ✅ Commit das alterações
2. ⏳ Testar fluxo completo do questionário
3. ⏳ Verificar que renda é capturada corretamente no Step 2
4. ⏳ Validar que TCO é calculado quando renda é informada

## Data
2025-11-06
