# 🎯 Princípio: Filtros Opcionais se Tornam Obrigatórios

## Regra Fundamental

**Todo e qualquer filtro opcional, a partir do momento em que é selecionado pelo usuário, torna-se obrigatório no retorno dos resultados.**

---

## O que isso significa?

### ❌ ERRADO: Fallback que ignora filtros
```python
# NÃO FAZER ISSO!
filtered_cars = filter_by_year(cars, ano_minimo=2018)

if not filtered_cars:
    # ❌ Retornar todos os carros ignorando o filtro
    return cars  # ERRADO!
```

### ✅ CORRETO: Respeitar filtros sempre
```python
# FAZER ISSO!
filtered_cars = filter_by_year(cars, ano_minimo=2018)

if not filtered_cars:
    # ✅ Retornar lista vazia
    print("[AVISO] Nenhum carro atende ao filtro de ano >= 2018")
    return []  # CORRETO!
```

---

## Por que isso é importante?

### 1. Transparência
- Usuário sabe exatamente o que está buscando
- Não há "surpresas" com carros que não atendem aos critérios

### 2. Confiança
- Sistema respeita as escolhas do usuário
- Não tenta "ajudar" mostrando carros inadequados

### 3. Educação
- Usuário aprende sobre o mercado
- Entende que precisa ajustar critérios se não encontrar

### 4. Qualidade
- Resultados sempre relevantes
- Não polui a busca com carros fora do perfil

---

## Filtros Implementados

### 1. Orçamento (SEMPRE obrigatório)
```python
def filter_by_budget(self, cars: List[Car], profile: UserProfile) -> List[Car]:
    filtered = [
        car for car in cars
        if car.preco > 0 and profile.orcamento_min <= car.preco <= profile.orcamento_max
    ]
    
    if not filtered:
        print(f"[AVISO] Nenhum carro na faixa R$ {profile.orcamento_min:,.2f} - R$ {profile.orcamento_max:,.2f}")
    
    return filtered  # ✅ Retorna lista vazia se nenhum atender
```

### 2. Faixa de Anos (opcional → obrigatório)
```python
def filter_by_year(self, cars: List[Car], ano_minimo: Optional[int], ano_maximo: Optional[int]) -> List[Car]:
    filtered = cars
    
    if ano_minimo:
        filtered = [car for car in filtered if car.ano >= ano_minimo]
    
    if ano_maximo:
        filtered = [car for car in filtered if car.ano <= ano_maximo]
    
    return filtered  # ✅ Retorna lista vazia se nenhum atender
```

**Comportamento:**
- Se usuário NÃO seleciona: retorna todos os carros (qualquer ano)
- Se usuário seleciona ano >= 2018: retorna APENAS carros de 2018+
- Se nenhum carro atende: retorna lista vazia (não fallback!)

### 3. Quilometragem Máxima (opcional → obrigatório)
```python
def filter_by_km(self, cars: List[Car], km_maxima: Optional[int]) -> List[Car]:
    if not km_maxima:
        return cars
    
    return [car for car in cars if car.quilometragem <= km_maxima]
```

**Comportamento:**
- Se usuário NÃO seleciona: retorna todos os carros (qualquer km)
- Se usuário seleciona km <= 50000: retorna APENAS carros com até 50k km
- Se nenhum carro atende: retorna lista vazia

### 4. Must-Haves / Itens Obrigatórios (opcional → obrigatório)
```python
def filter_by_must_haves(self, cars: List[Car], must_haves: List[str]) -> List[Car]:
    if not must_haves:
        return cars
    
    filtered = []
    for car in cars:
        car_items = set(car.itens_seguranca + car.itens_conforto)
        required_items = set(must_haves)
        
        if required_items.issubset(car_items):
            filtered.append(car)
    
    return filtered  # ✅ Retorna lista vazia se nenhum atender
```

**Comportamento:**
- Se usuário NÃO seleciona: retorna todos os carros
- Se usuário seleciona ["ISOFIX", "6_airbags"]: retorna APENAS carros com AMBOS
- Se nenhum carro atende: retorna lista vazia

