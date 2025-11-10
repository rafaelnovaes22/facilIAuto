# Correção: Marcas Dinâmicas no Questionário

## Problema Identificado

As marcas no Step 4 do questionário estavam **hardcoded** em um array fixo, não refletindo o estoque real disponível.

### Comportamento Anterior
```typescript
const MARCAS_POPULARES = [
  'Fiat',
  'Ford',
  'Volkswagen',
  'Chevrolet',
  'Toyota',
  'Honda',
  'Hyundai',
  'Nissan',
  'Renault',
  'Jeep',
]
```

**Problemas**:
- ❌ Marcas fixas não refletem estoque real
- ❌ Usuário pode selecionar marca sem carros disponíveis
- ❌ Não mostra quantidade de modelos por marca
- ❌ Precisa atualização manual quando estoque muda

## Solução Implementada

### Integração com API `/brands-models`

O componente agora busca as marcas dinamicamente da API, mostrando apenas marcas com carros disponíveis no estoque.

### Mudanças no Código

**Arquivo**: `platform/frontend/src/components/questionnaire/Step4Preferences.tsx`

#### 1. Imports Adicionados
```typescript
import { useQuery } from '@tanstack/react-query'
import { getBrandsWithModels, queryKeys } from '@/services/api'
import { Spinner, Center } from '@chakra-ui/react'
```

#### 2. Hook para Buscar Dados
```typescript
// Buscar marcas e modelos disponíveis da API
const { data: brandsModels, isLoading: isLoadingBrands } = useQuery({
  queryKey: queryKeys.brandsModels,
  queryFn: getBrandsWithModels,
  staleTime: 1000 * 60 * 60, // 1 hora (dados raramente mudam)
})

// Extrair lista de marcas ordenadas
const availableBrands = brandsModels ? Object.keys(brandsModels).sort() : []
```

#### 3. UI Atualizada com Loading State
```typescript
{isLoadingBrands ? (
  <Center py={8}>
    <Spinner size="md" color="brand.500" />
  </Center>
) : (
  <CheckboxGroup
    value={formData.marcas_preferidas || []}
    onChange={(values) =>
      updateFormData({ marcas_preferidas: values as string[] })
    }
  >
    <SimpleGrid columns={{ base: 2, md: 3 }} spacing={3}>
      {availableBrands.map((marca) => {
        const modelCount = brandsModels?.[marca]?.length || 0
        return (
          <Checkbox
            key={marca}
            value={marca}
            size="lg"
            colorScheme="brand"
          >
            <HStack spacing={2}>
              <Text>{marca}</Text>
              <Badge colorScheme="gray" fontSize="xs">
                {modelCount}
              </Badge>
            </HStack>
          </Checkbox>
        )
      })}
    </SimpleGrid>
  </CheckboxGroup>
)}
```

## Melhorias Implementadas

### 1. Dados Dinâmicos
- ✅ Marcas carregadas do estoque real
- ✅ Apenas marcas com carros disponíveis
- ✅ Atualização automática quando estoque muda

### 2. Contador de Modelos
- ✅ Badge mostra quantidade de modelos por marca
- ✅ Ajuda usuário a entender variedade disponível
- ✅ Exemplo: "Chevrolet (8)" significa 8 modelos disponíveis

### 3. Loading State
- ✅ Spinner enquanto carrega dados
- ✅ Experiência fluida sem conteúdo vazio
- ✅ Feedback visual para o usuário

### 4. Cache Inteligente
- ✅ Dados cacheados por 1 hora (React Query)
- ✅ Reduz chamadas desnecessárias à API
- ✅ Performance otimizada

## Exemplo de UI

### Antes (Hardcoded)
```
☐ Fiat
☐ Ford
☐ Volkswagen
☐ Chevrolet
☐ Toyota
☐ Honda
☐ Hyundai
☐ Nissan
☐ Renault
☐ Jeep
```

### Depois (Dinâmico)
```
☐ Chevrolet  8
☐ Fiat       12
☐ Ford       5
☐ Honda      6
☐ Hyundai    7
☐ Nissan     4
☐ Toyota     9
☐ Volkswagen 11
```

**Nota**: Os números representam a quantidade de modelos disponíveis de cada marca.

## Fluxo de Dados

```
1. Usuário acessa Step 4
   ↓
2. React Query busca /brands-models
   ↓
3. API retorna { "Fiat": ["Argo", "Cronos", ...], ... }
   ↓
4. Componente extrai marcas e conta modelos
   ↓
5. UI renderiza checkboxes com badges
   ↓
6. Dados cacheados por 1 hora
```

## Benefícios

### UX
- ✅ Usuário vê apenas opções realmente disponíveis
- ✅ Contador de modelos ajuda na decisão
- ✅ Evita frustração de selecionar marca sem estoque
- ✅ Loading state profissional

### Manutenção
- ✅ Sem necessidade de atualizar código quando estoque muda
- ✅ Sincronização automática com backend
- ✅ Menos código hardcoded
- ✅ Mais fácil de testar

### Performance
- ✅ Cache de 1 hora reduz chamadas à API
- ✅ Dados leves (apenas marcas e modelos)
- ✅ Carregamento rápido

## Testes

### Cenários Testados

1. ✅ **Carregamento inicial**
   - Spinner aparece enquanto busca dados
   - Marcas aparecem após carregamento

2. ✅ **Seleção de marcas**
   - Checkboxes funcionam normalmente
   - Estado persiste no store

3. ✅ **Contador de modelos**
   - Badge mostra número correto
   - Atualiza quando estoque muda

4. ✅ **Cache**
   - Segunda visita não faz nova chamada
   - Dados permanecem por 1 hora

## Próximos Passos (Opcional)

### Possíveis Melhorias Futuras

1. **Seleção de Modelos Específicos**
   - Após selecionar marca, mostrar modelos disponíveis
   - Permitir seleção granular

2. **Filtro de Busca**
   - Campo de busca para filtrar marcas
   - Útil quando houver muitas marcas

3. **Ordenação Customizada**
   - Ordenar por popularidade
   - Ordenar por quantidade de modelos

4. **Indicador de Novidades**
   - Badge "Novo" para marcas recém-adicionadas
   - Destaque para marcas com mais estoque

## Arquivos Modificados

- ✅ `platform/frontend/src/components/questionnaire/Step4Preferences.tsx`
  - Removido array hardcoded `MARCAS_POPULARES`
  - Adicionado hook `useQuery` para buscar dados
  - Adicionado loading state
  - Adicionado contador de modelos

## Dependências

Esta correção depende de:
- ✅ Endpoint `/brands-models` (implementado anteriormente)
- ✅ Função `getBrandsWithModels()` no service layer
- ✅ React Query configurado no projeto

## Validação

### Como Testar

1. **Acesse o questionário**
   ```
   http://localhost:3000/questionario?step=4
   ```

2. **Verifique as marcas**
   - Devem aparecer apenas marcas com estoque
   - Cada marca deve ter um badge com número de modelos

3. **Teste o loading**
   - Abra DevTools → Network → Slow 3G
   - Recarregue a página
   - Deve aparecer spinner antes das marcas

4. **Verifique o cache**
   - Navegue para outro step e volte
   - Marcas devem aparecer instantaneamente (cache)

### Console do Navegador

```javascript
// Verificar dados carregados
const brandsModels = await fetch('http://localhost:8000/brands-models').then(r => r.json())
console.log(brandsModels)

// Verificar cache do React Query
// Abra React Query DevTools
```

---

**Data**: 2025-11-07  
**Tipo**: Fix - Dynamic Data Integration  
**Prioridade**: Alta  
**Status**: ✅ Completo e Testado
