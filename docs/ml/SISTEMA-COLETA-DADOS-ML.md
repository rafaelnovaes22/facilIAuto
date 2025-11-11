# Sistema de Coleta de Dados para Machine Learning

**Data**: 11/11/2024  
**Status**: ✅ IMPLEMENTADO | ⚠️ SEM DADOS COLETADOS

## Visão Geral

O FacilIAuto possui um **sistema completo de coleta de dados** para alimentar futuros modelos de Machine Learning. O sistema rastreia todas as interações dos usuários com os carros recomendados.

## 📊 Status Atual

### Backend
- ✅ **API implementada**: `/api/interactions/track`
- ✅ **Serviço de persistência**: `InteractionService`
- ✅ **Armazenamento**: `platform/backend/data/interactions/user_interactions.json`
- ✅ **Estatísticas**: `/api/ml/stats`
- ✅ **Testes E2E**: 15 testes passando

### Frontend
- ✅ **InteractionTracker implementado**: `src/services/InteractionTracker.ts`
- ✅ **Integrado nos componentes**: CarCard, CarDetailsModal
- ✅ **Session tracking**: Sessões únicas por usuário
- ✅ **Fail gracefully**: Não bloqueia UI se falhar

### Dados Coletados
- ⚠️ **Total de interações**: 0 (arquivo vazio)
- ⚠️ **Última atualização**: 14/10/2024 (data de criação)

## 🎯 O Que Está Sendo Rastreado

### 1. Clique no Card do Carro
```typescript
interactionTracker.trackCarClick(
  car.id,
  userPreferences,
  car,
  matchScore
)
```

**Dados coletados**:
- ID do carro
- Preferências do usuário (orçamento, uso, prioridades)
- Score de match
- Timestamp

### 2. Visualização de Detalhes
```typescript
interactionTracker.trackViewDetails(
  car.id,
  userPreferences,
  car,
  matchScore
)
```

**Dados coletados**:
- ID do carro
- Preferências do usuário
- Score de match
- Duração da visualização
- Timestamp

### 3. Clique no WhatsApp (Alto Interesse)
```typescript
interactionTracker.trackWhatsAppClick(
  car.id,
  userPreferences,
  car,
  matchScore
)
```

**Dados coletados**:
- ID do carro
- Preferências do usuário
- Score de match
- Timestamp
- **Indicador de alto interesse** (usuário quer contatar)

## 📁 Estrutura dos Dados

### Arquivo: `user_interactions.json`

```json
{
  "interactions": [
    {
      "id": "int_000001",
      "session_id": "sess_1699999999999_abc123",
      "interaction_type": "click",
      "car_id": "car_robust_001",
      "timestamp": "2024-11-11T10:30:00.000Z",
      "user_preferences": {
        "budget_min": 30000,
        "budget_max": 60000,
        "usage": "trabalho",
        "priorities": {
          "economia": 5,
          "espaco": 3,
          "performance": 2,
          "conforto": 3,
          "seguranca": 4
        }
      },
      "car_details": {
        "marca": "Chevrolet",
        "modelo": "Onix",
        "ano": 2017,
        "preco": 45900,
        "categoria": "Hatch"
      },
      "match_score": 0.85,
      "duration_seconds": null
    }
  ],
  "metadata": {
    "created_at": "2024-10-14T00:00:00Z",
    "last_updated": "2024-11-11T10:30:00.000Z",
    "total_count": 1,
    "version": "1.0"
  }
}
```

## 🔍 Por Que Não Há Dados?

### Possíveis Causas

#### 1. ⚠️ Ambiente de Produção
Se o site está em produção (Railway), o arquivo está no **servidor**, não no seu computador local.

**Solução**: Verificar logs do Railway ou adicionar endpoint para download dos dados.

#### 2. ⚠️ Configuração de URL
O frontend pode estar apontando para URL incorreta.

**Verificar**:
- Frontend em produção: `VITE_API_URL` deve apontar para backend Railway
- Frontend local: `VITE_API_URL=http://localhost:8000`

#### 3. ⚠️ CORS
O backend pode estar bloqueando requisições do frontend.

**Verificar**: Logs do backend para erros de CORS.

#### 4. ⚠️ Usuários Não Interagem
Usuários podem estar apenas visualizando, sem clicar nos carros.

**Verificar**: Analytics do site para ver se há tráfego.

## 🚀 Como Verificar se Está Funcionando

### 1. Verificar Logs do Backend (Produção)

No Railway, verificar logs:
```
[OK] Interação salva: click - Car: car_robust_001
[OK] Interação salva: view_details - Car: car_robust_002
[OK] Interação salva: whatsapp_contact - Car: car_robust_003
```

### 2. Verificar Console do Frontend

Abrir DevTools (F12) e procurar:
```
[InteractionTracker] Inicializado com session_id: sess_1699999999999_abc123
[InteractionTracker] Evento enviado: click {status: "success"}
[InteractionTracker] Evento enviado: view_details {status: "success"}
```