### 5. Raio Geográfico (opcional → obrigatório)
```python
def filter_by_radius(self, cars: List[Car], user_city: Optional[str], raio_km: Optional[int]) -> List[Car]:
    if not raio_km or not user_city:
        return cars
    
    user_coords = get_city_coordinates(user_city)
    if not user_coords:
        return cars
    
    filtered = []
    for car in cars:
        if car.dealership_latitude and car.dealership_longitude:
            dealer_coords = (car.dealership_latitude, car.dealership_longitude)
            distance = calculate_distance(user_coords, dealer_coords)
            
            if distance is not None and distance <= raio_km:
                filtered.append(car)
    
    return filtered  # ✅ Retorna lista vazia se nenhum atender
```

**Comportamento:**
- Se usuário NÃO seleciona: retorna todos os carros
- Se usuário seleciona raio 30km: retorna APENAS carros dentro de 30km
- Se nenhum carro atende: retorna lista vazia

### 6. Transporte de Passageiros / Uber/99 (opcional → obrigatório)
```python
def filter_by_app_transport(self, cars: List[Car], profile: UserProfile) -> List[Car]:
    if profile.uso_principal != "transporte_passageiros":
        return cars
    
    categoria_app = getattr(profile, 'categoria_app', 'uberx_99pop')
    
    valid_cars = []
    for car in cars:
        is_valid, reason = app_transport_validator.is_valid_for_app_transport(
            marca=car.marca,
            modelo=car.modelo,
            ano=car.ano,
            categoria_desejada=categoria_app
        )
        
        if is_valid:
            valid_cars.append(car)
    
    # ⚠️ CRÍTICO: Não usar fallback!
    if not valid_cars:
        print(f"[AVISO] Nenhum carro atende aos requisitos do {categoria_app}")
    
    return valid_cars  # ✅ Retorna lista vazia se nenhum atender
```

**Comportamento:**
- Se usuário NÃO seleciona "Transporte de passageiros": retorna todos os carros
- Se usuário seleciona "Uber/99": retorna APENAS carros aceitos pelo Uber/99
- Se nenhum carro atende: retorna lista vazia (SEM FALLBACK!)

---

## Fluxo de Filtros no Engine

```python
def recommend(self, profile: UserProfile, limit: int = 10) -> List[Dict]:
    # 1. Orçamento (SEMPRE obrigatório)
    filtered_cars = self.filter_by_budget(self.all_cars, profile)
    print(f"[FILTRO] Após orçamento: {len(filtered_cars)} carros")
    
    # 2. Faixa de anos (opcional → obrigatório)
    filtered_cars = self.filter_by_year(filtered_cars, profile.ano_minimo, profile.ano_maximo)
    if profile.ano_minimo or profile.ano_maximo:
        print(f"[FILTRO] Após ano: {len(filtered_cars)} carros")
    
    # 3. Quilometragem (opcional → obrigatório)
    filtered_cars = self.filter_by_km(filtered_cars, profile.km_maxima)
    if profile.km_maxima:
        print(f"[FILTRO] Após km: {len(filtered_cars)} carros")
    
    # 4. Must-haves (opcional → obrigatório)
    filtered_cars = self.filter_by_must_haves(filtered_cars, profile.must_haves)
    if profile.must_haves:
        print(f"[FILTRO] Após must-haves: {len(filtered_cars)} carros")
    
    # 5. Raio geográfico (opcional → obrigatório)
    filtered_cars = self.filter_by_radius(filtered_cars, profile.city, profile.raio_maximo_km)
    if profile.raio_maximo_km:
        print(f"[FILTRO] Após raio: {len(filtered_cars)} carros")
    
    # 6. Contextos (priorização, não eliminação)
    filtered_cars = self.filter_by_family_context(filtered_cars, profile)
    filtered_cars = self.filter_by_first_car(filtered_cars, profile)
    
    # 7. Transporte app (opcional → obrigatório)
    filtered_cars = self.filter_by_app_transport(filtered_cars, profile)
    
    # ⚠️ CRÍTICO: Se nenhum carro após filtros, retornar lista vazia
    if not filtered_cars:
        print("[AVISO] Nenhum carro após filtros. Retornando lista vazia.")
        return []  # ✅ SEM FALLBACK!
    
    # Calcular scores e retornar
    # ...
```

---

## Frontend: Mensagens Apropriadas

Quando nenhum carro é encontrado, o frontend deve mostrar mensagens específicas:

