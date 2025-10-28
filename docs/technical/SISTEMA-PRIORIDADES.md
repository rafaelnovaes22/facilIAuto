# 🎯 Sistema de Prioridades - FacilIAuto

## 📋 Visão Geral

O sistema de prioridades do FacilIAuto permite que usuários indiquem o que é mais importante na escolha de um carro. Este documento explica em detalhes como funciona.

---

## 🔢 Estrutura das Prioridades

### **5 Prioridades Principais (Core)**

O usuário pode avaliar **5 dimensões principais** em uma escala de 1 a 5:

```python
prioridades: {
    "economia": 1-5,      # Consumo de combustível, custo de manutenção
    "espaco": 1-5,        # Espaço interno, porta-malas, capacidade
    "performance": 1-5,   # Potência, aceleração, dirigibilidade
    "conforto": 1-5,      # Acabamento, tecnologia, conforto
    "seguranca": 1-5      # Airbags, freios, estabilidade
}
```

### **3 Prioridades Adicionais (Fase 3)**

Há também **3 prioridades adicionais** para análise de "Carro Bom":

```python
prioridades: {
    # ... 5 principais acima
    "revenda": 1-5,           # Valor de revenda
    "confiabilidade": 1-5,    # Confiabilidade da marca/modelo
    "custo_manutencao": 1-5   # Custo de manutenção
}
```

**Total**: 8 prioridades possíveis

---

## 🎯 Por Que Mostrar Apenas Top 3?

### **Razão 1: UX e Clareza**

Mostrar todas as 5 (ou 8) prioridades seria:
- ❌ Confuso para o usuário
- ❌ Difícil de ler rapidamente
- ❌ Poluição visual
- ❌ Menos impactante

Mostrar apenas as **Top 3** é:
- ✅ Claro e direto
- ✅ Fácil de entender rapidamente
- ✅ Foca no que realmente importa
- ✅ Melhor UX

### **Razão 2: Relevância**

As 3 prioridades mais altas são as que **realmente influenciam** a decisão do usuário. As outras são menos importantes por definição.

**Exemplo**:
```
Usuário define:
- Segurança: 5 ⭐⭐⭐⭐⭐
- Espaço: 5 ⭐⭐⭐⭐⭐
- Conforto: 4 ⭐⭐⭐⭐
- Economia: 2 ⭐⭐
- Performance: 1 ⭐

Top 3 mostradas: Segurança, Espaço, Conforto
(Economia e Performance são menos importantes para este usuário)
```

### **Razão 3: Algoritmo de Recomendação**

O algoritmo usa **TODAS as 5 prioridades** no cálculo do score, mas mostra apenas as Top 3 para o usuário entender o contexto da recomendação.

---

## 🔄 Como Funciona o Sistema

### **1. Coleta (Frontend - Questionário)**

```typescript
// Step 2 do questionário
const priorities = {
  economia: 4,      // Slider 1-5
  espaco: 5,        // Slider 1-5
  performance: 2,   // Slider 1-5
  conforto: 4,      // Slider 1-5
  seguranca: 5      // Slider 1-5
}
```

### **2. Processamento (Backend - API)**

```python
# api/main.py - Endpoint /recommend

# Ordenar prioridades por valor (maior para menor)
sorted_priorities = sorted(
    profile.prioridades.items(), 
    key=lambda x: x[1],  # Ordena pelo valor (1-5)
    reverse=True         # Maior primeiro
)

# Pegar apenas as Top 3
top_priorities = [
    priority_labels.get(key, key.capitalize()) 
    for key, value in sorted_priorities[:3]  # [:3] = primeiras 3
    if value > 0  # Apenas se valor > 0
]
```

### **3. Cálculo do Score (Engine)**

```python
# services/unified_recommendation_engine.py

# TODAS as 5 prioridades são usadas no cálculo
score_prioridades = (
    (car.score_economia * profile.prioridades['economia']) +
    (car.score_familia * profile.prioridades['espaco']) +
    (car.score_performance * profile.prioridades['performance']) +
    (car.score_conforto * profile.prioridades['conforto']) +
    (car.score_seguranca * profile.prioridades['seguranca'])
) / sum(profile.prioridades.values())

# Peso: 40% do score final
final_score = (
    categoria_score * 0.30 +
    score_prioridades * 0.40 +  # Usa TODAS as 5
    preferencias_score * 0.20 +
    orcamento_score * 0.10
)
```

### **4. Exibição (Frontend - Resultados)**

