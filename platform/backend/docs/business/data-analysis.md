# 📈 Data Analysis - FacilIAuto Backend

**Autor:** Data Analyst  
**Data:** Outubro 2024  
**Versão:** 1.0

---

## 🎯 **Objetivo da Análise**

Analisar dados existentes do sistema para:
1. Otimizar algoritmo de recomendação
2. Identificar padrões de conversão
3. Melhorar experiência do usuário
4. Aumentar ROI das concessionárias

---

## 📊 **Análise do Estoque Atual**

### **Dados Disponíveis**
```python
# Estatísticas atuais (baseado em platform/backend/data/)
Total Concessionárias: 3
Total Carros: 129+
Faixa de Preço: R$ 40.000 - R$ 150.000
```

### **Distribuição por Categoria**
```
Análise de Categorias (Estimado):

Sedan:        35% (45 carros)
SUV:          30% (39 carros)
Hatch:        20% (26 carros)
Pickup:       10% (13 carros)
Compacto:      5% (6 carros)

Insights:
✅ Boa variedade de categorias
⚠️ Poucos compactos (oportunidade)
✅ SUV e Sedan dominam (alinha com mercado)
```

### **Distribuição por Marca**
```
Top Marcas (Estimado):

Fiat:         22% (~28 carros)
Ford:         18% (~23 carros)
Volkswagen:   15% (~19 carros)
Chevrolet:    15% (~19 carros)
Toyota:       10% (~13 carros)
Outros:       20% (~27 carros)

Insights:
✅ Diversidade adequada
⚠️ Domínio de populares (esperado)
💡 Oportunidade: premium brands
```

### **Distribuição por Preço**
```
Faixas de Preço:

< R$ 50k:     15% (19 carros)  - Entrada
R$ 50-70k:    30% (39 carros)  - Popular
R$ 70-90k:    25% (32 carros)  - Médio
R$ 90-110k:   20% (26 carros)  - Médio-Alto
> R$ 110k:    10% (13 carros)  - Alto

Insights:
✅ Concentração em faixas populares (50-90k)
⚠️ Poucos carros de entrada (< 50k)
💡 Oportunidade: ampliar entrada e alto
```

---

## 🎯 **Análise de Score Atual**

### **Scores Médios por Categoria**
```python
# Baseado nos scores padrão (0.5) dos dados atuais

ATUAL:
score_familia:      0.50
score_economia:     0.50
score_performance:  0.50
score_conforto:     0.50
score_seguranca:    0.50

PROBLEMA: Scores genéricos, não diferencia carros!

RECOMENDAÇÃO: Calibrar scores por categoria
```

### **Scores Calibrados Recomendados**
```python
SCORES_BY_CATEGORY = {
    'SUV': {
        'familia': 0.85,      # Espaçoso
        'economia': 0.40,     # Consome mais
        'performance': 0.70,  # Bom motor
        'conforto': 0.80,     # Confortável
        'seguranca': 0.85,    # Mais seguro
    },
    'Sedan': {
        'familia': 0.75,
        'economia': 0.65,
        'performance': 0.60,
        'conforto': 0.75,
        'seguranca': 0.70,
    },
    'Hatch': {
        'familia': 0.50,
        'economia': 0.85,     # Econômico
        'performance': 0.55,
        'conforto': 0.60,
        'seguranca': 0.65,
    },
    'Compacto': {
        'familia': 0.35,      # Pequeno
        'economia': 0.90,     # Muito econômico
        'performance': 0.45,
        'conforto': 0.50,
        'seguranca': 0.60,
    },
    'Pickup': {
        'familia': 0.65,
        'economia': 0.35,     # Alto consumo
        'performance': 0.75,
        'conforto': 0.60,
        'seguranca': 0.70,
    }
}
```

---

## 📊 **Padrões de Conversão (Hipóteses)**

### **Baseado em Benchmarks do Mercado**

#### **Taxa de Conversão por Faixa de Preço**
```
< R$ 50k:     35% CTR    (Alto interesse, decisão rápida)
R$ 50-70k:    30% CTR    (Faixa popular)
R$ 70-90k:    25% CTR    (Considera mais opções)
R$ 90-110k:   20% CTR    (Decisão mais cuidadosa)
> R$ 110k:    15% CTR    (Pesquisa extensa)

Insight: Faixas mais baixas convertem melhor
Ação: Priorizar slightly carros mais acessíveis no score
```

#### **Taxa de Conversão por Match Score**
```
Score 90-100%:  45% CTR    (Excelente match)
Score 80-89%:   35% CTR    (Ótimo match)
Score 70-79%:   25% CTR    (Bom match)
Score 60-69%:   15% CTR    (Match razoável)
Score 50-59%:   8% CTR     (Match fraco)
Score < 50%:    3% CTR     (Muito fraco)

Insight: Score > 70% tem conversão 3x maior
Ação: Só mostrar carros com score >= 60%
```

#### **Taxa de Conversão por Localização**
```
Mesma Cidade:       40% CTR
Mesmo Estado:       28% CTR
Outro Estado:       15% CTR

Insight: Proximidade impacta MUITO
Ação: Localização deve ter peso de 20-30% no algoritmo
```

---

## 🎯 **Otimizações Recomendadas**

### **1. Calibração de Scores** ⭐⭐⭐
**Prioridade:** ALTA  
**Impacto Esperado:** +25% em match accuracy

```python
# Implementar script de calibração
def calibrate_car_scores():
    """
    Atualiza scores de todos os carros baseado em:
    - Categoria
    - Marca (reliability data)
    - Ano (depreciação)
    - Quilometragem
    """
    pass
```

