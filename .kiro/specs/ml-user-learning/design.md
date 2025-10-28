# Design Document - Sistema de ML para Aprendizado com Usuários

## Overview

Este documento descreve o design técnico para implementar um sistema de Machine Learning que aprende com as interações dos usuários e melhora progressivamente as recomendações de veículos no FacilIAuto.

### Objetivos do Design

1. **Coleta Passiva**: Capturar interações dos usuários sem impactar a experiência
2. **Modelo Simples**: Implementar um modelo de ML viável para MVP que possa evoluir
3. **Sistema Híbrido**: Combinar algoritmo de regras atual com ML de forma gradual
4. **Fallback Gracioso**: Garantir que falhas no ML não afetem a experiência do usuário
5. **Escalabilidade**: Preparar infraestrutura para crescimento futuro

### Abordagem Técnica

O sistema será implementado em 3 camadas:

1. **Camada de Coleta** (Frontend): Captura eventos de interação
2. **Camada de Armazenamento** (Backend): Persiste dados para treinamento
3. **Camada de ML** (Backend): Treina modelos e gera predições

### Tecnologias Escolhidas

- **Frontend**: React + TypeScript (já existente)
- **Backend**: FastAPI + Python (já existente)
- **ML Framework**: scikit-learn (simples, estável, adequado para MVP)
- **Armazenamento**: JSON files (MVP) → SQLite (futuro) → PostgreSQL (produção)
- **Modelo**: Random Forest Regressor (interpretável, robusto, bom para dados tabulares)

## Architecture

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  InteractionTracker (novo componente)                  │ │
│  │  - trackCarClick(carId, preferences)                   │ │
│  │  - trackWhatsAppClick(carId, preferences)              │ │
│  │  - trackViewDuration(carId, duration)                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP POST
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  API Endpoints (api/main.py)                           │ │
│  │  POST /api/interactions/track                          │ │
│  │  GET  /api/ml/stats                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  InteractionService (services/interaction_service.py)  │ │
│  │  - save_interaction()                                  │ │
│  │  - get_interactions_for_training()                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Data Storage (data/interactions/)                     │ │
│  │  - user_interactions.json                              │ │
│  │  - interaction_stats.json                              │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MLService (services/ml_service.py)                    │ │
│  │  - train_model()                                       │ │
│  │  - predict_score()                                     │ │
│  │  - load_model()                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  HybridRecommendationEngine (novo)                     │ │
│  │  - combine_scores(rule_score, ml_score)                │ │
│  │  - get_recommendations_with_ml()                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Model Storage (data/ml_models/)                       │ │
│  │  - recommendation_model_v1.pkl                         │ │
│  │  - feature_scaler.pkl                                  │ │
│  │  - model_metadata.json                                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Dados

#### 1. Coleta de Interações (Runtime)
```
Usuário clica em carro → InteractionTracker captura evento → 
Envia para /api/interactions/track → InteractionService salva em JSON →
Dados disponíveis para treinamento futuro
```

#### 2. Treinamento do Modelo (Offline/Periódico)
```
Script de treinamento executado → Carrega user_interactions.json →
Feature engineering → Treina Random Forest → Avalia performance →
Salva modelo em .pkl → Atualiza metadata
```

#### 3. Recomendação Híbrida (Runtime)
```
Usuário faz busca → UnifiedRecommendationEngine calcula score de regras →
MLService calcula score ML (se modelo disponível) →
HybridEngine combina scores (70% regras + 30% ML) →
Retorna carros ordenados por score híbrido
```

## Components and Interfaces

### 1. Frontend: InteractionTracker

**Localização**: `platform/frontend/src/services/InteractionTracker.ts`

**Responsabilidades**:
- Capturar eventos de interação do usuário
- Enviar dados para backend de forma assíncrona
- Gerenciar session_id no localStorage
- Não bloquear UI em caso de falhas

**Interface**:
```typescript
interface InteractionEvent {
  session_id: string;
  car_id: string;
  interaction_type: 'click' | 'view_details' | 'whatsapp_contact';
  timestamp: string;
  user_preferences: {
    budget: number;
    usage: string;
    priorities: string[];
  };
  duration_seconds?: number;
}

class InteractionTracker {
  private sessionId: string;
  
  constructor();
  trackCarClick(carId: string, preferences: UserPreferences): Promise<void>;
  trackWhatsAppClick(carId: string, preferences: UserPreferences): Promise<void>;
  trackViewDuration(carId: string, duration: number, preferences: UserPreferences): Promise<void>;
  private sendEvent(event: InteractionEvent): Promise<void>;
  private getOrCreateSessionId(): string;
}
```