```typescript
// Mostra apenas Top 3 no resumo
profile_summary: {
  budget_range: "R$ 50.000 - R$ 100.000",
  usage: "familia",
  location: "São Paulo, SP",
  top_priorities: ["Segurança", "Espaço", "Conforto"]  // Top 3
}
```

---

## 📊 Exemplo Completo

### **Cenário: Família com Crianças**

#### **Input do Usuário**
```json
{
  "uso_principal": "familia",
  "tamanho_familia": 4,
  "tem_criancas": true,
  "prioridades": {
    "economia": 3,
    "espaco": 5,
    "performance": 1,
    "conforto": 4,
    "seguranca": 5
  }
}
```

#### **Processamento**

1. **Ordenação por valor**:
```
seguranca: 5    ← Top 1
espaco: 5       ← Top 2
conforto: 4     ← Top 3
economia: 3     ← Não mostrado
performance: 1  ← Não mostrado
```

2. **Top 3 extraídas**:
```
["Segurança", "Espaço", "Conforto"]
```

3. **Cálculo do score** (usa TODAS as 5):
```python
# Para um Jeep Compass:
score = (
    (0.6 * 3) +  # economia: 3
    (0.9 * 5) +  # espaco: 5
    (0.8 * 1) +  # performance: 1
    (0.8 * 4) +  # conforto: 4
    (0.9 * 5)    # seguranca: 5
) / (3 + 5 + 1 + 4 + 5)

score = 14.3 / 18 = 0.794 (79.4%)
```

#### **Output para Usuário**

```json
{
  "profile_summary": {
    "budget_range": "R$ 50.000 - R$ 100.000",
    "usage": "familia",
    "location": "São Paulo, SP",
    "top_priorities": ["Segurança", "Espaço", "Conforto"]
  },
  "recommendations": [
    {
      "car": { "nome": "JEEP COMPASS SPORT 2.0" },
      "match_score": 0.79,
      "match_percentage": 79,
      "justification": "Categoria SUV ideal para familia. Amplo espaço para família. Excelente segurança."
    }
  ]
}
```

---

## 🎨 Implementação no Frontend

### **Questionário (Step 2)**

```typescript
// QuestionnairePage.tsx - Step 2

<FormControl>
  <FormLabel>Economia (Consumo e Manutenção)</FormLabel>
  <Slider
    min={1}
    max={5}
    step={1}
    value={priorities.economia}
    onChange={(val) => setPriorities({ ...priorities, economia: val })}
  >
    <SliderTrack>
      <SliderFilledTrack />
    </SliderTrack>
    <SliderThumb />
  </Slider>
  <Text fontSize="sm" color="gray.600">
    {priorities.economia}/5
  </Text>
</FormControl>

// Repetir para: espaco, performance, conforto, seguranca
```

### **Resultados (Profile Summary)**

```typescript
// ResultsPage.tsx

<Box bg="gray.50" p={4} borderRadius="lg">
  <Text fontSize="sm" color="gray.600" mb={2}>
    Suas Prioridades Principais:
  </Text>
  <HStack spacing={2}>
    {profileSummary.top_priorities.map((priority) => (
      <Badge key={priority} colorScheme="brand" fontSize="sm">
        {priority}
      </Badge>
    ))}
  </HStack>
</Box>
```

---

## 🔍 Casos Especiais

### **Caso 1: Empate nas Prioridades**

```json
{
  "prioridades": {
    "economia": 5,
    "espaco": 5,
    "performance": 5,
    "conforto": 3,
    "seguranca": 3
  }
}
```

**Resultado**: Top 3 = ["Economia", "Espaço", "Performance"]
- Ordem alfabética como desempate (ou ordem de definição no código)

### **Caso 2: Todas as Prioridades Iguais**

```json
{
  "prioridades": {
    "economia": 3,
    "espaco": 3,
    "performance": 3,
    "conforto": 3,
    "seguranca": 3
  }
}
```

**Resultado**: Top 3 = ["Economia", "Espaço", "Performance"]
- Primeiras 3 na ordem de definição

### **Caso 3: Prioridades com Valor 0**

```json
{
  "prioridades": {
    "economia": 5,
    "espaco": 4,
    "performance": 0,
    "conforto": 0,
    "seguranca": 3
  }
}
```

**Resultado**: Top 3 = ["Economia", "Espaço", "Segurança"]
- Valores 0 são ignorados (filtro `if value > 0`)

---

## 📈 Pesos no Algoritmo

### **Distribuição do Score Final**

