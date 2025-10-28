# 🎯 Guia Rápido: Sistema de Prioridades

## ❓ A Pergunta

**"Como definimos as prioridades principais entre 5 para escolhermos e são definidas só 3?"**

## ✅ A Resposta Simples

1. **Usuário define 5 prioridades** (escala 1-5 cada)
2. **Sistema usa TODAS as 5** no cálculo do score
3. **Sistema mostra apenas Top 3** para o usuário

**Por quê?** Melhor UX sem perder precisão!

---

## 📊 Exemplo Visual

### **Input do Usuário (Questionário)**

```
┌─────────────────────────────────────────┐
│  Defina suas prioridades (1-5):        │
├─────────────────────────────────────────┤
│  Economia:     ⭐⭐⭐⭐ (4)              │
│  Espaço:       ⭐⭐⭐⭐⭐ (5)            │
│  Performance:  ⭐⭐ (2)                  │
│  Conforto:     ⭐⭐⭐⭐ (4)              │
│  Segurança:    ⭐⭐⭐⭐⭐ (5)            │
└─────────────────────────────────────────┘
```

### **Processamento (Backend)**

```
┌─────────────────────────────────────────┐
│  1. ORDENAR por valor (maior → menor)  │
├─────────────────────────────────────────┤
│  Espaço:      5  ← Top 1                │
│  Segurança:   5  ← Top 2                │
│  Economia:    4  ← Top 3                │
│  Conforto:    4  ← Não mostrado         │
│  Performance: 2  ← Não mostrado         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  2. CALCULAR score (usa TODAS as 5)    │
├─────────────────────────────────────────┤
│  Score = (                              │
│    (carro.economia * 4) +               │
│    (carro.espaco * 5) +                 │
│    (carro.performance * 2) +            │
│    (carro.conforto * 4) +               │
│    (carro.seguranca * 5)                │
│  ) / (4+5+2+4+5)                        │
│                                         │
│  Score = 16.2 / 20 = 0.81 (81%)        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  3. EXTRAIR Top 3 para mostrar         │
├─────────────────────────────────────────┤
│  top_priorities = [                     │
│    "Espaço",                            │
│    "Segurança",                         │
│    "Economia"                           │
│  ]                                      │
└─────────────────────────────────────────┘
```

### **Output para Usuário (Resultados)**

```
┌─────────────────────────────────────────┐
│  📋 Resumo do Seu Perfil                │
├─────────────────────────────────────────┤
│  Orçamento: R$ 50.000 - R$ 80.000       │
│  Uso: Família                           │
│  Localização: São Paulo, SP             │
│                                         │
│  🎯 Suas Prioridades:                   │
│  • Espaço                               │
│  • Segurança                            │
│  • Economia                             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  🚗 JEEP COMPASS SPORT 2.0              │
│  Match: 81% ⭐⭐⭐⭐                      │
├─────────────────────────────────────────┤
│  Por que recomendamos:                  │
│  ✓ Amplo espaço para família            │
│  ✓ Excelente segurança (6 airbags)      │
│  ✓ Boa economia para categoria          │
└─────────────────────────────────────────┘
```

---

## 🔍 Detalhamento

### **Por Que Coletar 5?**

✅ Captura preferências completas do usuário  
✅ Algoritmo mais preciso  
✅ Diferenciação entre carros similar  
✅ Flexibilidade para diferentes perfis  

### **Por Que Usar Todas as 5 no Cálculo?**

✅ Não perde informação valiosa  
✅ Score mais justo e preciso  
✅ Considera todas as preferências  
✅ Mesmo prioridades baixas influenciam  

**Exemplo**:
```
Carro A: economia=0.9, performance=0.3
Carro B: economia=0.7, performance=0.8

Usuário: economia=5, performance=1

Score A = (0.9*5 + 0.3*1) / 6 = 4.8/6 = 0.80
Score B = (0.7*5 + 0.8*1) / 6 = 4.3/6 = 0.72

Carro A vence! (mesmo com performance baixa)
```

Se ignorássemos performance (valor 1), perderíamos essa diferenciação.

### **Por Que Mostrar Apenas Top 3?**

✅ **UX Limpa**: Fácil de ler e entender  
✅ **Foco**: Destaca o que realmente importa  
✅ **Não Sobrecarrega**: Informação digestível  
✅ **Impacto Visual**: Mais memorável  

**Comparação**:

❌ **Mostrar todas as 5**:
```
Suas Prioridades:
• Espaço (5)
• Segurança (5)
• Economia (4)
• Conforto (4)
• Performance (2)
```
→ Confuso, muito texto, menos impactante