**Integração**:
- Importar em `CarCard.tsx` para capturar cliques
- Importar em `CarDetailsModal.tsx` para capturar visualizações e WhatsApp
- Usar hook `useEffect` para medir tempo de visualização

### 2. Backend: InteractionService

**Localização**: `platform/backend/services/interaction_service.py`

**Responsabilidades**:
- Receber e validar eventos de interação
- Persistir dados em formato estruturado
- Fornecer dados para treinamento
- Calcular estatísticas básicas

**Interface**:
```python
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class InteractionEvent(BaseModel):
    session_id: str
    car_id: str
    interaction_type: str  # 'click', 'view_details', 'whatsapp_contact'
    timestamp: datetime
    user_preferences: Dict
    duration_seconds: Optional[int] = None

class InteractionService:
    def __init__(self, data_dir: str = "data/interactions"):
        self.data_dir = data_dir
        self.interactions_file = f"{data_dir}/user_interactions.json"
    
    def save_interaction(self, event: InteractionEvent) -> bool:
        """Salva interação no arquivo JSON"""
        pass
    
    def get_all_interactions(self) -> List[Dict]:
        """Retorna todas as interações para treinamento"""
        pass
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas básicas"""
        pass
    
    def get_interactions_count(self) -> int:
        """Retorna total de interações coletadas"""
        pass
```

### 3. Backend: MLService

**Localização**: `platform/backend/services/ml_service.py`

**Responsabilidades**:
- Feature engineering (transformar dados brutos em features)
- Treinar modelo Random Forest
- Fazer predições de score
- Gerenciar versionamento de modelos
- Avaliar performance

**Interface**:
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Dict, List, Optional, Tuple

