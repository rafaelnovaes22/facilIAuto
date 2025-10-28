# 📅 Quando e Como Implementar a Fase 2

## 🎯 Quando Implementar?

Implemente a Fase 2 (Feature Engineering + Treinamento do Modelo) quando:

✅ **Critério Principal**: Mínimo de **500 interações** coletadas  
✅ **Critério Ideal**: Mínimo de **1000 interações** para melhor qualidade  
✅ **Critério de Diversidade**: Pelo menos **50 carros diferentes** com interações  
✅ **Critério de Distribuição**: Pelo menos **20% de interações de alto interesse** (WhatsApp)

## 📊 Como Verificar se Está Pronto?

### 1. Verificar Total de Interações

```bash
curl http://localhost:8000/api/ml/stats
```

Procure por:
```json
{
  "ml_readiness": {
    "ready_for_training": true,  // ← Deve ser true
    "progress_percentage": 100,   // ← Deve ser >= 100
    "interactions_needed": 0      // ← Deve ser 0
  }
}
```

### 2. Verificar Qualidade dos Dados

Execute este script Python para análise:

```python
import json

# Carregar dados
with open('platform/backend/data/interactions/user_interactions.json', 'r') as f:
    data = json.load(f)

interactions = data['interactions']

# Análise básica
total = len(interactions)
unique_cars = len(set(i['car_id'] for i in interactions))
unique_sessions = len(set(i['session_id'] for i in interactions))

# Distribuição por tipo
types = {}
for i in interactions:
    t = i['interaction_type']
    types[t] = types.get(t, 0) + 1

print(f"Total de interações: {total}")
print(f"Carros únicos: {unique_cars}")
print(f"Sessões únicas: {unique_sessions}")
print(f"\nDistribuição:")
for t, count in types.items():
    print(f"  {t}: {count} ({count/total*100:.1f}%)")

# Verificar se está pronto
ready = (
    total >= 500 and
    unique_cars >= 50 and
    types.get('whatsapp_contact', 0) >= total * 0.1  # Pelo menos 10% de alto interesse
)

print(f"\n{'✅' if ready else '❌'} Pronto para treinar: {ready}")
```

### 3. Verificar Distribuição Temporal

Idealmente, os dados devem cobrir pelo menos **2 semanas** para capturar diferentes padrões de comportamento.

---

## 🚀 Como Implementar a Fase 2

Quando os critérios forem atingidos, siga estes passos:

### Passo 1: Abrir o Spec

```bash
# Abrir arquivo de tarefas
code .kiro/specs/ml-user-learning/tasks.md
```

### Passo 2: Executar Tarefas da Fase 2

No arquivo `tasks.md`, execute as tarefas 5, 6 e 7:

- [ ] **Tarefa 5**: Implementar feature engineering
- [ ] **Tarefa 6**: Implementar treinamento do modelo ML
- [ ] **Tarefa 7**: Implementar predição com modelo ML

### Passo 3: Treinar Modelo

```bash
cd platform/backend
python scripts/train_ml_model.py
```

Você verá output como:
```
[INFO] Carregando 1250 interações...
[INFO] Preparando features...
[INFO] Features criadas: 10 features, 1250 amostras
[INFO] Treinando modelo Random Forest...
[INFO] Modelo treinado com sucesso!
[INFO] Métricas:
  - RMSE: 0.45
  - MAE: 0.32
  - R² Score: 0.68
[OK] Modelo salvo em: data/ml_models/recommendation_model_v1.pkl
```

### Passo 4: Validar Modelo

Verifique se o modelo foi salvo:
```bash
ls platform/backend/data/ml_models/
# Deve mostrar:
# - recommendation_model_v1.pkl
# - feature_scaler.pkl
# - model_metadata.json
```

Verifique metadata:
```bash
cat platform/backend/data/ml_models/model_metadata.json
```

### Passo 5: Testar Predições

Crie um script de teste:

```python
from services.ml_service import MLService

ml_service = MLService()
ml_service.load_model()

# Testar predição
user_prefs = {
    "budget": 120000,
    "usage": "urbano",
    "priorities": ["economia", "conforto"]
}

car = {
    "marca": "Toyota",
    "modelo": "Corolla",
    "ano": 2022,
    "preco": 115990,
    "categoria": "Sedan",
    "combustivel": "Flex",
    "cambio": "Automático",
    "quilometragem": 25000
}

score = ml_service.predict_score(user_prefs, car)
print(f"Score ML: {score:.2f}")  # Deve retornar valor entre 0 e 1
```

---

## 🔄 Implementar Fase 3 (Sistema Híbrido)

Após validar o modelo, implemente a Fase 3:

### Passo 1: Executar Tarefas 8 e 9

No arquivo `tasks.md`:

- [ ] **Tarefa 8**: Implementar HybridRecommendationEngine
- [ ] **Tarefa 9**: Integrar sistema híbrido na API

### Passo 2: Testar Sistema Híbrido

```bash
# Fazer requisição de recomendação
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "orcamento_min": 100000,
    "orcamento_max": 150000,
    "uso_principal": "urbano",
    "prioridades": {
      "economia": 0.8,
      "conforto": 0.6,
      "performance": 0.3
    }
  }'
```

Verifique que os carros retornados têm:
- `match_score` (score híbrido)
- `ml_score` (score do modelo ML, para debug)