### Mensagem Genérica
```
😔 Nenhum carro encontrado

Não encontramos carros que correspondam aos seus critérios.

Sugestões:
• Aumente a faixa de orçamento
• Amplie a faixa de anos
• Remova alguns filtros opcionais

[✏️ Editar Busca]  [🔄 Nova Busca]
```

### Mensagem Específica (Uber/99)
```
😔 Nenhum carro encontrado

Não encontramos carros que correspondam aos seus critérios 
na faixa de R$ 10.000 - R$ 30.000 para uso como Uber/99.

Por que não encontramos?
• Carros para Uber/99 precisam ter ano mínimo 2015
• Apenas modelos específicos são aceitos pelas plataformas
• Veículo não pode ter mais de 10 anos de uso
• Tente ampliar o orçamento para R$ 40k-80k

[✏️ Editar Busca]  [🔄 Nova Busca]
```

### Mensagem Específica (Ano muito restritivo)
```
😔 Nenhum carro encontrado

Não encontramos carros de 2023 a 2025 
na faixa de R$ 30.000 - R$ 60.000.

Por que não encontramos?
• Carros muito novos (2023+) custam mais
• Nessa faixa de preço, encontramos carros de 2018-2021
• Tente ampliar a faixa de anos ou aumentar o orçamento

[✏️ Editar Busca]  [🔄 Nova Busca]
```

---

## Benefícios do Princípio

### 1. Transparência Total
- Usuário sabe exatamente o que está buscando
- Sistema não "mente" mostrando carros inadequados

### 2. Confiança no Sistema
- Resultados sempre relevantes
- Não há "surpresas" desagradáveis

### 3. Educação do Usuário
- Aprende sobre o mercado
- Entende limitações de orçamento/critérios
- Pode ajustar busca conscientemente

### 4. Qualidade dos Resultados
- 100% dos resultados atendem aos critérios
- Não polui com carros irrelevantes
- Facilita decisão de compra

### 5. Debugging Facilitado
- Logs claros de cada filtro
- Fácil identificar onde carros foram eliminados
- Rastreabilidade completa

---

## Exemplos Práticos

### Exemplo 1: Busca Uber/99 com orçamento baixo
```
Entrada:
- Orçamento: R$ 10k-30k
- Uso: Transporte de passageiros (Uber/99)

Filtros aplicados:
1. Orçamento: 150 carros
2. Uber/99 válidos: 0 carros (nenhum atende ano >= 2015 nessa faixa)

Resultado: Lista vazia ✅
Mensagem: "Carros para Uber/99 precisam ter ano mínimo 2015. 
           Tente ampliar o orçamento para R$ 40k-80k"
```

### Exemplo 2: Busca com ano muito restritivo
```
Entrada:
- Orçamento: R$ 30k-60k
- Ano: 2023-2025

Filtros aplicados:
1. Orçamento: 200 carros
2. Ano 2023-2025: 0 carros (muito novos para essa faixa)

Resultado: Lista vazia ✅
Mensagem: "Carros muito novos (2023+) custam mais. 
           Tente ampliar a faixa de anos ou aumentar o orçamento"
```

### Exemplo 3: Busca com múltiplos filtros
```
Entrada:
- Orçamento: R$ 50k-80k
- Ano: 2018-2020
- Km: <= 50.000
- Must-haves: ["ISOFIX", "6_airbags"]

Filtros aplicados:
1. Orçamento: 300 carros
2. Ano 2018-2020: 150 carros
3. Km <= 50k: 80 carros
4. ISOFIX + 6 airbags: 25 carros

Resultado: 25 carros ✅
Todos atendem a TODOS os critérios
```

---

## Checklist de Implementação

Para cada novo filtro, garantir:

- [ ] Se não especificado, retorna todos os carros (não filtra)
- [ ] Se especificado, aplica filtro rigorosamente
- [ ] Se nenhum carro atende, retorna lista vazia (SEM fallback)
- [ ] Log claro do resultado do filtro
- [ ] Mensagem apropriada no frontend quando lista vazia
- [ ] Documentação do comportamento
- [ ] Testes validando lista vazia quando aplicável

---

## Conclusão

**Filtros opcionais se tornam obrigatórios quando selecionados.**

Este princípio garante:
- ✅ Transparência total
- ✅ Confiança no sistema
- ✅ Resultados sempre relevantes
- ✅ Educação do usuário
- ✅ Qualidade das recomendações

**Nunca use fallback que ignore filtros do usuário!**
