# ✅ Checklist de Validação de Filtros

Use este checklist para validar que todos os filtros seguem o princípio fundamental.

---

## Princípio a Validar

**Todo filtro opcional, quando selecionado, torna-se obrigatório nos resultados.**

---

## Checklist Geral

### Para cada filtro, verificar:

- [ ] **Se NÃO especificado**: retorna todos os carros (não filtra)
- [ ] **Se especificado**: aplica filtro rigorosamente
- [ ] **Lista vazia**: retorna `[]` sem fallback
- [ ] **Log claro**: mostra resultado do filtro
- [ ] **Mensagem frontend**: apropriada quando lista vazia
- [ ] **Documentação**: comportamento documentado
- [ ] **Testes**: validam lista vazia quando aplicável

---

## Validação por Filtro

### 1. Orçamento (SEMPRE obrigatório)

- [x] Sempre aplicado (não é opcional)
- [x] Elimina carros fora da faixa
- [x] Retorna lista vazia se nenhum atender
- [x] Log: `[FILTRO] Após orçamento: X carros`
- [x] Aviso se lista vazia: `[AVISO] Nenhum carro na faixa R$ X - R$ Y`
- [x] Sem fallback

**Código:**
```python
def filter_by_budget(self, cars, profile):
    filtered = [car for car in cars if profile.orcamento_min <= car.preco <= profile.orcamento_max]
    if not filtered:
        print(f"[AVISO] Nenhum carro na faixa...")
    return filtered  # ✅ Lista vazia se nenhum atender
```

---

### 2. Ano (Opcional → Obrigatório)

- [x] Se não especificado: retorna todos
- [x] Se especificado: filtra rigorosamente
- [x] Suporta min, max, ou ambos
- [x] Retorna lista vazia se nenhum atender
- [x] Log apropriado:
  - `[FILTRO] Após ano >= X: Y carros`
  - `[FILTRO] Após ano <= X: Y carros`
  - `[FILTRO] Após ano X-Y: Z carros`
- [x] Sem fallback

**Código:**
```python
def filter_by_year(self, cars, ano_minimo, ano_maximo):
    filtered = cars
    if ano_minimo:
        filtered = [car for car in filtered if car.ano >= ano_minimo]
    if ano_maximo:
        filtered = [car for car in filtered if car.ano <= ano_maximo]
    return filtered  # ✅ Lista vazia se nenhum atender
```

**Validação manual:**
```bash
# Teste 1: Sem filtro
ano_minimo=None, ano_maximo=None → retorna todos ✅

# Teste 2: Só mínimo
ano_minimo=2018, ano_maximo=None → só carros >= 2018 ✅

# Teste 3: Só máximo
ano_minimo=None, ano_maximo=2016 → só carros <= 2016 ✅

# Teste 4: Faixa
ano_minimo=2015, ano_maximo=2018 → só carros 2015-2018 ✅

# Teste 5: Nenhum atende
ano_minimo=2023, ano_maximo=2025, orçamento baixo → lista vazia ✅
```

---

### 3. Quilometragem (Opcional → Obrigatório)

- [x] Se não especificado: retorna todos
- [x] Se especificado: filtra rigorosamente
- [x] Retorna lista vazia se nenhum atender
- [x] Log: `[FILTRO] Após km <= X: Y carros`
- [x] Sem fallback

**Código:**
```python
def filter_by_km(self, cars, km_maxima):
    if not km_maxima:
        return cars
    return [car for car in cars if car.quilometragem <= km_maxima]  # ✅
```

**Validação manual:**
```bash
# Teste 1: Sem filtro
km_maxima=None → retorna todos ✅

# Teste 2: Com filtro
km_maxima=50000 → só carros <= 50k km ✅

# Teste 3: Nenhum atende
km_maxima=10000 → lista vazia se nenhum tiver <= 10k ✅
```

---

### 4. Must-haves (Opcional → Obrigatório)