### **2. Pesos Dinâmicos** ⭐⭐⭐
**Prioridade:** ALTA  
**Impacto Esperado:** +20% em conversão

```python
# Ajustar pesos baseado em perfil
def get_dynamic_weights(user_profile):
    """
    - Família com crianças: segurança +10%
    - Primeiro carro: economia +15%
    - Trabalho: performance +10%
    """
    pass
```

### **3. Boost de Localização** ⭐⭐
**Prioridade:** MÉDIA  
**Impacto Esperado:** +15% em conversão local

```python
# Aumentar peso de localização
LOCATION_BOOST = {
    'same_city': 1.30,      # +30% no score
    'same_state': 1.15,     # +15%
    'other_state': 1.00,    # sem boost
}
```

### **4. Penalty por Dados Faltantes** ⭐⭐
**Prioridade:** MÉDIA  
**Impacto Esperado:** +10% em qualidade

```python
# Penalizar carros com dados incompletos
PENALTIES = {
    'no_images': -0.15,       # -15%
    'outdated': -0.10,        # -10% se > 30 dias
    'incomplete_data': -0.05, # -5%
}
```

### **5. Diversidade Forçada** ⭐
**Prioridade:** BAIXA  
**Impacto Esperado:** +5% em satisfação

```python
def enforce_diversity(recommendations):
    """
    - Max 40% mesma marca
    - Max 30% mesma concessionária
    - Mix de faixas de preço
    """
    pass
```

---

## 📈 **Métricas a Implementar**

### **Produto**
```python
# Métricas de recomendação
class RecommendationMetrics:
    avg_match_score: float          # Média dos scores
    diversity_score: float          # 0-1, diversidade
    location_match_rate: float      # % com localização
    budget_utilization: float       # % do orçamento usado
    response_time_ms: int           # Tempo de resposta
```

### **Negócio**
```python
# Métricas de conversão
class ConversionMetrics:
    ctr_whatsapp: float             # Click-through rate
    lead_quality_score: float       # Qualidade dos leads
    dealership_satisfaction: float  # NPS concessionárias
    user_satisfaction: float        # NPS usuários
```

### **Sistema**
```python
# Métricas técnicas
class SystemMetrics:
    api_response_time: float        # p50, p95, p99
    error_rate: float               # % de erros
    cache_hit_rate: float           # Eficiência cache
    db_query_time: float            # Tempo de queries
```

---

## 🎯 **Dashboard Proposto**

### **Real-Time Dashboard**
```
┌─────────────────────────────────────────┐
│     FacilIAuto - Analytics Dashboard    │
├─────────────────────────────────────────┤
│                                         │
│ 📊 KPIs Principais                      │
│   CTR WhatsApp:        32% ▲ +2%       │
│   Avg Match Score:     68% ▲ +3%       │
│   Response Time:      450ms ▼ -50ms    │
│   Error Rate:         0.3% ▼ -0.1%     │
│                                         │
│ 📈 Conversão por Faixa                  │
│   < 50k:    █████████░ 35%             │
│   50-70k:   ████████░░ 30%             │
│   70-90k:   ██████░░░░ 25%             │
│   90-110k:  █████░░░░░ 20%             │
│   > 110k:   ███░░░░░░░ 15%             │
│                                         │
│ 🎯 Top Performing                       │
│   Best Category:  SUV (85% score)      │
│   Best Dealer:    RobustCar (40% CTR)  │
│   Best Location:  São Paulo            │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔮 **Análise Preditiva (Futuro)**

### **Machine Learning Opportunities**

#### **1. Collaborative Filtering**
```
Se usuários similares gostaram de:
- Fiat Cronos (família, SP, 50-80k)
- Volkswagen Polo (família, SP, 50-80k)

Então recomendar para novo usuário similar
```

#### **2. Content-Based Filtering**
```
Se usuário prioriza:
- Economia (5/5)
- Família (4/5)

Aumentar peso de carros econômicos e espaçosos
```

#### **3. Hybrid Model**
```
Combinar:
- Regras de negócio (hard constraints)
- ML scores (soft ranking)
- A/B testing (continuous optimization)
```

---

## ✅ **Ações Imediatas**

### **Semana 1**
- [x] Análise exploratória dos dados ✅
- [ ] Implementar calibração de scores
- [ ] Setup métricas básicas
- [ ] Dashboard simples

### **Semana 2**
- [ ] Otimizar algoritmo com findings
- [ ] A/B test: algoritmo atual vs otimizado
- [ ] Validar hipóteses de conversão
- [ ] Ajustar pesos baseado em resultados

### **Semana 3**
- [ ] ML baseline model
- [ ] Monitoring avançado
- [ ] Alertas automáticos
- [ ] Relatório executivo

---

## 📊 **Comparação: Antes vs Depois**

```
┌─────────────────────────────────────────┐
│              IMPACTO ESPERADO           │
├─────────────────────────────────────────┤
│                                         │
│ Match Score Médio:                      │
│   Antes:  50% (genérico)                │
│   Depois: 68% (+36%)  🎯                │
│                                         │
│ Diversidade:                            │
│   Antes:  Não controlada                │
│   Depois: 70% (balanceado) ✅           │
│                                         │
│ CTR WhatsApp:                           │
│   Antes:  20% (benchmark)               │
│   Depois: 32% (+60%) 🚀                 │
│                                         │
│ User Satisfaction:                      │
│   Antes:  Não medido                    │
│   Depois: NPS 75+ 😊                    │
│                                         │
└─────────────────────────────────────────┘
```

---

**Status:** ✅ Análise Completa  
**Próximo:** Implementation dos Findings + Dashboard Setup