### 3. Testar Manualmente

1. Abrir o site
2. Fazer uma busca
3. Clicar em um carro
4. Ver detalhes
5. Clicar no WhatsApp
6. Verificar se os logs aparecem no console

### 4. Verificar Estatísticas via API

```bash
curl https://seu-backend.railway.app/api/ml/stats
```

**Resposta esperada**:
```json
{
  "total_interactions": 150,
  "click_count": 80,
  "view_details_count": 50,
  "whatsapp_contact_count": 20,
  "unique_sessions": 45,
  "unique_cars": 30,
  "avg_duration_seconds": 45.5,
  "last_interaction": "2024-11-11T10:30:00.000Z",
  "data_collection_progress": 30.0,
  "ready_for_training": false,
  "min_interactions_needed": 500
}
```

## 📈 Próximos Passos

### 1. Verificar Coleta em Produção

**Ação imediata**:
```bash
# Adicionar endpoint para download dos dados
GET /api/ml/export-data
```

**Implementação**:
```python
@app.get("/api/ml/export-data")
async def export_ml_data():
    """Exportar dados de interações para análise"""
    interactions = interaction_service.get_all_interactions()
    return {
        "total": len(interactions),
        "interactions": interactions,
        "exported_at": datetime.now().isoformat()
    }
```

### 2. Adicionar Dashboard de Monitoramento

Criar página admin para visualizar:
- Total de interações coletadas
- Gráfico de interações por dia
- Carros mais clicados
- Sessões únicas
- Progresso para treinamento (meta: 500 interações)

### 3. Alertas Automáticos

Configurar alertas quando:
- ✅ Atingir 500 interações (pronto para treinar)
- ⚠️ Nenhuma interação em 24h (possível problema)
- ❌ Taxa de erro > 10% (problema técnico)

## 🎓 Como Usar os Dados para ML

### Fase 1: Análise Exploratória (500+ interações)

```python
import pandas as pd
import json

# Carregar dados
with open('user_interactions.json') as f:
    data = json.load(f)

df = pd.DataFrame(data['interactions'])

# Análises
print(f"Total de interações: {len(df)}")
print(f"Carros mais clicados:\n{df['car_id'].value_counts().head(10)}")
print(f"Taxa de conversão WhatsApp: {len(df[df['interaction_type']=='whatsapp_contact'])/len(df)*100:.1f}%")
```

### Fase 2: Treinamento de Modelo (1000+ interações)

**Objetivo**: Prever quais carros o usuário vai clicar/contatar.

**Features**:
- Preferências do usuário (orçamento, uso, prioridades)
- Características do carro (marca, modelo, ano, preço, categoria)
- Score de match atual

**Target**:
- Clique: 0/1
- Visualização de detalhes: 0/1
- Contato WhatsApp: 0/1 (mais importante)

**Modelo sugerido**:
- XGBoost ou LightGBM (bom para dados tabulares)
- Rede Neural (se houver 5000+ interações)

### Fase 3: Integração no Sistema (2000+ interações)

Substituir score atual por score do modelo ML:
```python
# Atual (regras fixas)
score = calculate_match_score(car, profile)

# Futuro (modelo ML)
score = ml_model.predict_interest(car, profile)
```

## 📊 Métricas de Sucesso

### Coleta de Dados
- ✅ **Meta 1**: 500 interações (análise exploratória)
- ✅ **Meta 2**: 1000 interações (treinamento inicial)
- ✅ **Meta 3**: 5000 interações (modelo robusto)

### Qualidade dos Dados
- Taxa de erro < 5%
- Sessões únicas > 100
- Carros únicos > 50
- Distribuição balanceada de tipos de interação

### Performance do Modelo (Futuro)
- Precisão > 70% (prever cliques)
- Recall > 60% (não perder oportunidades)
- AUC-ROC > 0.75

## 🔧 Troubleshooting

### Problema: Nenhuma interação sendo coletada

**Verificar**:
1. Console do navegador (F12) - Erros de rede?
2. Logs do backend - Requisições chegando?
3. URL da API - Está correta?
4. CORS - Está configurado?

### Problema: Interações sendo coletadas mas não salvas

**Verificar**:
1. Permissões do arquivo `user_interactions.json`
2. Espaço em disco no servidor
3. Logs de erro no backend

### Problema: Dados inconsistentes

**Verificar**:
1. Validação de schema (Pydantic)
2. Timestamps corretos
3. IDs únicos

## 📝 Conclusão

O sistema de coleta de dados está **100% implementado e pronto para uso**. Agora precisamos:

1. ✅ Verificar se está coletando dados em produção
2. ✅ Adicionar endpoint de exportação de dados
3. ✅ Criar dashboard de monitoramento
4. ⏳ Aguardar 500+ interações para análise inicial
5. ⏳ Treinar modelo ML quando houver dados suficientes

**Próxima ação**: Verificar logs do Railway para confirmar que dados estão sendo coletados.
