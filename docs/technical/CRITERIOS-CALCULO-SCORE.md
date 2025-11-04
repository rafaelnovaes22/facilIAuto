# Critérios de Cálculo de Score - FacilIAuto

## Visão Geral

O motor de recomendação do FacilIAuto calcula o **match score** (0.0 a 1.0) de forma **dinâmica** para cada carro baseado no perfil do usuário. O score final é uma média ponderada de 4 componentes principais.

## Fórmula do Match Score

```
Match Score = (Category × W1) + (Priorities × W2) + (Preferences × W3) + (Budget × W4)
```

Onde os pesos (W1, W2, W3, W4) são **dinâmicos** e variam conforme o perfil de uso.

---

## 1. Score de Categoria (Category Score)

**Peso padrão:** 30% | **Peso dinâmico:** 25% a 50%

Avalia a adequação da categoria do carro ao uso principal declarado pelo usuário.

### Mapeamento Categoria × Uso

| Categoria | Família | Primeiro Carro | Trabalho | Comercial | Lazer | Transporte App |
|-----------|---------|----------------|----------|-----------|-------|----------------|
| **SUV** | 0.95 ⭐⭐⭐⭐⭐ | 0.30 ⭐ | 0.50 ⭐⭐ | 0.60 ⭐⭐⭐ | 0.95 ⭐⭐⭐⭐⭐ | 0.90 ⭐⭐⭐⭐⭐ |
| **Van** | 0.90 ⭐⭐⭐⭐⭐ | 0.15 | 0.30 ⭐ | 0.90 ⭐⭐⭐⭐⭐ | 0.70 ⭐⭐⭐ | 0.40 ⭐⭐ |
| **Sedan** | 0.75 ⭐⭐⭐⭐ | 0.55 ⭐⭐ | 0.95 ⭐⭐⭐⭐⭐ | 0.40 ⭐⭐ | 0.55 ⭐⭐ | 0.95 ⭐⭐⭐⭐⭐ |
| **Hatch** | 0.40 ⭐⭐ | 0.95 ⭐⭐⭐⭐⭐ | 0.85 ⭐⭐⭐⭐ | 0.30 ⭐ | 0.40 ⭐⭐ | 0.70 ⭐⭐⭐ |
| **Pickup** | 0.35 ⭐ | 0.20 | 0.40 ⭐⭐ | 0.95 ⭐⭐⭐⭐⭐ | 0.85 ⭐⭐⭐⭐ | 0.20 |
| **Compacto** | 0.20 | 0.95 ⭐⭐⭐⭐⭐ | 0.75 ⭐⭐⭐ | 0.25 | 0.30 ⭐ | 0.50 ⭐⭐ |

**Exemplos:**
- SUV para família: 0.95 (ideal - espaço + segurança)
- Hatch para primeiro carro: 0.95 (ideal - fácil de dirigir)
- Pickup para comercial: 0.95 (ideal - capacidade de carga)

---

## 2. Score de Prioridades (Priorities Score)

**Peso padrão:** 40% | **Peso dinâmico:** 35% a 50%

Avalia o quanto o carro atende às 5 prioridades definidas pelo usuário (escala 1-5).

### Prioridades Disponíveis

1. **Economia** → `car.score_economia`
2. **Espaço** → `car.score_familia`
3. **Performance** → `car.score_performance`
4. **Conforto** → `car.score_conforto`
5. **Segurança** → `car.score_seguranca`

### Prioridades Avançadas (Fase 3)

6. **Revenda** → `car.indice_revenda`
7. **Confiabilidade** → `car.indice_confiabilidade`
8. **Custo Manutenção** → Normalizado de `car.custo_manutencao_anual`

### Cálculo

```python
priorities_score = Σ(car_score[prioridade] × user_value[prioridade] / 5) / Σ(user_value / 5)
```

