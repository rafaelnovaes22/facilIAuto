# Melhoria: Campo de Orçamento Digitável para Mobile

## Problema Identificado

Usuários em dispositivos móveis estavam com dificuldades para selecionar a faixa de orçamento usando o slider de duplo controle (RangeSlider), que requer precisão de toque e arraste.

## Solução Implementada

### 1. Campos de Input Digitáveis

Adicionados dois campos de entrada numérica com as seguintes características:

- **Type**: `tel` com `inputMode="numeric"` - Abre teclado numérico no mobile
- **Pattern**: `[0-9]*` - Aceita apenas números
- **Size**: `lg` - Campos grandes e fáceis de tocar
- **Visual**: InputLeftAddon com labels "Mínimo" e "Máximo"

### 2. Validação em Tempo Real

- Remove caracteres não numéricos automaticamente
- Valida limites (min: R$ 10.000, max: R$ 500.000)
- Garante que mínimo < máximo
- Corrige valores inválidos ao perder foco (onBlur)

### 3. UX Adaptativa

- **Mobile**: Mostra apenas campos de input (slider oculto)
- **Desktop**: Mostra campos + slider para flexibilidade
- Texto de ajuda adaptado ao dispositivo

### 4. Feedback Visual

- Valores formatados em moeda (R$) abaixo dos inputs
- Box de resumo mostrando a faixa selecionada
- Cores da marca (brand.500/600) para destaque

## Arquivos Modificados

- `platform/frontend/src/components/questionnaire/BudgetSlider.tsx`

## Melhorias de UX

### Antes
- ❌ Difícil arrastar sliders em telas pequenas
- ❌ Falta de precisão ao tocar
- ❌ Frustração em dispositivos móveis

### Depois
- ✅ Teclado numérico nativo do celular
- ✅ Digitação direta e precisa
- ✅ Validação automática
- ✅ Slider opcional no desktop
- ✅ Experiência mobile-first

## Exemplo de Uso

```typescript
// O componente mantém a mesma interface
<BudgetSlider
  minValue={50000}
  maxValue={100000}
  onChange={(min, max) => console.log(min, max)}
  minLimit={10000}
  maxLimit={500000}
  step={5000}
/>
```

## Testes Recomendados

1. **Mobile**: Testar digitação em iOS e Android
2. **Validação**: Tentar valores inválidos (negativos, muito altos, etc.)
3. **Desktop**: Verificar que slider ainda funciona
4. **Acessibilidade**: Testar com leitores de tela

## Próximos Passos

Considerar aplicar a mesma abordagem para outros sliders:
- `YearSelector` (ano do veículo)
- `PrioritySlider` (prioridades do usuário)

## Referências

- Chakra UI InputGroup: https://chakra-ui.com/docs/components/input
- Mobile Input Best Practices: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/tel
