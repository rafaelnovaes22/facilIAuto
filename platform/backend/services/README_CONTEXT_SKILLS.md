# 🎯 Context-Based Recommendation Skills

## 📋 Visão Geral

Este conjunto de **Agent Skills** implementa busca contextual inteligente que utiliza a base de conhecimento dos perfis de uso para recomendar carros baseado na intenção do usuário.

## 🧩 Componentes

### 1. Context-Based Recommendation Skill (`context_based_recommendation_skill.py`)

**Funcionalidade Principal:**
- Analisa queries de busca do usuário
- Detecta intenção de uso (Uber, trabalho, família, etc.)
- Aplica conhecimento da base de perfis de uso
- Gera recomendações contextualizadas com boost de score

**Skills Implementadas:**
- `analyze_search_context()` - Análise de contexto da busca
- `recommend_by_context()` - Recomendações baseadas em contexto
- `_apply_entity_filters()` - Filtros por entidades extraídas
- `_calculate_context_boost()` - Boost contextual baseado no perfil

### 2. Search Intent Classifier (`search_intent_classifier.py`)

**Funcionalidade Principal:**
- Classificação avançada de intenção usando NLP
- Extração de entidades (marcas, modelos, preços, anos)
- Inferência de persona do usuário
- Cálculo de fatores de prioridade

**Skills Implementadas:**
- `classify_intent()` - Classificação principal de intenção
- `_extract_all_entities()` - Extração de entidades
- `_infer_user_persona()` - Inferência de persona
- `_calculate_priority_factors()` - Fatores de prioridade

## 🔌 Integração com API

### Novos Endpoints

#### `/search/contextual`
```http
GET /search/contextual?query=carros para fazer uber&max_results=10
```

**Resposta:**
```json
{
  "query": "carros para fazer uber",
  "context_analysis": {
    "detected_intent": "transporte_passageiros",
    "confidence": 0.95,
    "profile_match": "transporte_passageiros",
    "extracted_entities": {"marcas": [], "categorias": []}
  },
  "total_results": 10,
  "recommendations": [...]
}
```

#### `/search/intent-analysis`
```http
GET /search/intent-analysis?query=SUV para família com crianças
```

**Resposta:**
```json
{
  "query": "SUV para família com crianças",
  "analysis": {
    "primary_intent": {
      "category": "familia", 
      "confidence": 0.87
    },
    "entities": [
      {"type": "categories", "value": "suv"},
      {"type": "family_context", "value": "crianças"}
    ],
    "user_persona": "family_oriented",
    "priority_factors": {
      "seguranca": 0.9,
      "espaco": 0.8
    }
  }
}
```

## 🎯 Casos de Uso Suportados

### 1. **Transporte de Passageiros (Uber/99)**
- **Query:** "carros para fazer uber"
- **Intenção:** `transporte_passageiros`
- **Perfil:** Economia, durabilidade, revenda
- **Veículos:** Sedan compacto, Hatch premium

### 2. **Trabalho Diário**
- **Query:** "carro para trabalho"
- **Intenção:** `trabalho_diario`
- **Perfil:** Economia, confiabilidade, baixa manutenção
- **Veículos:** Sedan compacto, Hatch econômico

### 3. **Uso Familiar**
- **Query:** "SUV para família com crianças"
- **Intenção:** `familia`
- **Perfil:** Segurança, espaço, conforto
- **Veículos:** SUV, SUV Compacto, Minivan

### 4. **Uso Comercial**
- **Query:** "pickup para entregas"
- **Intenção:** `comercial`
- **Perfil:** Capacidade de carga, durabilidade
- **Veículos:** Pickup pequena, Furgão

### 5. **Primeiro Carro**
- **Query:** "primeiro carro econômico"
- **Intenção:** `primeiro_carro`
- **Perfil:** Segurança, facilidade, economia
- **Veículos:** Hatch básico, Sedan compacto