- [x] Se não especificado: retorna todos
- [x] Se especificado: filtra rigorosamente
- [x] Exige TODOS os itens (não apenas alguns)
- [x] Retorna lista vazia se nenhum atender
- [x] Log: `[FILTRO] Após must-haves [X, Y]: Z carros`
- [x] Sem fallback

**Código:**
```python
def filter_by_must_haves(self, cars, must_haves):
    if not must_haves:
        return cars
    
    filtered = []
    for car in cars:
        car_items = set(car.itens_seguranca + car.itens_conforto)
        required_items = set(must_haves)
        if required_items.issubset(car_items):
            filtered.append(car)
    
    return filtered  # ✅ Lista vazia se nenhum atender
```

**Validação manual:**
```bash
# Teste 1: Sem filtro
must_haves=[] → retorna todos ✅

# Teste 2: Com 1 item
must_haves=["ISOFIX"] → só carros com ISOFIX ✅

# Teste 3: Com múltiplos itens
must_haves=["ISOFIX", "6_airbags"] → só carros com AMBOS ✅

# Teste 4: Nenhum atende
must_haves=["item_raro"] → lista vazia ✅
```

---

### 5. Raio Geográfico (Opcional → Obrigatório)

- [x] Se não especificado: retorna todos
- [x] Se especificado: filtra rigorosamente
- [x] Retorna lista vazia se nenhum atender
- [x] Log: `[FILTRO] Após raio Xkm: Y carros`
- [x] Sem fallback

**Código:**
```python
def filter_by_radius(self, cars, user_city, raio_km):
    if not raio_km or not user_city:
        return cars
    
    user_coords = get_city_coordinates(user_city)
    if not user_coords:
        return cars
    
    filtered = []
    for car in cars:
        if car.dealership_latitude and car.dealership_longitude:
            distance = calculate_distance(user_coords, (car.dealership_latitude, car.dealership_longitude))
            if distance and distance <= raio_km:
                filtered.append(car)
    
    return filtered  # ✅ Lista vazia se nenhum atender
```

**Validação manual:**
```bash
# Teste 1: Sem filtro
raio_km=None → retorna todos ✅

# Teste 2: Com filtro
raio_km=30, city="São Paulo" → só carros dentro de 30km ✅

# Teste 3: Nenhum atende
raio_km=5, city="Cidade Pequena" → lista vazia ✅
```

---

### 6. Uber/99 (Opcional → Obrigatório)

- [x] Se perfil ≠ transporte: retorna todos
- [x] Se perfil = transporte: filtra rigorosamente
- [x] Valida ano, modelo, categoria
- [x] Retorna lista vazia se nenhum atender
- [x] Log: `[FILTRO APP] X de Y carros válidos para Z`
- [x] **SEM FALLBACK** (crítico!)

**Código:**
```python
def filter_by_app_transport(self, cars, profile):
    if profile.uso_principal != "transporte_passageiros":
        return cars
    
    categoria_app = getattr(profile, 'categoria_app', 'uberx_99pop')
    
    valid_cars = []
    for car in cars:
        is_valid, reason = app_transport_validator.is_valid_for_app_transport(
            marca=car.marca, modelo=car.modelo, ano=car.ano, categoria_desejada=categoria_app
        )
        if is_valid:
            valid_cars.append(car)
    
    # ⚠️ CRÍTICO: Não usar fallback!
    if not valid_cars:
        print(f"[AVISO] Nenhum carro atende aos requisitos do {categoria_app}")
    
    return valid_cars  # ✅ Lista vazia se nenhum atender
```

**Validação manual:**
```bash
# Teste 1: Perfil diferente
uso_principal="familia" → retorna todos ✅

# Teste 2: Uber/99 com carros válidos
uso_principal="transporte_passageiros", orçamento adequado → carros válidos ✅

# Teste 3: Uber/99 sem carros válidos
uso_principal="transporte_passageiros", orçamento baixo → lista vazia ✅
# ⚠️ CRÍTICO: Não retorna fallback!
```

