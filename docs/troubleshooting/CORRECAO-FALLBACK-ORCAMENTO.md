# Correção Crítica: Fallback Ignorando Filtro de Orçamento

**Data:** 30 de outubro de 2025  
**Severidade:** 🔴 CRÍTICA  
**Problema:** Sistema retornava carros fora da faixa de orçamento especificada

## Problema Identificado

### Sintoma
Ao buscar carros na faixa de **R$ 10.000 - R$ 15.000**, o sistema retornava:
- Ford Focus: R$ 34.990 ❌
- Caoa Chery Face: R$ 21.990 ❌
- Fiat Siena: R$ 35.990 ❌
- Renault Sandero: R$ 36.990 ❌
- Citroen C3: R$ 36.990 ❌

**Todos os carros estavam FORA da faixa especificada!**

### Causa Raiz

No arquivo `platform/backend/services/unified_recommendation_engine.py`, linhas 608-615:

```python
if not filtered_cars:
    # Fallback: pegar os 5 carros mais próximos do orçamento (sem filtros avançados)
    print("[AVISO] Nenhum carro após filtros. Usando fallback.")
    all_sorted = sorted(
        self.all_cars,
        key=lambda c: abs(c.preco - profile.orcamento_max)
    )
    filtered_cars = all_sorted[:5]  # ❌ IGNORA O FILTRO DE ORÇAMENTO!
```

### Logs do Backend
```
[AVISO] Nenhum carro encontrado na faixa R$ 10,000.00 - R$ 15,000.00
[FILTRO] Após orçamento: 0 carros
[AVISO] Nenhum carro após filtros. Usando fallback.  ← PROBLEMA AQUI!
INFO: "POST /recommend HTTP/1.1" 200 OK
```

O fallback estava retornando os 5 carros **mais próximos** do orçamento máximo (R$ 15.000), mas **sem respeitar a faixa**. Isso resultava em carros de R$ 20k-40k sendo retornados.

## Solução Implementada

### Código Corrigido

```python
if not filtered_cars:
    # ⚠️ CRÍTICO: Não usar fallback que ignora orçamento!
    # Se nenhum carro atende aos filtros, retornar lista vazia
    # O frontend deve mostrar mensagem apropriada
    print("[AVISO] Nenhum carro após filtros. Retornando lista vazia.")
    return []  # ✅ RETORNA LISTA VAZIA
```

### Comportamento Correto

**Antes:**
```
Busca: R$ 10.000 - R$ 15.000
Resultado: 5 carros (R$ 21k - R$ 37k) ❌ FORA DA FAIXA
```

**Depois:**
```
Busca: R$ 10.000 - R$ 15.000
Resultado: 0 carros ✅ CORRETO (não há carros nesta faixa)
Frontend: Mostra mensagem "Nenhum carro encontrado"
```

## Regras de Negócio

### Filtros Eliminatórios (Hard Constraints)
Estes filtros **NUNCA** devem ser ignorados:

1. ✅ **Orçamento** - Preço deve estar entre `orcamento_min` e `orcamento_max`
2. ✅ **Preço válido** - Preço deve ser > 0
3. ✅ **Categoria** - Não pode ser "Moto"
4. ✅ **Disponibilidade** - Deve estar disponível

### Filtros Opcionais (Soft Constraints)
Estes podem ser relaxados se necessário:

- Ano mínimo
- Quilometragem máxima
- Must-haves (itens obrigatórios)
- Raio geográfico

### Quando Nenhum Carro é Encontrado

**Comportamento Correto:**
1. Backend retorna lista vazia (`[]`)
2. Frontend mostra mensagem clara:
   - "Nenhum carro encontrado na faixa de R$ X - R$ Y"
   - "Tente ajustar seus filtros ou ampliar a faixa de preço"
3. Usuário pode:
   - Voltar e ajustar o orçamento
   - Remover filtros opcionais
   - Tentar outra busca

**Comportamento INCORRETO (antes):**
1. Backend usava fallback ignorando orçamento ❌
2. Frontend mostrava carros fora da faixa ❌
3. Usuário ficava confuso ❌

## Testes de Validação

### Teste 1: Faixa Sem Carros
```bash
Busca: R$ 10.000 - R$ 15.000
Resultado esperado: 0 carros
Resultado obtido: 0 carros ✅
```

