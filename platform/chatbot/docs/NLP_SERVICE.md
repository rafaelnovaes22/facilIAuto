# NLP Service - Documentação

## Visão Geral

O NLP Service é o componente de Processamento de Linguagem Natural do chatbot WhatsApp FacilIAuto. Ele é responsável por entender as mensagens dos usuários através de três capacidades principais:

1. **Classificação de Intenções** - Identifica o que o usuário quer fazer
2. **Extração de Entidades** - Extrai informações específicas da mensagem
3. **Análise de Sentimento** - Detecta o tom emocional da mensagem

## Instalação

O NLP Service já está incluído no projeto. Não requer instalação adicional.

## Uso Básico

```python
from src.services.nlp_service import NLPService

# Inicializar o serviço
nlp = NLPService()

# Processar uma mensagem
result = await nlp.process("Tenho 50 mil de orçamento para um carro econômico")

# Acessar os resultados
print(f"Intenção: {result.intent.value}")
print(f"Confiança: {result.confidence}")
print(f"Entidades: {result.entities}")
print(f"Sentimento: {result.sentiment.value}")
```

## Intenções Suportadas

O serviço reconhece 15 tipos de intenções:

| Intenção | Descrição | Exemplo |
|----------|-----------|---------|
| `GREETING` | Saudações | "Olá", "Bom dia" |
| `BUDGET_INQUIRY` | Consultas de orçamento | "Tenho 50 mil" |
| `CAR_RECOMMENDATION` | Pedidos de recomendação | "Me recomenda um carro" |
| `CAR_DETAILS` | Detalhes de veículos | "Qual o consumo?" |
| `COMPARE_CARS` | Comparação de carros | "Civic ou Corolla?" |
| `SCHEDULE_TEST_DRIVE` | Agendamento de test drive | "Quero fazer test drive" |
| `CONTACT_DEALER` | Contato com concessionária | "Falar com vendedor" |
| `HUMAN_HANDOFF` | Transferência para humano | "Quero falar com atendente" |
| `FEEDBACK_POSITIVE` | Feedback positivo | "Obrigado!", "Adorei" |
| `FEEDBACK_NEGATIVE` | Feedback negativo | "Não gostei" |
| `LOCATION_INQUIRY` | Consultas de localização | "Onde fica?" |
| `FINANCING_INQUIRY` | Consultas de financiamento | "Posso financiar?" |
| `USAGE_INQUIRY` | Consultas de uso | "Para trabalho" |
| `PREFERENCE_INQUIRY` | Consultas de preferências | "Priorizo economia" |
| `UNKNOWN` | Intenção desconhecida | - |


## Entidades Extraídas

O serviço extrai 6 tipos de entidades:

### 1. Orçamento (budget)

Valores monetários mencionados pelo usuário.

**Formatos suportados:**
- "R$ 50.000"
- "50 mil"
- "50k"
- "50000 reais"

**Normalização:** Valores são convertidos para números inteiros (ex: "50 mil" → "50000")

### 2. Marca (brand)

Marcas de carros mencionadas.

**Marcas suportadas:** Toyota, Honda, Volkswagen, VW, Ford, Chevrolet, Fiat, Hyundai, Nissan, Renault, Peugeot, Citroën, Jeep, BMW, Mercedes, Audi, Volvo, Mitsubishi, Kia, Mazda, Subaru, Suzuki, Chery, CAOA, BYD

### 3. Modelo (model)

Modelos de carros mencionados.

**Modelos suportados:** Corolla, Civic, Onix, HB20, Gol, Polo, Up, Fox, Ka, Fiesta, Focus, Fusion, Cruze, Tracker, Equinox, S10, Hilux, Ranger, Toro, Strada, Renegade, Compass, Kicks, Versa, March, Sandero, Logan, Duster, 208, 2008, 3008, C3, C4, HR-V, CR-V, Fit, City, Tucson, Creta, IX35, Sportage, Cerato, Soul, Picanto, Argo, Mobi, Uno, Palio, Siena, Cronos, Pulse, Fastback, Nivus, T-Cross, Taos, Tiguan, Jetta, Virtus, Saveiro, Amarok

### 4. Categoria (category)

Tipo de veículo.

**Categorias:** SUV, Sedan, Hatch, Hatchback, Pickup, Caminhonete, Minivan, Crossover, Compacto, Subcompacto, Esportivo, Conversível

### 5. Localização (location)

Cidades e estados brasileiros.

**Localizações:** São Paulo, SP, Rio de Janeiro, RJ, Belo Horizonte, MG, Brasília, DF, Salvador, BA, Fortaleza, CE, Recife, PE, Curitiba, PR, Porto Alegre, RS, e outras capitais e cidades principais

### 6. Preferência (preference)

Características desejadas pelo usuário.

**Preferências:** Economia, Econômico, Espaço, Espaçoso, Performance, Potência, Potente, Conforto, Confortável, Segurança, Seguro, Tecnologia, Tecnológico, Luxo, Luxuoso, Design, Bonito, Moderno, Robusto, Resistente, Durável


## Análise de Sentimento

