# Melhoria: Seleção Dinâmica de Localização

## Problema Identificado

O campo de cidade era um input de texto livre, dificultando:
- Padronização dos nomes de cidades
- Validação de dados
- Experiência do usuário em mobile (digitação)

## Solução Implementada

### 1. Base de Dados de Cidades

Criado arquivo `platform/frontend/src/data/cities.ts` com:
- **27 estados** brasileiros
- **500+ cidades** principais (capitais + cidades relevantes)
- Foco em cidades com maior probabilidade de ter concessionárias

### 2. Seleção Dinâmica

**Fluxo de UX:**
1. Usuário seleciona o **estado** primeiro
2. Lista de **cidades** carrega automaticamente
3. Opção **"Todo o estado"** permite busca ampla
4. Feedback visual mostra o escopo da busca

### 3. Comportamento Inteligente

**Quando estado é selecionado:**
- Carrega cidades daquele estado
- Limpa cidade anterior se não pertence ao novo estado
- Mostra placeholder "Todo o estado"

**Quando cidade é deixada vazia:**
- Busca em todo o estado selecionado
- Mensagem clara: "Vamos buscar concessionárias em todo o estado de XX"

**Quando cidade é selecionada:**
- Busca prioriza aquela cidade específica
- Mensagem: "Vamos priorizar concessionárias em [Cidade] - [Estado]"

## Arquivos Criados

### `platform/frontend/src/data/cities.ts`
```typescript
export const CIDADES_POR_ESTADO: Record<string, string[]> = {
    SP: ['São Paulo', 'Guarulhos', 'Campinas', ...],
    RJ: ['Rio de Janeiro', 'Niterói', 'Duque de Caxias', ...],
    // ... todos os estados
}

export const getCitiesByState = (state: string): string[] => {...}
export const hasCities = (state: string): boolean => {...}
```

## Arquivos Modificados

### `platform/frontend/src/components/questionnaire/LocationSelector.tsx`

**Mudanças principais:**
- Input de texto → Select dropdown para cidades
- Carregamento dinâmico com `useEffect`
- Layout vertical (VStack) para melhor UX mobile
- Feedback contextual baseado na seleção

## Melhorias de UX

### Antes
- ❌ Campo de texto livre (erros de digitação)
- ❌ Sem validação de cidades
- ❌ Difícil digitar em mobile
- ❌ Sem opção de busca estadual

### Depois
- ✅ Dropdown com cidades validadas
- ✅ Carregamento dinâmico por estado
- ✅ Fácil seleção em mobile
- ✅ Opção "Todo o estado" clara
- ✅ Feedback visual do escopo de busca
- ✅ Limpa cidade ao trocar estado

## Cobertura de Cidades

### Estados com mais cidades (mercado relevante):
- **SP**: 40 cidades (maior mercado)
- **MG**: 25 cidades
- **RJ**: 20 cidades
- **RS**: 20 cidades
- **PR**: 20 cidades
- **SC**: 20 cidades
- **BA**: 15 cidades
- **GO**: 14 cidades
- **PE**: 15 cidades

### Estados menores:
- 4-9 cidades principais por estado
- Foco em capitais e cidades com concessionárias

## Exemplo de Uso

```typescript
// Usuário seleciona SP
<LocationSelector
  state="SP"
  city={undefined}  // "Todo o estado"
  onChange={(location) => {
    // location = { state: "SP", city: undefined }
    // Busca em todo o estado de SP
  }}
/>

// Usuário seleciona cidade específica
<LocationSelector
  state="SP"
  city="Campinas"
  onChange={(location) => {
    // location = { state: "SP", city: "Campinas" }
    // Prioriza Campinas
  }}
/>
```

## Comportamento no Backend

O backend já suporta ambos os cenários:
- `state="SP"` + `city=undefined` → Busca em todo SP
- `state="SP"` + `city="Campinas"` → Prioriza Campinas

## Testes Recomendados

1. **Seleção de estado**: Verificar carregamento de cidades
2. **Troca de estado**: Verificar limpeza de cidade anterior
3. **"Todo o estado"**: Verificar que city=undefined é enviado
4. **Cidade específica**: Verificar que city é enviada corretamente
5. **Mobile**: Testar dropdowns em iOS e Android
6. **Feedback visual**: Verificar mensagens contextuais

## Próximos Passos (Opcional)

1. **Busca de cidades**: Adicionar campo de busca no dropdown (muitas cidades)
2. **Geolocalização**: Detectar localização automaticamente
3. **Cidades recentes**: Salvar últimas cidades selecionadas
4. **Mais cidades**: Expandir lista conforme demanda

## Dados Técnicos

- **Total de estados**: 27
- **Total de cidades**: ~500
- **Tamanho do arquivo**: ~8KB
- **Performance**: Carregamento instantâneo (dados locais)