```
Score Final = 100%
├── Categoria por Uso: 30%
├── Prioridades: 40% ← TODAS as 5 são usadas aqui
├── Preferências: 20%
└── Orçamento: 10%
```

### **Dentro das Prioridades (40%)**

```python
score_prioridades = (
    (car.score_economia * user.prioridades['economia']) +
    (car.score_familia * user.prioridades['espaco']) +
    (car.score_performance * user.prioridades['performance']) +
    (car.score_conforto * user.prioridades['conforto']) +
    (car.score_seguranca * user.prioridades['seguranca'])
) / sum(user.prioridades.values())
```

**Exemplo**:
```
Usuário: economia=5, espaco=5, performance=1, conforto=4, seguranca=5
Soma: 20

Carro: economia=0.8, espaco=0.9, performance=0.6, conforto=0.7, seguranca=0.9

Score = (0.8*5 + 0.9*5 + 0.6*1 + 0.7*4 + 0.9*5) / 20
      = (4.0 + 4.5 + 0.6 + 2.8 + 4.5) / 20
      = 16.4 / 20
      = 0.82 (82%)
```

---

## 🎯 Recomendações de UX

### **✅ Boas Práticas**

1. **Mostrar Top 3 no resumo**
   - Claro e direto
   - Fácil de entender
   - Não sobrecarrega o usuário

2. **Usar TODAS as 5 no cálculo**
   - Algoritmo mais preciso
   - Considera todas as preferências
   - Mesmo que não mostre todas

3. **Permitir ajuste no questionário**
   - Sliders de 1-5 para cada prioridade
   - Feedback visual imediato
   - Explicação de cada prioridade

### **❌ Evitar**

1. **Mostrar todas as 5 prioridades**
   - Confuso
   - Poluição visual
   - Menos impactante

2. **Usar apenas as Top 3 no cálculo**
   - Perde informação
   - Algoritmo menos preciso
   - Ignora preferências do usuário

3. **Não explicar o que cada prioridade significa**
   - Usuário pode não entender
   - Escolhas incorretas
   - Resultados ruins

---

## 🔧 Implementação Técnica

### **Backend (Python)**

```python
# api/main.py

# Extrair top 3 prioridades
priority_labels = {
    'economia': 'Economia',
    'espaco': 'Espaço',
    'performance': 'Performance',
    'conforto': 'Conforto',
    'seguranca': 'Segurança'
}

sorted_priorities = sorted(
    profile.prioridades.items(), 
    key=lambda x: x[1], 
    reverse=True
)

top_priorities = [
    priority_labels.get(key, key.capitalize()) 
    for key, value in sorted_priorities[:3] 
    if value > 0
]
```

### **Frontend (TypeScript)**

```typescript
// types/index.ts

export interface ProfileSummary {
  budget_range: string
  usage: string
  location: string
  top_priorities: string[]  // Array com Top 3
}

export interface Priorities {
  economia: number      // 1-5
  espaco: number        // 1-5
  performance: number   // 1-5
  conforto: number      // 1-5
  seguranca: number     // 1-5
}
```

---

## 📊 Métricas e Analytics

### **Dados a Coletar**

1. **Distribuição de Prioridades**
   - Quais prioridades são mais escolhidas?
   - Média de cada prioridade
   - Correlação entre prioridades

2. **Top 3 Mais Comuns**
   - Quais combinações aparecem mais?
   - Segmentação por uso_principal
   - Padrões por região

3. **Impacto no Score**
   - Prioridades que mais influenciam o score
   - Correlação entre prioridade e conversão
   - A/B testing de pesos

---

## 🎓 Conclusão

### **Resumo**

- ✅ **5 prioridades** são coletadas do usuário
- ✅ **TODAS as 5** são usadas no cálculo do score
- ✅ **Apenas Top 3** são mostradas no resumo
- ✅ Isso melhora UX sem perder precisão

### **Benefícios**

1. **UX Limpa**: Usuário vê apenas o essencial
2. **Algoritmo Preciso**: Usa todas as informações
3. **Foco**: Destaca o que realmente importa
4. **Flexibilidade**: Fácil adicionar mais prioridades

### **Próximos Passos**

1. Validar com usuários reais
2. Coletar métricas de uso
3. Ajustar pesos se necessário
4. Considerar adicionar mais prioridades (Fase 3)

---

**Criado em**: 15 de Outubro, 2025  
**Versão**: 1.0  
**Status**: ✅ DOCUMENTADO