**Exemplo:**
```
Usuário define:
- Economia: 5 (peso 1.0)
- Segurança: 5 (peso 1.0)
- Espaço: 3 (peso 0.6)
- Performance: 2 (peso 0.4)
- Conforto: 2 (peso 0.4)

Carro tem:
- score_economia: 0.9
- score_seguranca: 0.8
- score_familia: 0.7
- score_performance: 0.5
- score_conforto: 0.6

Score = (0.9×1.0 + 0.8×1.0 + 0.7×0.6 + 0.5×0.4 + 0.6×0.4) / (1.0+1.0+0.6+0.4+0.4)
      = (0.9 + 0.8 + 0.42 + 0.2 + 0.24) / 3.4
      = 2.56 / 3.4
      = 0.75
```

---

## 3. Score de Preferências (Preferences Score)

**Peso padrão:** 20% | **Peso dinâmico:** 10% a 20%

Avalia preferências específicas do usuário (marcas, combustível, câmbio).

### Critérios

| Preferência | Impacto | Score |
|-------------|---------|-------|
| **Marca preferida** | +30% | +0.3 |
| **Marca rejeitada** | -50% | -0.5 |
| **Tipo preferido** | +20% | +0.2 |
| **Combustível preferido** | +10% | +0.1 |

**Base:** 0.5 (neutro)

**Exemplo:**
```
Carro: Volkswagen Gol, Flex
Preferências: Marcas preferidas = [Volkswagen, Fiat]

Score = 0.5 (base) + 0.3 (marca preferida) = 0.8
```

### Filtros Obrigatórios

⚠️ **IMPORTANTE:** Antes do cálculo de score, preferências são aplicadas como **filtros eliminatórios**:

- Se marcas preferidas definidas → **APENAS** essas marcas
- Se marcas rejeitadas definidas → **ELIMINA** essas marcas
- Se tipos preferidos definidos → **APENAS** esses tipos
- Se combustível preferido → **APENAS** esse combustível
- Se câmbio preferido → **APENAS** esse câmbio

---

## 4. Score de Posição no Orçamento (Budget Score)

**Peso padrão:** 10% | **Peso dinâmico:** 5% a 10%

Avalia a posição do preço do carro dentro da faixa de orçamento.

### Lógica

Carros no **meio do orçamento** recebem score máximo (1.0).
Carros nos extremos recebem scores menores.

```python
middle = (orcamento_min + orcamento_max) / 2
distance_from_middle = abs(preco - middle)
normalized_distance = distance_from_middle / (budget_range / 2)
budget_score = max(0.0, 1.0 - normalized_distance)
```

**Exemplo:**
```
Orçamento: R$ 40.000 - R$ 80.000
Meio: R$ 60.000

Carro A: R$ 60.000 → distance = 0 → score = 1.0 ⭐⭐⭐⭐⭐
Carro B: R$ 50.000 → distance = 10k → score = 0.5 ⭐⭐⭐
Carro C: R$ 40.000 → distance = 20k → score = 0.0 ⭐
```

---

## Pesos Dinâmicos por Perfil

Os pesos dos 4 componentes variam conforme o perfil de uso:

| Perfil | Category | Priorities | Preferences | Budget |
|--------|----------|------------|-------------|--------|
| **Padrão** | 30% | 40% | 20% | 10% |
| **Família** | 40% ⬆️ | 45% ⬆️ | 10% ⬇️ | 5% ⬇️ |
| **Primeiro Carro** | 35% ⬆️ | 50% ⬆️ | 10% ⬇️ | 5% ⬇️ |
| **Trabalho** | 25% ⬇️ | 45% ⬆️ | 20% | 10% |
| **Comercial** | 45% ⬆️ | 35% ⬇️ | 15% ⬇️ | 5% ⬇️ |
| **Lazer** | 35% ⬆️ | 40% | 15% ⬇️ | 10% |
| **Transporte App** | 50% ⬆️ | 35% ⬇️ | 10% ⬇️ | 5% ⬇️ |

### Justificativas

- **Família:** Categoria (SUV/Van) e prioridades (segurança/espaço) são críticas
- **Primeiro Carro:** Prioridades (economia/facilidade) são mais importantes que marca
- **Comercial:** Categoria (Pickup/Van) é essencial, prioridades secundárias
- **Transporte App:** Categoria (Sedan/SUV) é crítica para aprovação nos apps

---

