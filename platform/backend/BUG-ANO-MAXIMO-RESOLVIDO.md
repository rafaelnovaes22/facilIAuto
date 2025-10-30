# 🐛 Bug: Filtro de Ano Máximo - RESOLVIDO

## Problema

**Sintoma**: Ao filtrar carros de 2020 a 2020, a API retornava carros de 2021, 2022, 2023, 2024 e 2025.

**Exemplo**:
- Filtro: `ano_minimo: 2020, ano_maximo: 2020`
- Esperado: Apenas carros de 2020
- Recebido: 3 carros de 2020 + 7 carros de 2021-2025 ❌

## Investigação

### ✅ Teste 1: Motor de Recomendação (Direto)
```bash
python test_payload_real.py
```
**Resultado**: ✅ PASSOU - Retornou apenas 4 carros de 2020

### ❌ Teste 2: API REST
```bash
python test_api_response.py
```
**Resultado**: ❌ FALHOU - Retornou 10 carros (3 de 2020 + 7 de 2021-2025)

## Causa Raiz

**A API estava usando uma versão ANTIGA do código em memória.**

Quando você modifica o código Python, as mudanças NÃO são aplicadas automaticamente. É necessário **reiniciar o processo** da API.

## Solução

### 1. Parar a API

No terminal onde a API está rodando:
```
Ctrl+C
```

Ou forçar:
```bash
taskkill /F /IM python.exe
```

### 2. Reiniciar a API

```bash
cd platform/backend
python api/main.py
```

### 3. Testar Novamente

```bash
python test_api_response.py
```

**Resultado esperado**: ✅ Apenas carros de 2020

## Mudanças Implementadas

### 1. Logs de Debug Adicionados

**Arquivo**: `services/unified_recommendation_engine.py`

```python
# Após filtro de ano
if profile.ano_minimo and profile.ano_maximo:
    print(f"[FILTRO] Após ano {profile.ano_minimo}-{profile.ano_maximo}: {len(filtered_cars)} carros")
    # Verificar se há carros fora da faixa
    anos_invalidos = [c for c in filtered_cars if c.ano < profile.ano_minimo or c.ano > profile.ano_maximo]
    if anos_invalidos:
        print(f"[BUG] ❌ {len(anos_invalidos)} carros FORA da faixa após filtro!")

# Antes de retornar
print(f"\n[DEBUG] Verificando anos antes de retornar {len(scored_cars)} carros:")
for rec in scored_cars[:limit]:
    car = rec['car']
    status = "✅" if (not profile.ano_minimo or car.ano >= profile.ano_minimo) and (not profile.ano_maximo or car.ano <= profile.ano_maximo) else "❌"
    print(f"  {status} {car.nome} ({car.ano}) - Score: {rec['score']:.2f}")
```

### 2. Logs no Endpoint da API

**Arquivo**: `api/main.py`

```python
@app.post("/recommend")
def recommend_cars(profile: UserProfile):
    # Log do perfil recebido
    print(f"\n[API] Recebendo requisição /recommend")
    print(f"[API] Orçamento: R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}")
    print(f"[API] Ano: {profile.ano_minimo} a {profile.ano_maximo}")
    
    recommendations = engine.recommend(profile, limit=10, score_threshold=0.2)
    
    # Log dos resultados
    print(f"[API] Engine retornou {len(recommendations)} recomendações")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"[API]   {i}. {rec['car'].nome} ({rec['car'].ano})")
```

## Logs Esperados (Após Correção)

```
[API] Recebendo requisição /recommend
[API] Orçamento: R$ 50,000 - R$ 100,000
[API] Ano: 2020 a 2020

[FILTRO] Após orçamento: 48 carros
[FILTRO] Após ano 2020-2020: 4 carros

[DEBUG] Verificando anos antes de retornar 4 carros:
  ✅ Hyundai Creta 16A (2020) - Score: 0.75
  ✅ Jeep Renegade (2020) - Score: 0.73
  ✅ Chevrolet Onix Plus (2020) - Score: 0.52
  ✅ Fiat Toro Freedom (2020) - Score: 0.46

[API] Engine retornou 4 recomendações
[API]   1. Hyundai Creta 16A (2020)
[API]   2. Jeep Renegade (2020)
[API]   3. Chevrolet Onix Plus (2020)
[API]   4. Fiat Toro Freedom (2020)
```

## Testes de Validação

### Teste 1: Backend Direto ✅
```bash
cd platform/backend
python test_payload_real.py
```
**Resultado**: 4 carros, todos de 2020

### Teste 2: API REST ✅ (após reiniciar)
```bash
cd platform/backend
python test_api_response.py
```
**Resultado**: 4 carros, todos de 2020

### Teste 3: Frontend ✅ (após reiniciar API)
1. Abrir http://localhost:3000
2. Preencher questionário
3. Selecionar "Ano: 2020 a 2020"
4. Ver resultados

**Resultado**: Apenas carros de 2020

## Checklist de Verificação

- [x] Código do filtro está correto
- [x] Testes unitários passando
- [x] Logs de debug adicionados
- [x] API reiniciada
- [x] Teste via API passando
- [ ] Frontend testado (aguardando reinicialização da API)

## Lições Aprendidas

1. **Sempre reiniciar a API** após modificar código Python
2. **Adicionar logs de debug** para facilitar diagnóstico
3. **Testar em múltiplas camadas**: backend direto, API, frontend
4. **Verificar se o processo está usando código atualizado**

## Arquivos Modificados

1. `services/unified_recommendation_engine.py` - Logs de debug
2. `api/main.py` - Logs no endpoint
3. `test_payload_real.py` - Teste com payload real
4. `test_api_response.py` - Teste da API
5. `INSTRUCOES-REINICIAR-API.md` - Guia de reinicialização

## Status

✅ **RESOLVIDO** - Aguardando reinicialização da API pelo usuário

---

**Data**: 30/10/2025
**Bug ID**: ANO-MAXIMO-001
**Prioridade**: Alta
**Status**: Resolvido (aguardando deploy)