### Teste 2: Faixa Com Carros
```bash
Busca: R$ 50.000 - R$ 80.000
Resultado esperado: 29 carros (todos dentro da faixa)
Resultado obtido: 29 carros ✅
Validação: Todos entre R$ 50k e R$ 80k ✅
```

### Teste 3: Logs do Backend
```
[AVISO] Nenhum carro encontrado na faixa R$ 10,000.00 - R$ 15,000.00
[FILTRO] Após orçamento: 0 carros
[AVISO] Nenhum carro após filtros. Retornando lista vazia. ✅
INFO: "POST /recommend HTTP/1.1" 200 OK
```

## Impacto

### Antes da Correção
- ❌ Usuários viam carros fora do orçamento
- ❌ Perda de confiança no sistema
- ❌ Frustração ao ver carros inacessíveis
- ❌ Violação de expectativa do usuário

### Depois da Correção
- ✅ Apenas carros dentro do orçamento são mostrados
- ✅ Mensagem clara quando nenhum carro é encontrado
- ✅ Usuário pode ajustar filtros conscientemente
- ✅ Sistema confiável e previsível

## Arquivos Modificados

### Código
- `platform/backend/services/unified_recommendation_engine.py` - Removido fallback que ignorava orçamento

### Documentação
- `docs/troubleshooting/CORRECAO-FALLBACK-ORCAMENTO.md` - Este documento
- `docs/troubleshooting/CORRECAO-FILTROS-ORCAMENTO.md` - Correções anteriores
- `docs/troubleshooting/CORRECAO-CLASSIFICACAO-VEICULOS.md` - Correções de classificação

## Lições Aprendidas

### 1. Fallbacks Devem Respeitar Constraints Críticos
- ✅ Fallback pode relaxar filtros **opcionais**
- ❌ Fallback **NUNCA** deve ignorar orçamento
- ❌ Fallback **NUNCA** deve ignorar preço > 0
- ❌ Fallback **NUNCA** deve incluir motos

### 2. Transparência com o Usuário
- ✅ Melhor retornar lista vazia com mensagem clara
- ❌ Pior retornar resultados que não atendem aos critérios

### 3. Logs São Essenciais
- Os logs mostraram claramente o problema:
  ```
  [AVISO] Nenhum carro após filtros. Usando fallback.
  ```
- Isso permitiu identificar e corrigir rapidamente

## Prevenção de Regressões

### 1. Testes Automatizados
Adicionar teste que valida:
```python
def test_no_fallback_outside_budget():
    """Garantir que fallback não retorna carros fora do orçamento"""
    profile = UserProfile(
        uso_principal="familia",
        orcamento_min=10000,
        orcamento_max=15000,
        prioridades={"economia": 5, "seguranca": 5}
    )
    
    recommendations = engine.recommend(profile)
    
    # Se não há carros na faixa, deve retornar lista vazia
    if not recommendations:
        assert len(recommendations) == 0
    else:
        # Se há carros, todos devem estar na faixa
        for rec in recommendations:
            assert 10000 <= rec['car'].preco <= 15000
```

### 2. Validação no Frontend
O frontend deve validar que todos os carros retornados estão dentro da faixa:
```typescript
const validateBudgetRange = (cars: Car[], min: number, max: number) => {
  const outOfRange = cars.filter(car => car.preco < min || car.preco > max);
  if (outOfRange.length > 0) {
    console.error('Carros fora da faixa de orçamento:', outOfRange);
    // Filtrar no frontend como fallback
    return cars.filter(car => car.preco >= min && car.preco <= max);
  }
  return cars;
};
```

### 3. Monitoramento
Adicionar métricas para detectar:
- Quantas buscas retornam 0 resultados
- Quais faixas de preço têm poucos carros
- Alertar quando fallback é acionado

## Status Final

✅ **PROBLEMA CRÍTICO RESOLVIDO**

- Fallback removido: ✅
- Filtro de orçamento rigoroso: ✅
- Lista vazia quando nenhum carro atende: ✅
- Logs claros: ✅
- Documentação completa: ✅

## Próximos Passos

1. ✅ Recarregar frontend
2. ✅ Testar busca R$ 10k-15k (deve retornar 0 carros)
3. ✅ Verificar mensagem no frontend
4. ⏳ Implementar testes automatizados
5. ⏳ Adicionar validação no frontend
6. ⏳ Considerar adicionar mais carros na faixa R$ 10k-30k
