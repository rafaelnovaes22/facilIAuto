# 🔄 Como Reiniciar a API

## Problema Identificado

A API está retornando carros fora do filtro de ano porque está usando uma **versão antiga do código** em memória.

## Solução: Reiniciar a API

### Passo 1: Parar a API

Se a API está rodando em um terminal:
1. Vá até o terminal onde a API está rodando
2. Pressione **Ctrl+C** para parar

Se não sabe onde está rodando:
```bash
# Windows
taskkill /F /IM python.exe

# Ou encontrar o processo
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

### Passo 2: Iniciar a API Novamente

```bash
cd platform/backend
python api/main.py
```

### Passo 3: Testar

```bash
# Em outro terminal
cd platform/backend
python test_api_response.py
```

## O Que Foi Corrigido

1. ✅ Adicionado logs de debug no endpoint `/recommend`
2. ✅ Adicionado verificação de anos antes de retornar
3. ✅ Filtro de ano máximo está funcionando no engine

## Logs Esperados

Quando você fizer uma requisição, deve ver:

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

## Se Ainda Não Funcionar

1. **Limpar cache do Python**:
```bash
cd platform/backend
del /s /q __pycache__
del /s /q *.pyc
```

2. **Verificar se está usando o código correto**:
```bash
python -c "from services.unified_recommendation_engine import UnifiedRecommendationEngine; print('OK')"
```

3. **Testar diretamente**:
```bash
python test_payload_real.py
```

Se o teste direto funciona mas a API não, o problema é que a API não foi reiniciada corretamente.

---

**IMPORTANTE**: Sempre que modificar o código do backend, você DEVE reiniciar a API!