✅ **Mostrar Top 3**:
```
Suas Prioridades:
• Espaço
• Segurança
• Economia
```
→ Claro, direto, impactante

---

## 🎨 Implementação

### **1. Coleta (Frontend)**

```typescript
// Step 2 do Questionário
const [priorities, setPriorities] = useState({
  economia: 3,
  espaco: 3,
  performance: 3,
  conforto: 3,
  seguranca: 3
})

// Usuário ajusta com sliders
<Slider
  min={1}
  max={5}
  value={priorities.economia}
  onChange={(val) => setPriorities({...priorities, economia: val})}
/>
```

### **2. Envio (API Call)**

```typescript
// Envia TODAS as 5 prioridades
const response = await api.post('/recommend', {
  orcamento_min: 50000,
  orcamento_max: 80000,
  uso_principal: 'familia',
  prioridades: {
    economia: 4,
    espaco: 5,
    performance: 2,
    conforto: 4,
    seguranca: 5
  }
})
```

### **3. Processamento (Backend)**

```python
# Ordenar e pegar Top 3
sorted_priorities = sorted(
    profile.prioridades.items(),
    key=lambda x: x[1],
    reverse=True
)

top_3 = [
    priority_labels[key]
    for key, value in sorted_priorities[:3]
    if value > 0
]

# Calcular score com TODAS as 5
score = sum(
    car.scores[key] * profile.prioridades[key]
    for key in profile.prioridades.keys()
) / sum(profile.prioridades.values())
```

### **4. Resposta (API Response)**

```json
{
  "profile_summary": {
    "top_priorities": ["Espaço", "Segurança", "Economia"]
  },
  "recommendations": [
    {
      "car": {...},
      "match_score": 0.81,
      "justification": "Amplo espaço, excelente segurança, boa economia"
    }
  ]
}
```

### **5. Exibição (Frontend)**

```typescript
// Mostra apenas Top 3
<HStack>
  {profileSummary.top_priorities.map(priority => (
    <Badge key={priority}>{priority}</Badge>
  ))}
</HStack>
```

---

## 📈 Casos de Uso

### **Caso 1: Família com Crianças**

```
Input:
  economia: 3, espaco: 5, performance: 1, conforto: 4, seguranca: 5

Top 3 Mostradas:
  1. Espaço (5)
  2. Segurança (5)
  3. Conforto (4)

Recomendação:
  SUV familiar com 6 airbags e amplo porta-malas
```

### **Caso 2: Jovem Profissional**

```
Input:
  economia: 5, espaco: 2, performance: 4, conforto: 3, seguranca: 3

Top 3 Mostradas:
  1. Economia (5)
  2. Performance (4)
  3. Conforto (3)

Recomendação:
  Hatch econômico com bom desempenho
```

### **Caso 3: Executivo**

```
Input:
  economia: 2, espaco: 3, performance: 5, conforto: 5, seguranca: 4

Top 3 Mostradas:
  1. Performance (5)
  2. Conforto (5)
  3. Segurança (4)

Recomendação:
  Sedan premium com motor potente e acabamento luxuoso
```

---

## ✅ Checklist de Implementação

### **Backend**
- [x] Modelo aceita 5 prioridades (1-5 cada)
- [x] Algoritmo usa TODAS as 5 no cálculo
- [x] Endpoint extrai Top 3 para resposta
- [x] Ordenação correta (maior → menor)
- [x] Filtro para valores > 0

### **Frontend**
- [ ] Questionário coleta 5 prioridades
- [ ] Sliders de 1-5 para cada
- [ ] Explicação de cada prioridade
- [ ] Envia todas as 5 para API
- [ ] Exibe apenas Top 3 nos resultados
- [ ] Badges ou tags visuais

### **UX**
- [ ] Labels claros para cada prioridade
- [ ] Feedback visual nos sliders
- [ ] Tooltip explicando cada uma
- [ ] Top 3 destacadas visualmente
- [ ] Justificativa usa as Top 3

---

## 🎯 Resumo Final

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  COLETA: 5 prioridades (1-5 cada)              │
│     ↓                                           │
│  CALCULA: Usa TODAS as 5 no score              │
│     ↓                                           │
│  MOSTRA: Apenas Top 3 para o usuário           │
│                                                 │
│  Resultado: UX limpa + Algoritmo preciso ✅     │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Benefícios**:
- ✅ Usuário não fica sobrecarregado
- ✅ Sistema não perde informação
- ✅ Recomendações mais precisas
- ✅ Interface mais limpa

---

**Criado em**: 15 de Outubro, 2025  
**Versão**: 1.0  
**Status**: ✅ DOCUMENTADO