### Passo 3: Comparar Resultados

Compare recomendações:
- **Apenas regras** (sistema atual)
- **Sistema híbrido** (regras + ML)

Verifique se o sistema híbrido:
- Mantém qualidade das recomendações
- Adiciona personalização baseada em comportamento real
- Não degrada performance

### Passo 4: Ajustar Pesos (Opcional)

Se necessário, ajuste os pesos em `HybridRecommendationEngine`:

```python
# Padrão: 70% regras + 30% ML
self.rule_weight = 0.7
self.ml_weight = 0.3

# Mais conservador: 80% regras + 20% ML
self.rule_weight = 0.8
self.ml_weight = 0.2

# Mais agressivo: 60% regras + 40% ML
self.rule_weight = 0.6
self.ml_weight = 0.4
```

### Passo 5: Deploy Gradual

1. **Teste A/B**: 10% dos usuários com ML, 90% com regras
2. **Monitorar métricas**: Taxa de cliques, conversões, tempo de sessão
3. **Aumentar gradualmente**: 25% → 50% → 75% → 100%

---

## 📊 Métricas para Monitorar

### Durante Treinamento
- **RMSE** (Root Mean Squared Error): < 0.5 é bom
- **MAE** (Mean Absolute Error): < 0.4 é bom
- **R² Score**: > 0.6 é aceitável, > 0.7 é bom

### Em Produção
- **Taxa de cliques**: Deve aumentar ou manter
- **Taxa de conversão** (WhatsApp): Deve aumentar
- **Tempo de sessão**: Deve aumentar (usuários mais engajados)
- **Latência**: Deve manter < 100ms

---

## 🔄 Retreinamento Periódico

Após ativar o ML, configure retreinamento periódico:

### Frequência Recomendada
- **Inicial**: Semanal (primeiras 4 semanas)
- **Estável**: Quinzenal ou mensal

### Como Retreinar

```bash
# Manual
cd platform/backend
python scripts/retrain_ml_model.py

# Automático (cron job)
# Adicionar ao crontab:
0 2 * * 0 cd /path/to/platform/backend && python scripts/retrain_ml_model.py
```

### Critérios para Retreinar
- Acumulou 500+ novas interações desde último treino
- Performance do modelo degradou (monitorar métricas)
- Mudanças significativas no catálogo de carros

---

## ⚠️ Troubleshooting

### Problema: Modelo não treina

**Possíveis causas**:
- Dados insuficientes (< 500 interações)
- Dados corrompidos no JSON
- Falta de diversidade (poucos carros únicos)

**Solução**:
```python
# Verificar dados
python scripts/validate_training_data.py
```

### Problema: Performance ruim do modelo

**Possíveis causas**:
- Dados de baixa qualidade
- Features inadequadas
- Hiperparâmetros não otimizados

**Solução**:
1. Analisar distribuição dos dados
2. Adicionar mais features relevantes
3. Fazer grid search de hiperparâmetros

### Problema: ML não melhora recomendações

**Possíveis causas**:
- Peso do ML muito baixo (< 20%)
- Modelo não capturou padrões relevantes
- Dados de treinamento não representativos

**Solução**:
1. Aumentar peso do ML gradualmente
2. Retreinar com mais dados
3. Revisar features utilizadas

---

## 📚 Recursos Adicionais

### Documentação
- `requirements.md` - Requisitos completos
- `design.md` - Design técnico detalhado
- `tasks.md` - Plano de implementação

### Scripts Úteis
- `train_ml_model.py` - Treinar modelo
- `retrain_ml_model.py` - Retreinar modelo
- `validate_training_data.py` - Validar dados

### Endpoints
- `POST /api/interactions/track` - Coletar interações
- `GET /api/ml/stats` - Estatísticas do sistema
- `GET /api/ml/health` - Health check do ML
- `POST /recommend` - Recomendações (híbrido quando ML ativo)

---

## ✅ Checklist de Implementação

### Antes de Começar
- [ ] Verificar que tem 500+ interações
- [ ] Analisar qualidade dos dados
- [ ] Revisar spec completo

### Durante Implementação
- [ ] Implementar feature engineering (Tarefa 5)
- [ ] Implementar treinamento (Tarefa 6)
- [ ] Implementar predição (Tarefa 7)
- [ ] Treinar primeiro modelo
- [ ] Validar métricas do modelo

### Ativação do Sistema Híbrido
- [ ] Implementar HybridEngine (Tarefa 8)
- [ ] Integrar na API (Tarefa 9)
- [ ] Testar localmente
- [ ] Fazer A/B testing
- [ ] Deploy gradual

### Pós-Deploy
- [ ] Monitorar métricas
- [ ] Configurar retreinamento
- [ ] Documentar aprendizados
- [ ] Planejar melhorias

---

## 🎯 Objetivo Final

Quando tudo estiver implementado, você terá:

✅ Sistema de recomendação híbrido (regras + ML)  
✅ Modelo que aprende continuamente com usuários reais  
✅ Recomendações cada vez mais personalizadas  
✅ Vantagem competitiva baseada em dados proprietários  

**Boa sorte com a implementação!** 🚀

---

**Documento criado**: 14 de Outubro de 2024  
**Próxima revisão**: Quando atingir 500+ interações