---

## Validação do Fluxo Completo

### Método `recommend()`

- [x] Aplica filtros na ordem correta
- [x] Cada filtro tem log apropriado
- [x] Se lista vazia após filtros: retorna `[]`
- [x] Aviso final: `[AVISO] Nenhum carro após filtros. Retornando lista vazia.`
- [x] **NUNCA** retorna fallback ignorando filtros

**Código:**
```python
def recommend(self, profile, limit=10):
    # 1. Orçamento
    filtered_cars = self.filter_by_budget(self.all_cars, profile)
    print(f"[FILTRO] Após orçamento: {len(filtered_cars)} carros")
    
    # 2. Ano
    filtered_cars = self.filter_by_year(filtered_cars, profile.ano_minimo, profile.ano_maximo)
    # ... logs
    
    # 3-7. Outros filtros
    # ...
    
    # ⚠️ CRÍTICO: Se nenhum carro após filtros
    if not filtered_cars:
        print("[AVISO] Nenhum carro após filtros. Retornando lista vazia.")
        return []  # ✅ SEM FALLBACK!
    
    # Calcular scores e retornar
    # ...
```

---

## Validação do Frontend

### Mensagens quando lista vazia

- [x] Mensagem genérica implementada
- [x] Mensagens específicas por contexto
- [x] Sugestões de ajuste de critérios
- [x] Botões de ação (Editar/Nova Busca)

**Exemplo de mensagem:**
```
😔 Nenhum carro encontrado

Não encontramos carros que correspondam aos seus critérios.

Sugestões:
• Aumente a faixa de orçamento
• Amplie a faixa de anos
• Remova alguns filtros opcionais

[✏️ Editar Busca]  [🔄 Nova Busca]
```

---

## Testes de Regressão

### Cenários a testar:

1. **Busca sem filtros opcionais**
   - [ ] Retorna carros dentro do orçamento
   - [ ] Não aplica filtros desnecessários

2. **Busca com 1 filtro opcional**
   - [ ] Aplica filtro corretamente
   - [ ] Log apropriado
   - [ ] Lista vazia se nenhum atender

3. **Busca com múltiplos filtros**
   - [ ] Aplica todos os filtros
   - [ ] Ordem correta
   - [ ] Logs de cada etapa
   - [ ] Lista vazia se nenhum atender

4. **Busca muito restritiva**
   - [ ] Retorna lista vazia
   - [ ] Aviso apropriado
   - [ ] Mensagem específica no frontend

5. **Uber/99 com orçamento baixo**
   - [ ] Retorna lista vazia
   - [ ] **NÃO** retorna fallback
   - [ ] Mensagem específica sobre requisitos

---

## Checklist de Código

### Para cada filtro, verificar no código:

- [ ] Método de filtro existe
- [ ] Parâmetro opcional (pode ser `None`)
- [ ] Se `None`: retorna todos os carros
- [ ] Se especificado: aplica filtro
- [ ] Retorna lista (pode ser vazia)
- [ ] **NUNCA** tem `if not filtered: return cars`
- [ ] Log apropriado no `recommend()`
- [ ] Documentação do comportamento

---

## Resultado Esperado

Após validação completa:

✅ Todos os filtros seguem o princípio
✅ Nenhum fallback problemático
✅ Logs claros e consistentes
✅ Mensagens apropriadas no frontend
✅ Testes validam comportamento
✅ Documentação completa

---

## Ações se Falhar

Se algum item falhar:

1. **Identificar o filtro problemático**
2. **Corrigir o código** (remover fallback)
3. **Atualizar logs**
4. **Testar novamente**
5. **Atualizar documentação**

---

## Contato

Dúvidas sobre validação? Consulte:
- [Princípio de Filtros](./PRINCIPIO-FILTROS-OBRIGATORIOS.md)
- [Resumo de Filtros](./FILTROS-RESUMO.md)
- [Fluxograma](./FILTROS-FLUXOGRAMA.md)