### 6. **Lazer/Aventura**
- **Query:** "carro para viagens"
- **Intenção:** `lazer`
- **Perfil:** Performance, conforto, tecnologia
- **Veículos:** SUV, Crossover, Pickup

## 🔍 Detecção de Intenção

### Padrões de Busca
```python
# Uber/Transporte
r'\buber\b', r'\b99\b', r'\btransporte\s+passageiros\b'

# Trabalho
r'\btrabalho\b', r'\bdiario\b', r'\beconomico\b'

# Família
r'\bfamilia\b', r'\bcriancas\b', r'\bisofix\b'

# Comercial
r'\bcomercial\b', r'\bentrega\b', r'\bcarga\b'
```

### Extração de Entidades
- **Marcas:** Toyota, Honda, Ford, etc.
- **Modelos:** Corolla, Civic, Focus, etc.
- **Anos:** 2018, 2019, 2020, etc.
- **Preços:** R$ 50.000, até 80 mil, etc.
- **Categorias:** SUV, Sedan, Hatch, etc.

## 🎭 Agent Orchestrator Integration

### Workflow Registrado
```python
contextual_search = WorkflowDefinition(
    workflow_id='contextual_vehicle_search',
    name='Busca Contextual de Veículos',
    phases=[
        'intent_analysis',
        'recommendation_generation', 
        'result_validation'
    ]
)
```

### Capacidades da Skill
- **contextual_search:** Busca contextual completa
- **intent_classification:** Classificação de intenção
- **SLA:** 30s para busca, 10s para classificação

## 🚀 Exemplo de Uso

```python
from services.context_based_recommendation_skill import create_context_skill
from services.search_intent_classifier import create_intent_classifier

# Criar skills
context_skill = create_context_skill()
intent_classifier = create_intent_classifier()

# Análise de intenção
query = "carros para fazer uber"
analysis = intent_classifier.classify_intent(query)

print(f"Intent: {analysis.primary_intent.value}")
print(f"Confidence: {analysis.confidence}")

# Recomendações contextuais
recommendations = context_skill.recommend_by_context(query, max_results=5)

for rec in recommendations:
    print(f"{rec.car.marca} {rec.car.modelo} - Score: {rec.final_score}")
    print(f"Motivos: {rec.reasoning}")
```

## 📊 Métricas de Performance

### Scores Contextuais
- **Base Score:** Score básico do veículo (0.0-1.0)
- **Context Boost:** Boost baseado no perfil (-0.5 a +0.5)  
- **Final Score:** Score final = base × (1 + boost)

### Alinhamento com Perfil
- **Categoria:** Match com categorias ideais
- **Requisitos:** Atendimento aos requisitos essenciais
- **Top Modelos:** Similaridade com modelos recomendados

## 🔧 Configuração

### Dependências
```python
# Instalar dependências necessárias
pip install difflib  # Para similaridade de strings
```

### Integração na API
```python
# Em api/main.py
from services.context_based_recommendation_skill import create_context_skill
from services.search_intent_classifier import create_intent_classifier

# Inicialização
context_skill = create_context_skill(data_dir=data_dir)
intent_classifier = create_intent_classifier()
```

## 🎯 Roadmap de Melhorias

### Fase 1 ✅ - Implementação Base
- [x] Context-Based Recommendation Skill
- [x] Search Intent Classifier  
- [x] Integração com API
- [x] Orquestrador de Agentes

### Fase 2 🔄 - Aprimoramentos
- [ ] Machine Learning para detecção de intenção
- [ ] Cache de resultados contextuais
- [ ] A/B Testing de algoritmos
- [ ] Analytics de performance

### Fase 3 📋 - Inteligência Avançada
- [ ] Personalização baseada no histórico
- [ ] Recomendações multi-modal
- [ ] Context learning automático
- [ ] Feedback loop inteligente

---

**🎯 Implementado por:** Agent Skills Framework  
**📅 Data:** Dezembro 2024  
**🔗 Integração:** FacilIAuto Platform Backend