# 📋 Filtros - Resumo Rápido

## Princípio Fundamental

**Todo filtro opcional, quando selecionado, torna-se obrigatório nos resultados.**

---

## Filtros Disponíveis

| Filtro | Tipo | Comportamento |
|--------|------|---------------|
| **Orçamento** | Obrigatório | Sempre aplicado. Elimina carros fora da faixa. |
| **Ano (min/max)** | Opcional → Obrigatório | Se selecionado, elimina carros fora da faixa. |
| **Quilometragem** | Opcional → Obrigatório | Se selecionado, elimina carros acima do limite. |
| **Must-haves** | Opcional → Obrigatório | Se selecionado, elimina carros sem TODOS os itens. |
| **Raio geográfico** | Opcional → Obrigatório | Se selecionado, elimina concessionárias fora do raio. |
| **Uber/99** | Opcional → Obrigatório | Se perfil = transporte, elimina carros não aceitos. |

---

## Regras de Implementação

### ✅ CORRETO
```python
def filter_by_something(cars, criteria):
    if not criteria:
        return cars  # Não filtra se não especificado
    
    filtered = [car for car in cars if meets_criteria(car, criteria)]
    return filtered  # Retorna lista vazia se nenhum atender
```

### ❌ ERRADO
```python
def filter_by_something(cars, criteria):
    if not criteria:
        return cars
    
    filtered = [car for car in cars if meets_criteria(car, criteria)]
    
    if not filtered:
        return cars  # ❌ NUNCA FAZER ISSO!
    
    return filtered
```

---

## Ordem de Aplicação

1. **Orçamento** (sempre)
2. **Ano** (se especificado)
3. **Quilometragem** (se especificado)
4. **Must-haves** (se especificado)
5. **Raio geográfico** (se especificado)
6. **Contextos** (priorização, não eliminação)
7. **Uber/99** (se perfil = transporte)

---

## Logs Esperados

```
[FILTRO] Após orçamento: 300 carros
[FILTRO] Após ano 2018-2020: 150 carros
[FILTRO] Após km <= 50000: 80 carros
[FILTRO] Após must-haves ['ISOFIX']: 40 carros
[FILTRO] Após raio 30km: 25 carros
```

Se nenhum carro após filtros:
```
[AVISO] Nenhum carro após filtros. Retornando lista vazia.
```

---

## Frontend: Mensagens

### Lista vazia genérica
```
😔 Nenhum carro encontrado
Não encontramos carros que correspondam aos seus critérios.

Sugestões:
• Aumente a faixa de orçamento
• Amplie a faixa de anos
• Remova alguns filtros opcionais
```

### Lista vazia específica (detectar qual filtro eliminou tudo)
```
😔 Nenhum carro encontrado
Carros para Uber/99 precisam ter ano mínimo 2015.
Tente ampliar o orçamento para R$ 40k-80k.
```

---

## Checklist para Novos Filtros

- [ ] Se não especificado → retorna todos
- [ ] Se especificado → aplica rigorosamente
- [ ] Lista vazia → sem fallback
- [ ] Log claro do resultado
- [ ] Mensagem apropriada no frontend
- [ ] Documentação
- [ ] Testes

---

## Documentação Completa

Ver: `docs/technical/PRINCIPIO-FILTROS-OBRIGATORIOS.md`