## Filtros Contextuais

Além do score, o sistema aplica filtros contextuais:

### 1. Filtro de Família com Crianças

Se `uso_principal = "familia"` E `tem_criancas = true`:

**Prioriza carros com:**
- ISOFIX nos itens de segurança
- `score_familia >= 0.6`
- Categoria: SUV, Van ou Sedan

### 2. Filtro de Primeiro Carro

Se `primeiro_carro = true` OU `uso_principal = "primeiro_carro"`:

**Prioriza carros:**
- Categoria: Hatch ou Compacto
- `score_economia >= 0.7`
- Câmbio: Manual (mais simples)
- **Evita:** SUV, Pickup, Van

### 3. Filtro de Transporte de Passageiros

Se `uso_principal = "transporte_passageiros"`:

**Valida contra lista oficial:**
- Uber/99 modelos aceitos (150+ modelos)
- Categorias: UberX, Comfort, Black
- Requisitos: 4 portas, 5 lugares, ar-condicionado, ano mínimo

---

## Filtros Geográficos

### 1. Raio de Distância

Se `raio_km` definido:
- Calcula distância entre usuário e concessionária
- **Elimina** carros fora do raio

### 2. Priorização Geográfica

Ordena resultados por proximidade:
1. Mesma cidade
2. Mesmo estado
3. Outros estados

---

## Exemplo Completo de Cálculo

### Perfil do Usuário
```json
{
  "uso_principal": "familia",
  "orcamento_min": 80000,
  "orcamento_max": 150000,
  "prioridades": {
    "economia": 3,
    "espaco": 5,
    "performance": 2,
    "conforto": 4,
    "seguranca": 5
  },
  "tem_criancas": true
}
```

### Carro: Hyundai Creta 2020 - R$ 81.990

**1. Category Score (peso 40%)**
- Categoria: SUV
- Uso: família
- Score: 0.95

**2. Priorities Score (peso 45%)**
```
Prioridades normalizadas:
- economia: 3/5 = 0.6
- espaco: 5/5 = 1.0
- performance: 2/5 = 0.4
- conforto: 4/5 = 0.8
- seguranca: 5/5 = 1.0

Scores do carro:
- score_economia: 0.8
- score_familia: 0.9
- score_performance: 0.5
- score_conforto: 0.7
- score_seguranca: 0.8

Score = (0.8×0.6 + 0.9×1.0 + 0.5×0.4 + 0.7×0.8 + 0.8×1.0) / (0.6+1.0+0.4+0.8+1.0)
      = (0.48 + 0.9 + 0.2 + 0.56 + 0.8) / 3.8
      = 2.94 / 3.8
      = 0.77
```

**3. Preferences Score (peso 10%)**
- Sem preferências específicas
- Score: 0.5

**4. Budget Score (peso 5%)**
```
Orçamento: R$ 80.000 - R$ 150.000
Meio: R$ 115.000
Preço: R$ 81.990
Distance: R$ 33.010
Normalized: 33.010 / 35.000 = 0.94
Score: 1.0 - 0.94 = 0.06
```

**Match Score Final**
```
Score = (0.95 × 0.40) + (0.77 × 0.45) + (0.5 × 0.10) + (0.06 × 0.05)
      = 0.38 + 0.35 + 0.05 + 0.003
      = 0.783
      = 78% de match
```

---

## Observações Importantes

1. **Scores são dinâmicos:** Calculados em tempo real para cada requisição
2. **Não há cache:** Cada busca recalcula todos os scores
3. **Filtros são eliminatórios:** Aplicados antes do cálculo de score
4. **Pesos variam por perfil:** Otimizam matching para cada contexto
5. **Normalização:** Todos os scores são normalizados para 0.0-1.0
6. **Transparência:** Justificativas explicam o match para o usuário

---

## Próximas Melhorias (Roadmap)

- [ ] Machine Learning para ajustar pesos automaticamente
- [ ] Feedback loop para refinar scores baseado em conversões
- [ ] A/B testing de diferentes fórmulas de score
- [ ] Personalização baseada em histórico do usuário
- [ ] Scores contextuais por região/clima
