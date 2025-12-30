# 🔍 Debug: Filtro de Ano Máximo

## Problema Reportado

**Usuário**: "Filtrei por carros 2020 a 2020 e retornou carros de ano acima, desconsiderando o filtro máximo"

## Investigação

### ✅ Teste 1: Método `filter_by_year()` - PASSOU

```python
filtered = engine.filter_by_year(all_cars, ano_minimo=2020, ano_maximo=2020)
# Resultado: 6 carros, TODOS de 2020
```

**Conclusão**: O método está funcionando corretamente.

### ✅ Teste 2: Filtro Combinado (Orçamento + Ano) - PASSOU

```python
filtered_budget = engine.filter_by_budget(all_cars, profile)
filtered_year = engine.filter_by_year(filtered_budget, 2020, 2020)
# Resultado: 6 carros, TODOS de 2020
```

**Conclusão**: A combinação de filtros está funcionando.

### ✅ Teste 3: Método `recommend()` Completo - PASSOU

```python
profile = UserProfile(
    orcamento_min=30000,
    orcamento_max=300000,
    ano_minimo=2020,
    ano_maximo=2020,
    ...
)
recommendations = engine.recommend(profile)
# Resultado: 6 carros, TODOS de 2020
```

**Conclusão**: O motor de recomendação está funcionando corretamente.

## Resultado da Investigação

**O BACKEND ESTÁ FUNCIONANDO CORRETAMENTE** ✅

Todos os testes passaram:
- ✅ Filtro direto de ano
- ✅ Filtro combinado com orçamento
- ✅ Recomendação completa

## Possíveis Causas do Problema

### 1. Frontend não está enviando `ano_maximo`

**Verificar**: O frontend está enviando o campo `ano_maximo` no payload?

```typescript
// Verificar em questionnaireStore.ts
toUserProfile: (): UserProfile => {
  return {
    ...
    ano_minimo: formData.ano_minimo,
    ano_maximo: formData.ano_maximo,  // ⚠️ Está sendo enviado?
    ...
  }
}
```

### 2. Frontend está enviando `null` ou `undefined`

**Problema**: Se `ano_maximo` for `null` ou `undefined`, o filtro não é aplicado.

```python
# No backend
if ano_maximo:  # Se for None, não filtra
    filtered = [car for car in filtered if car.ano <= ano_maximo]
```

**Solução**: Garantir que o frontend envie o valor correto.

### 3. Cache do navegador

**Problema**: O navegador pode estar usando uma versão antiga do código.

**Solução**: 
- Limpar cache do navegador (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)
- Abrir em aba anônima

### 4. API não foi reiniciada

**Problema**: Mudanças no código não foram aplicadas porque a API não foi reiniciada.

**Solução**:
```bash
# Parar a API (Ctrl+C)
# Reiniciar
cd platform/backend
python api/main.py
```

## Como Testar

### Teste 1: Backend Direto

```bash
cd platform/backend
python test_ano_maximo.py
```

**Resultado esperado**: ✅ Todos os testes passam

### Teste 2: API via curl

```bash
# Iniciar API
cd platform/backend
python api/main.py

# Em outro terminal
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "orcamento_min": 30000,
    "orcamento_max": 300000,
    "uso_principal": "familia",
    "tamanho_familia": 4,
    "ano_minimo": 2020,
    "ano_maximo": 2020,
    "prioridades": {
      "economia": 3,
      "espaco": 4,
      "performance": 3,
      "conforto": 4,
      "seguranca": 5
    },
    "marcas_preferidas": [],
    "marcas_rejeitadas": [],
    "tipos_preferidos": [],
    "primeiro_carro": false
  }'
```

**Resultado esperado**: Apenas carros de 2020

### Teste 3: API via Python

```bash
cd platform/backend
python test_api_ano_maximo.py
```

**Resultado esperado**: ✅ Teste passa

### Teste 4: Frontend

1. Abrir o frontend
2. Preencher o questionário
3. Selecionar "Ano: 2020 a 2020"
4. Ver resultados

**Verificar**:
- Abrir DevTools (F12)
- Ir em Network
- Filtrar por "recommend"
- Ver o payload enviado
- Verificar se `ano_maximo: 2020` está presente

## Payload Correto

```json
{
  "orcamento_min": 30000,
  "orcamento_max": 300000,
  "city": "São Paulo",
  "state": "SP",
  "uso_principal": "familia",
  "tamanho_familia": 4,
  "tem_criancas": false,
  "tem_idosos": false,
  "prioridades": {
    "economia": 3,
    "espaco": 4,
    "performance": 3,
    "conforto": 4,
    "seguranca": 5
  },
  "marcas_preferidas": [],
  "marcas_rejeitadas": [],
  "tipos_preferidos": [],
  "ano_minimo": 2020,
  "ano_maximo": 2020,  // ⚠️ CRÍTICO: Deve estar presente
  "primeiro_carro": false
}
```

## Logs do Backend

Quando o filtro é aplicado, você deve ver:

```
[FILTRO] Após orçamento: 72 carros
[FILTRO] Após ano 2020-2020: 6 carros
```

Se você NÃO ver a segunda linha, significa que `ano_maximo` não está sendo enviado.

## Checklist de Diagnóstico

- [ ] Backend: Executar `python test_ano_maximo.py` → Deve passar
- [ ] API: Executar `python test_api_ano_maximo.py` → Deve passar
- [ ] Frontend: Verificar DevTools → Payload deve ter `ano_maximo`
- [ ] Cache: Limpar cache do navegador
- [ ] API: Reiniciar a API
- [ ] Logs: Verificar logs do backend para ver filtros aplicados

## Solução Rápida

Se o problema persistir no frontend:

1. **Verificar o store**:
```typescript
// platform/frontend/src/store/questionnaireStore.ts
toUserProfile: (): UserProfile => {
  const { formData } = get()
  
  console.log('ano_minimo:', formData.ano_minimo)  // Debug
  console.log('ano_maximo:', formData.ano_maximo)  // Debug
  
  return {
    ...
    ano_minimo: formData.ano_minimo,
    ano_maximo: formData.ano_maximo,
    ...
  }
}
```

2. **Verificar o componente**:
```typescript
// Onde o usuário seleciona o ano
<input 
  type="number" 
  value={formData.ano_maximo}
  onChange={(e) => updateFormData({ ano_maximo: parseInt(e.target.value) })}
/>
```

3. **Verificar a chamada da API**:
```typescript
// services/api.ts
export const getRecommendations = async (profile: UserProfile) => {
  console.log('Enviando profile:', profile)  // Debug
  
  const response = await axios.post('/recommend', profile)
  return response.data
}
```

## Conclusão

✅ **Backend está funcionando perfeitamente**
⚠️ **Problema provavelmente está no frontend ou na comunicação**

**Próximos passos**:
1. Verificar se o frontend está enviando `ano_maximo`
2. Verificar logs do backend durante a requisição
3. Usar DevTools para inspecionar o payload
4. Limpar cache e reiniciar serviços

---

**Data**: 30/10/2025
**Status**: Backend validado ✅
**Ação necessária**: Verificar frontend