class MLService:
    def __init__(self, model_dir: str = "data/ml_models"):
        self.model_dir = model_dir
        self.model: Optional[RandomForestRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = []
        self.is_trained = False
    
    def prepare_features(self, interactions: List[Dict], cars: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Feature engineering: transforma dados brutos em features numéricas
        
        Features do usuário:
        - budget_normalized (0-1)
        - usage_encoded (0=urbano, 1=misto, 2=estrada)
        - priority_economia (0/1)
        - priority_conforto (0/1)
        - priority_desempenho (0/1)
        
        Features do carro:
        - price_normalized (0-1)
        - year_normalized (0-1)
        - mileage_normalized (0-1)
        - fuel_type_encoded (0=flex, 1=gasolina, 2=diesel, 3=eletrico)
        - transmission_encoded (0=manual, 1=automatico)
        
        Target:
        - interaction_score (1=click, 2=view_details, 3=whatsapp_contact)
        """
        pass
    
    def train_model(self, min_interactions: int = 500) -> Dict:
        """
        Treina modelo Random Forest com dados disponíveis
        Retorna métricas de performance
        """
        pass
    
    def predict_score(self, user_preferences: Dict, car: Dict) -> float:
        """
        Prediz score ML para um par (usuário, carro)
        Retorna 0.0 se modelo não estiver treinado
        """
        pass
    
    def load_model(self) -> bool:
        """Carrega modelo treinado do disco"""
        pass
    
    def save_model(self, metadata: Dict) -> bool:
        """Salva modelo e metadata no disco"""
        pass
    
    def evaluate_model(self, X_test, y_test) -> Dict:
        """Avalia performance do modelo"""
        pass
```

### 4. Backend: HybridRecommendationEngine

**Localização**: `platform/backend/services/hybrid_recommendation_engine.py`

**Responsabilidades**:
- Combinar scores de regras e ML
- Gerenciar fallback quando ML não disponível
- Logar uso de ML vs regras
- Reordenar resultados baseado em score híbrido

**Interface**:
```python
from services.unified_recommendation_engine import UnifiedRecommendationEngine
from services.ml_service import MLService
from models.user_profile import UserProfile
from models.car import Car
from typing import List, Dict

class HybridRecommendationEngine:
    def __init__(self, data_dir: str = "data"):
        self.rule_engine = UnifiedRecommendationEngine(data_dir=data_dir)
        self.ml_service = MLService()
        self.ml_weight = 0.3  # 30% ML, 70% regras para MVP
        self.rule_weight = 0.7
        
        # Tentar carregar modelo ML
        self.ml_available = self.ml_service.load_model()
    
    def get_recommendations(
        self, 
        user_profile: UserProfile, 
        top_n: int = 10
    ) -> List[Car]:
        """
        Retorna recomendações usando sistema híbrido
        """
        # 1. Obter recomendações do engine de regras
        rule_recommendations = self.rule_engine.recommend(user_profile, top_n=50)
        
        # 2. Se ML disponível, calcular scores ML
        if self.ml_available:
            for car in rule_recommendations:
                ml_score = self.ml_service.predict_score(
                    user_preferences=user_profile.dict(),
                    car=car.dict()
                )
                
                # Combinar scores
                hybrid_score = (
                    self.rule_weight * car.score +
                    self.ml_weight * ml_score
                )
                car.score = hybrid_score
                car.ml_score = ml_score  # Para debug
            
            # Reordenar por score híbrido
            rule_recommendations.sort(key=lambda x: x.score, reverse=True)
        
        # 3. Retornar top N
        return rule_recommendations[:top_n]
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do sistema híbrido"""
        return {
            "ml_available": self.ml_available,
            "ml_weight": self.ml_weight,
            "rule_weight": self.rule_weight,
            "model_version": self.ml_service.model_version if self.ml_available else None
        }
```

### 5. API Endpoints

**Localização**: `platform/backend/api/main.py`

**Novos Endpoints**:

```python
@app.post("/api/interactions/track")
async def track_interaction(event: InteractionEvent):
    """
    Registra interação do usuário
    """
    try:
        interaction_service.save_interaction(event)
        return {"status": "success"}
    except Exception as e:
        # Não falhar - apenas logar
        print(f"[ERRO] Falha ao salvar interação: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/ml/stats")
async def get_ml_stats():
    """
    Retorna estatísticas do sistema ML
    """
    return {
        "total_interactions": interaction_service.get_interactions_count(),
        "ml_available": hybrid_engine.ml_available,
        "ml_weight": hybrid_engine.ml_weight,
        "model_metadata": ml_service.get_metadata()
    }

@app.post("/api/recommendations/hybrid")
async def get_hybrid_recommendations(user_profile: UserProfile):
    """
    Retorna recomendações usando sistema híbrido (regras + ML)
    """
    recommendations = hybrid_engine.get_recommendations(user_profile)
    return recommendations
```

## Data Models

### 1. Interaction Event (Storage Format)

**Arquivo**: `data/interactions/user_interactions.json`

```json
{
  "interactions": [
    {
      "id": "int_001",
      "session_id": "sess_abc123",
      "car_id": "car_robust_001",
      "interaction_type": "whatsapp_contact",
      "timestamp": "2024-10-14T15:30:00Z",
      "user_preferences": {
        "budget": 120000,
        "usage": "urbano",
        "priorities": ["economia", "conforto"]
      },
      "duration_seconds": 45,
      "car_snapshot": {
        "marca": "Toyota",
        "modelo": "Corolla",
        "ano": 2022,
        "preco": 115990,
        "categoria": "Sedan",
        "combustivel": "Flex",
        "cambio": "Automático"
      }
    }
  ]
}
```

### 2. Model Metadata

**Arquivo**: `data/ml_models/model_metadata.json`

```json
{
  "version": "v1",
  "trained_at": "2024-10-14T20:00:00Z",
  "training_samples": 1250,
  "features": [
    "budget_normalized",
    "usage_encoded",
    "priority_economia",
    "priority_conforto",
    "priority_desempenho",
    "price_normalized",
    "year_normalized",
    "mileage_normalized",
    "fuel_type_encoded",
    "transmission_encoded"
  ],
  "metrics": {
    "rmse": 0.45,
    "mae": 0.32,
    "r2_score": 0.68
  },
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10,
    "min_samples_split": 5
  }
}
```

### 3. Feature Matrix (Training)

**Formato interno** (numpy array):

```
Features (X):
[
  [budget_norm, usage_enc, prio_econ, prio_conf, prio_desemp, price_norm, year_norm, mile_norm, fuel_enc, trans_enc],
  [0.6, 0, 1, 1, 0, 0.58, 0.8, 0.4, 0, 1],
  ...
]

Target (y):
[3, 1, 2, 3, 1, ...]  # 1=click, 2=view_details, 3=whatsapp_contact
```

## Error Handling

### Estratégias de Fallback

1. **ML Service Indisponível**:
   - Sistema usa apenas algoritmo de regras
   - Usuário não percebe diferença
   - Log de erro para monitoramento

2. **Falha ao Salvar Interação**:
   - Erro é logado mas não interrompe fluxo
   - Retorna status de erro mas não bloqueia UI
   - Retry pode ser implementado no frontend

3. **Modelo com Performance Ruim**:
   - Não substitui modelo anterior
   - Alerta é gerado para revisão manual
   - Sistema continua com modelo anterior ou regras

4. **Dados Insuficientes para Treinamento**:
   - Sistema continua coletando dados
   - Não tenta treinar modelo
   - Endpoint `/api/ml/stats` indica status

### Validações

1. **Validação de Entrada** (API):
   - Pydantic valida estrutura de InteractionEvent
   - Campos obrigatórios: session_id, car_id, interaction_type
   - Timestamp deve ser válido

2. **Validação de Features** (ML):
   - Features numéricas devem estar no range [0, 1]
   - Features categóricas devem ter valores conhecidos
   - Dados faltantes são tratados com valores padrão

3. **Validação de Modelo** (Training):
   - Mínimo de 500 interações para treinar
   - Métricas devem atingir threshold mínimo (R² > 0.5)
   - Modelo deve ser serializável

## Testing Strategy

### 1. Unit Tests

**Frontend** (`InteractionTracker.test.ts`):
- ✓ Cria session_id único no primeiro uso
- ✓ Reutiliza session_id em chamadas subsequentes
- ✓ Envia eventos com estrutura correta
- ✓ Não bloqueia UI em caso de falha de rede

**Backend** (`test_interaction_service.py`):
- ✓ Salva interação corretamente
- ✓ Retorna todas as interações
- ✓ Calcula estatísticas corretamente
- ✓ Lida com arquivo inexistente

**Backend** (`test_ml_service.py`):
- ✓ Feature engineering gera matriz correta
- ✓ Treina modelo com dados suficientes
- ✓ Não treina com dados insuficientes
- ✓ Predição retorna score válido [0, 1]
- ✓ Salva e carrega modelo corretamente

**Backend** (`test_hybrid_engine.py`):
- ✓ Combina scores corretamente
- ✓ Fallback para regras quando ML indisponível
- ✓ Reordena resultados por score híbrido

### 2. Integration Tests

**API** (`test_api_ml_integration.py`):
- ✓ POST /api/interactions/track salva dados
- ✓ GET /api/ml/stats retorna estatísticas corretas
- ✓ POST /api/recommendations/hybrid retorna resultados

**End-to-End** (`test_ml_pipeline.py`):
- ✓ Coleta → Armazenamento → Treinamento → Predição
- ✓ Sistema híbrido funciona com e sem ML

### 3. Performance Tests

- ✓ Predição ML não adiciona mais de 50ms de latência
- ✓ Salvar interação não bloqueia request
- ✓ Treinamento completa em menos de 5 minutos com 10k interações

### 4. Manual Testing Checklist

- [ ] Clicar em card de carro registra evento
- [ ] Clicar em WhatsApp registra evento de alto interesse
- [ ] Session ID persiste entre reloads
- [ ] Sistema funciona sem modelo ML
- [ ] Após treinar modelo, scores mudam
- [ ] Fallback funciona se modelo for deletado

## Implementation Notes

### Fase 1: Coleta de Dados (Semana 1)
- Implementar InteractionTracker no frontend
- Implementar InteractionService no backend
- Adicionar endpoints de API
- Testar coleta de dados

### Fase 2: Feature Engineering e Treinamento (Semana 2)
- Implementar MLService
- Criar script de treinamento
- Testar com dados sintéticos
- Documentar processo de treinamento

### Fase 3: Sistema Híbrido (Semana 3)
- Implementar HybridRecommendationEngine
- Integrar com API existente
- Testar combinação de scores
- Ajustar pesos (70/30)

### Fase 4: Monitoramento e Refinamento (Semana 4)
- Adicionar logs e métricas
- Criar dashboard de estatísticas
- Documentar processo de retreinamento
- Preparar para produção

### Considerações de Produção

1. **Armazenamento**: Migrar de JSON para SQLite/PostgreSQL
2. **Retreinamento**: Automatizar com cron job semanal
3. **Monitoramento**: Adicionar alertas para falhas de ML
4. **A/B Testing**: Testar diferentes pesos (regras vs ML)
5. **Feature Store**: Considerar feature store para features reutilizáveis