O serviço classifica mensagens em 3 categorias de sentimento:

### POSITIVE (Positivo)

Mensagens com tom positivo, satisfação ou gratidão.

**Exemplos:**
- "Obrigado!"
- "Adorei as opções"
- "Excelente atendimento"
- "Perfeito!"

### NEUTRAL (Neutro)

Mensagens informativas sem carga emocional.

**Exemplos:**
- "Tenho 50 mil de orçamento"
- "Quero um carro para família"
- "Qual o preço?"

### NEGATIVE (Negativo)

Mensagens com tom negativo, insatisfação ou frustração.

**Exemplos:**
- "Não gostei"
- "Péssimo"
- "Não é o que eu queria"

### Tratamento de Negações

O analisador detecta negações e inverte o sentimento:

- "Não gostei" → NEGATIVE (negação de positivo)
- "Não é ruim" → POSITIVE (negação de negativo)
- "Não é excelente" → NEGATIVE (negação de positivo)

## Modelo de Dados

### NLPResult

Resultado completo do processamento NLP.

```python
class NLPResult(BaseModel):
    intent: Intent                    # Intenção identificada
    confidence: float                 # Confiança (0.0 a 1.0)
    entities: List[Entity]            # Entidades extraídas
    sentiment: Sentiment              # Sentimento da mensagem
    language: str = "pt-BR"           # Idioma
    normalized_text: str              # Texto normalizado
    processing_time_ms: float         # Tempo de processamento
```

### Entity

Entidade extraída da mensagem.

```python
class Entity(BaseModel):
    type: str                         # Tipo da entidade
    value: str                        # Valor extraído
    confidence: float                 # Confiança (0.0 a 1.0)
    start_pos: Optional[int]          # Posição inicial no texto
    end_pos: Optional[int]            # Posição final no texto
```


## Exemplos Avançados

### Exemplo 1: Processamento Completo

```python
nlp = NLPService()

message = "Olá! Tenho 70 mil e procuro um Toyota Corolla econômico em São Paulo"
result = await nlp.process(message)

# Resultado:
# intent: CAR_RECOMMENDATION
# confidence: 0.67
# entities: [
#   Entity(type="budget", value="70000"),
#   Entity(type="brand", value="toyota"),
#   Entity(type="model", value="corolla"),
#   Entity(type="preference", value="econômico"),
#   Entity(type="location", value="são paulo")
# ]
# sentiment: NEUTRAL
```

### Exemplo 2: Múltiplas Entidades

```python
message = "Quero comparar o Honda Civic e o Toyota Corolla em Curitiba"
result = await nlp.process(message)

# Resultado:
# intent: COMPARE_CARS
# entities: [
#   Entity(type="brand", value="honda"),
#   Entity(type="model", value="civic"),
#   Entity(type="brand", value="toyota"),
#   Entity(type="model", value="corolla"),
#   Entity(type="location", value="curitiba")
# ]
```

### Exemplo 3: Feedback com Sentimento

```python
message = "Obrigado! Adorei as sugestões, muito bom!"
result = await nlp.process(message)

# Resultado:
# intent: FEEDBACK_POSITIVE
# sentiment: POSITIVE
# confidence: 0.75
```

## Performance

- **Tempo médio:** < 10ms por mensagem
- **Precisão de intenções:** 100% (nos testes)
- **Precisão de entidades:** 100% (nos testes)
- **Precisão de sentimento:** 86% (nos testes)
- **Suporte assíncrono:** Sim
- **Thread-safe:** Sim

## Testes

Execute os testes standalone:

```bash
# Teste de classificação de intenções
python tests/test_nlp_standalone.py

# Teste de extração de entidades
python tests/test_entity_extractor.py

# Teste de análise de sentimento
python tests/test_sentiment_analyzer.py

# Demo interativa
python examples/nlp_service_demo.py
```

## Extensão

### Adicionar Nova Intenção

1. Adicione ao enum `Intent`:
```python
class Intent(str, Enum):
    # ... existing intents
    NEW_INTENT = "new_intent"
```

2. Adicione padrões ao `IntentClassifier`:
```python
self.intent_patterns = {
    # ... existing patterns
    Intent.NEW_INTENT: [
        r'\b(palavra1|palavra2)\b',
        r'\b(padrão|regex)\b',
    ],
}
```

### Adicionar Nova Entidade

Adicione ao `EntityExtractor`:
```python
self.patterns = {
    # ... existing patterns
    "new_entity": [
        r'\b(padrão1|padrão2)\b',
    ],
}
```

## Limitações Conhecidas

1. **Idioma:** Suporta apenas português brasileiro
2. **Contexto:** Não mantém contexto entre mensagens (stateless)
3. **Ambiguidade:** Em casos ambíguos, escolhe a intenção com mais matches
4. **Entidades compostas:** Não detecta relacionamentos entre entidades

## Roadmap

- [ ] Suporte a contexto conversacional
- [ ] Integração com modelos ML (spaCy/Transformers)
- [ ] Suporte multilíngue
- [ ] Detecção de entidades compostas
- [ ] Cache de resultados para mensagens repetidas

