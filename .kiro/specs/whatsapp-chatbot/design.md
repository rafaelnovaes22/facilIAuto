# Design Document - Chatbot WhatsApp FacilIAuto

## Overview

O chatbot WhatsApp do FacilIAuto é uma solução conversacional inteligente que integra-se perfeitamente com o ecossistema existente da plataforma, aproveitando o UnifiedRecommendationEngine, os 12 agentes especializados e a metodologia XP com testes E2E. A arquitetura é baseada em microserviços, utilizando tecnologias modernas como PydanticAI, LangGraph, Redis, DuckDB, Guardrails e Celery para garantir conversas naturais, escaláveis e sem duplicações.

### Objetivos Principais

1. **Qualificação Automatizada**: Qualificar 100% dos leads antes de encaminhar para concessionárias
2. **Conversação Natural**: Processar linguagem natural em português com 85%+ de precisão
3. **Recomendações Consistentes**: Usar o mesmo engine de recomendação da plataforma web
4. **Performance**: Responder em <3s com suporte a 1000 mensagens/minuto
5. **Escalabilidade**: Arquitetura cloud-native que escala horizontalmente
6. **Observabilidade**: Métricas em tempo real integradas com Prometheus/Grafana
7. **Segurança**: Compliance com LGPD e criptografia end-to-end

### Princípios de Design (XP-Aligned)

- **Simple Design**: Arquitetura mais simples que funciona, evitando over-engineering
- **Test-Driven**: Desenvolvimento guiado por testes (TDD) com cobertura >= 80%
- **Evolutionary Architecture**: Design emergente que evolui com feedback
- **Continuous Integration**: Deploy automatizado com zero downtime
- **Customer Collaboration**: Validação constante com stakeholders

---

## Architecture

### High-Level Architecture


```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTE                                  │
│                      (WhatsApp App)                              │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS/TLS 1.3
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   WhatsApp Business API                          │
│                    (Meta Cloud API)                              │
└────────────────────────┬────────────────────────────────────────┘
                         │ Webhook
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway (Kong)                            │
│         Rate Limiting | Auth | Logging | Monitoring             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CHATBOT SERVICE (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Webhook Handler → Message Router → Response Builder    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         │                                        │
│         ┌───────────────┼───────────────┐                        │
│         ▼               ▼               ▼                        │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐                │
│  │   NLP    │   │ Session  │   │ Conversation │                │
│  │ Service  │   │ Manager  │   │   Engine     │                │
│  │(LangGraph│   │(PydanticAI│   │  (LangGraph) │                │
│  └──────────┘   └──────────┘   └──────────────┘                │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    Redis     │  │   DuckDB     │  │  PostgreSQL  │
│  (Session    │  │  (Context    │  │  (Persistent │
│   Cache &    │  │  Structured  │  │    Data)     │
│   Locks)     │  │   Queries)   │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────┐
│              CELERY WORKERS (Async Tasks)                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │  Memory    │  │ Embeddings │  │  Metrics   │             │
│  │  Summarize │  │  Indexing  │  │ Collection │             │
│  └────────────┘  └────────────┘  └────────────┘             │
└──────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────┐
│           EXISTING FACILIAUTO BACKEND (FastAPI)               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  UnifiedRecommendationEngine                           │  │
│  │  /api/recommend → Gera recomendações personalizadas   │  │
│  │  /api/cars → Catálogo de 89 carros RobustCar          │  │
│  │  /api/feedback → Sistema de feedback e refinamento    │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────┐
│              MONITORING & OBSERVABILITY                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Prometheus  │  │   Grafana    │  │     ELK      │       │
│  │  (Metrics)   │  │ (Dashboards) │  │   (Logs)     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**1. WhatsApp Business API (Meta Cloud API)**
- Recebe e envia mensagens via WhatsApp
- Gerencia webhooks para eventos de mensagens
- Suporta texto, áudio, imagem, documento, localização
- Rate limiting: 1000 mensagens/segundo (tier business)

**2. API Gateway (Kong)**
- Rate limiting: 100 req/min por número de telefone
- Autenticação via API keys e JWT
- Logging centralizado de todas as requisições
- Circuit breaker para proteção de backend
- CORS e security headers

**3. Chatbot Service (FastAPI)**
- Webhook handler para receber mensagens do WhatsApp
- Message router para direcionar para handlers específicos
- Response builder para formatar respostas
- Integração com NLP, Session Manager e Conversation Engine

**4. NLP Service (LangGraph)**
- Processamento de linguagem natural em português
- Identificação de intenções (intent classification)
- Extração de entidades (NER - Named Entity Recognition)
- Análise de sentimento
- Precisão alvo: >= 85%

**5. Session Manager (PydanticAI)**
- Gerenciamento de sessões com memória tipada
- Contexto conversacional estruturado
- TTL de 24 horas para sessões ativas
- Locks distribuídos via Redis (SET NX)
- Idempotência por session_id:turn_id


**6. Conversation Engine (LangGraph)**
- Grafo de estados conversacionais
- Checkpoints para recuperação de contexto
- Fluxos de qualificação de leads
- Handoff para atendimento humano
- Guardrails para evitar respostas duplicadas

**7. Redis**
- Cache de sessões ativas (TTL 24h)
- Locks distribuídos para writes concorrentes
- Cache de respostas frequentes (TTL 1h)
- Rate limiting counters
- Pub/Sub para comunicação entre workers

**8. DuckDB**
- Armazenamento de contexto estruturado
- Consultas analíticas baratas
- Histórico de conversas para análise
- Evita reprocessamento de documentos
- Queries SQL para insights

**9. PostgreSQL**
- Dados persistentes (usuários, leads, conversas)
- Histórico completo de interações
- Métricas agregadas
- Auditoria e compliance (LGPD)
- Backup e disaster recovery

**10. Celery Workers**
- Tarefas assíncronas fora do request principal
- Write-behind de memória (resumo, embeddings)
- Idempotência por chave de turno
- Rate limit e retry com backoff
- Debounce de eventos rápidos

**11. Existing FacilIAuto Backend**
- UnifiedRecommendationEngine para recomendações
- Catálogo de 89 carros RobustCar
- Sistema de feedback e refinamento
- Métricas e analytics
- Integração via API REST

**12. Monitoring Stack**
- Prometheus: Coleta de métricas (latência, throughput, erros)
- Grafana: Dashboards em tempo real
- ELK Stack: Logs centralizados e pesquisáveis
- Alerting: PagerDuty/Slack para incidentes

---

## Components and Interfaces

### 1. Webhook Handler

**Responsabilidade**: Receber e validar mensagens do WhatsApp

**Interface**:
```python
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, List

class WhatsAppMessage(BaseModel):
    """Mensagem recebida do WhatsApp"""
    message_id: str
    from_number: str
    timestamp: int
    type: str  # text, audio, image, document, location
    text: Optional[str] = None
    media_url: Optional[str] = None
    media_mime_type: Optional[str] = None
    location: Optional[dict] = None

class WhatsAppWebhook(BaseModel):
    """Payload do webhook do WhatsApp"""
    object: str
    entry: List[dict]

@app.post("/webhook/whatsapp")
async def handle_whatsapp_webhook(request: Request):
    """
    Recebe webhook do WhatsApp Business API
    
    Validações:
    - Verificar signature do Meta
    - Validar formato do payload
    - Deduplicar mensagens (idempotência)
    
    Returns:
        200 OK para confirmar recebimento
    """
    # Validar signature
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_signature(await request.body(), signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Processar webhook
    payload = await request.json()
    webhook = WhatsAppWebhook(**payload)
    
    # Extrair mensagens
    for entry in webhook.entry:
        for change in entry.get("changes", []):
            if change.get("field") == "messages":
                messages = change["value"].get("messages", [])
                for msg in messages:
                    # Processar mensagem de forma assíncrona
                    await process_message_async(msg)
    
    return {"status": "ok"}

@app.get("/webhook/whatsapp")
async def verify_whatsapp_webhook(
    hub_mode: str,
    hub_challenge: str,
    hub_verify_token: str
):
    """
    Verificação inicial do webhook pelo Meta
    """
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Invalid verify token")
```

**Dependências**:
- FastAPI para endpoints
- Pydantic para validação
- Celery para processamento assíncrono
- Redis para deduplicação

---

### 2. NLP Service (LangGraph)

**Responsabilidade**: Processar linguagem natural e extrair intenções

**Interface**:
```python
from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum

class Intent(str, Enum):
    """Intenções identificadas"""
    GREETING = "greeting"
    BUDGET_INQUIRY = "budget_inquiry"
    CAR_RECOMMENDATION = "car_recommendation"
    CAR_DETAILS = "car_details"
    COMPARE_CARS = "compare_cars"
    SCHEDULE_TEST_DRIVE = "schedule_test_drive"
    CONTACT_DEALER = "contact_dealer"
    HUMAN_HANDOFF = "human_handoff"
    FEEDBACK_POSITIVE = "feedback_positive"
    FEEDBACK_NEGATIVE = "feedback_negative"
    UNKNOWN = "unknown"

class Entity(BaseModel):
    """Entidade extraída da mensagem"""
    type: str  # budget, brand, category, year, etc
    value: str
    confidence: float

class NLPResult(BaseModel):
    """Resultado do processamento NLP"""
    intent: Intent
    confidence: float
    entities: List[Entity]
    sentiment: str  # positive, neutral, negative
    language: str = "pt-BR"

class NLPService:
    """Serviço de processamento de linguagem natural"""
    
    def __init__(self):
        self.model = self._load_model()
        self.intent_classifier = self._load_intent_classifier()
        self.entity_extractor = self._load_entity_extractor()
    
    async def process(self, text: str) -> NLPResult:
        """
        Processar texto e extrair intenção + entidades
        
        Args:
            text: Mensagem do usuário
            
        Returns:
            NLPResult com intenção, entidades e sentimento
        """
        # Normalizar texto
        normalized = self._normalize_text(text)
        
        # Classificar intenção
        intent, confidence = await self._classify_intent(normalized)
        
        # Extrair entidades
        entities = await self._extract_entities(normalized, intent)
        
        # Analisar sentimento
        sentiment = await self._analyze_sentiment(normalized)
        
        return NLPResult(
            intent=intent,
            confidence=confidence,
            entities=entities,
            sentiment=sentiment
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normalizar texto (lowercase, remover acentos, etc)"""
        pass
    
    async def _classify_intent(self, text: str) -> tuple[Intent, float]:
        """Classificar intenção usando modelo treinado"""
        pass
    
    async def _extract_entities(self, text: str, intent: Intent) -> List[Entity]:
        """Extrair entidades relevantes baseado na intenção"""
        pass
    
    async def _analyze_sentiment(self, text: str) -> str:
        """Analisar sentimento da mensagem"""
        pass
```

**Tecnologias**:
- LangGraph para orquestração de fluxo NLP
- spaCy ou Transformers para NER
- Modelo fine-tuned em português automotivo
- Redis para cache de resultados

---

### 3. Session Manager (PydanticAI)

**Responsabilidade**: Gerenciar sessões e contexto conversacional

**Interface**:
```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class SessionState(str, Enum):
    """Estados da sessão"""
    GREETING = "greeting"
    COLLECTING_PROFILE = "collecting_profile"
    GENERATING_RECOMMENDATIONS = "generating_recommendations"
    SHOWING_RECOMMENDATIONS = "showing_recommendations"
    CAR_DETAILS = "car_details"
    COMPARING_CARS = "comparing_cars"
    HUMAN_HANDOFF = "human_handoff"
    COMPLETED = "completed"

class ConversationMemory(BaseModel):
    """Memória episódica da conversa"""
    messages: List[Dict] = Field(default_factory=list)
    summary: str = ""
    last_updated: datetime = Field(default_factory=datetime.now)

class UserProfileData(BaseModel):
    """Dados do perfil do usuário coletados"""
    orcamento_min: Optional[float] = None
    orcamento_max: Optional[float] = None
    uso_principal: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    prioridades: Dict[str, int] = Field(default_factory=dict)
    marcas_preferidas: List[str] = Field(default_factory=list)
    tipos_preferidos: List[str] = Field(default_factory=list)
    completeness: float = 0.0  # 0-1

class SessionData(BaseModel):
    """Dados da sessão (PydanticAI)"""
    session_id: str
    phone_number: str
    state: SessionState = SessionState.GREETING
    turn_id: int = 0
    memory: ConversationMemory = Field(default_factory=ConversationMemory)
    user_profile: UserProfileData = Field(default_factory=UserProfileData)
    current_recommendations: List[str] = Field(default_factory=list)
    qualification_score: float = 0.0  # 0-100
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    ttl_seconds: int = 86400  # 24 hours

class SessionManager:
    """Gerenciador de sessões com PydanticAI"""
    
    def __init__(self, redis_client, duckdb_conn):
        self.redis = redis_client
        self.duckdb = duckdb_conn
    
    async def get_or_create_session(self, phone_number: str) -> SessionData:
        """
        Obter sessão existente ou criar nova
        
        Usa Redis com locks distribuídos para evitar race conditions
        """
        session_key = f"session:{phone_number}"
        
        # Tentar obter sessão do Redis
        session_json = await self.redis.get(session_key)
        
        if session_json:
            return SessionData.parse_raw(session_json)
        
        # Criar nova sessão com lock
        lock_key = f"lock:{session_key}"
        lock_acquired = await self.redis.set(
            lock_key, "1", nx=True, ex=10
        )
        
        if not lock_acquired:
            # Aguardar lock ser liberado
            await asyncio.sleep(0.1)
            return await self.get_or_create_session(phone_number)
        
        try:
            # Criar nova sessão
            session = SessionData(
                session_id=f"{phone_number}:{int(time.time())}",
                phone_number=phone_number
            )
            
            # Salvar no Redis
            await self.redis.setex(
                session_key,
                session.ttl_seconds,
                session.json()
            )
            
            return session
        finally:
            # Liberar lock
            await self.redis.delete(lock_key)
    
    async def update_session(self, session: SessionData) -> bool:
        """
        Atualizar sessão com idempotência
        
        Usa session_id:turn_id como chave de idempotência
        """
        session.turn_id += 1
        session.updated_at = datetime.now()
        
        idempotency_key = f"idempotency:{session.session_id}:{session.turn_id}"
        
        # Verificar se já foi processado
        if await self.redis.exists(idempotency_key):
            return False  # Já processado
        
        # Marcar como processado
        await self.redis.setex(idempotency_key, 3600, "1")
        
        # Atualizar sessão no Redis
        session_key = f"session:{session.phone_number}"
        await self.redis.setex(
            session_key,
            session.ttl_seconds,
            session.json()
        )
        
        # Salvar resumo no DuckDB (assíncrono via Celery)
        await self._save_to_duckdb_async(session)
        
        return True
    
    async def _save_to_duckdb_async(self, session: SessionData):
        """Salvar resumo no DuckDB via Celery"""
        from tasks import save_session_to_duckdb
        save_session_to_duckdb.delay(session.dict())
```

**Tecnologias**:
- PydanticAI para memória tipada
- Redis para cache e locks
- DuckDB para contexto estruturado
- Celery para persistência assíncrona


---

### 4. Conversation Engine (LangGraph)

**Responsabilidade**: Orquestrar fluxo conversacional e gerar respostas

**Interface**:
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class ConversationState(TypedDict):
    """Estado do grafo conversacional"""
    messages: Annotated[list, operator.add]
    session: SessionData
    nlp_result: NLPResult
    response: str
    next_action: str

class ConversationEngine:
    """Engine conversacional usando LangGraph"""
    
    def __init__(self, nlp_service: NLPService, session_manager: SessionManager):
        self.nlp = nlp_service
        self.session_manager = session_manager
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Construir grafo de estados conversacionais"""
        workflow = StateGraph(ConversationState)
        
        # Nós do grafo
        workflow.add_node("process_nlp", self._process_nlp)
        workflow.add_node("handle_greeting", self._handle_greeting)
        workflow.add_node("collect_profile", self._collect_profile)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("show_car_details", self._show_car_details)
        workflow.add_node("compare_cars", self._compare_cars)
        workflow.add_node("human_handoff", self._human_handoff)
        workflow.add_node("apply_guardrails", self._apply_guardrails)
        
        # Edges condicionais
        workflow.set_entry_point("process_nlp")
        workflow.add_conditional_edges(
            "process_nlp",
            self._route_by_intent,
            {
                Intent.GREETING: "handle_greeting",
                Intent.BUDGET_INQUIRY: "collect_profile",
                Intent.CAR_RECOMMENDATION: "generate_recommendations",
                Intent.CAR_DETAILS: "show_car_details",
                Intent.COMPARE_CARS: "compare_cars",
                Intent.HUMAN_HANDOFF: "human_handoff",
            }
        )
        
        # Todos os nós passam por guardrails antes de finalizar
        for node in ["handle_greeting", "collect_profile", "generate_recommendations", 
                     "show_car_details", "compare_cars", "human_handoff"]:
            workflow.add_edge(node, "apply_guardrails")
        
        workflow.add_edge("apply_guardrails", END)
        
        return workflow.compile()
    
    async def process_message(
        self, 
        phone_number: str, 
        message: str
    ) -> str:
        """
        Processar mensagem e gerar resposta
        
        Args:
            phone_number: Número do WhatsApp
            message: Mensagem do usuário
            
        Returns:
            Resposta do chatbot
        """
        # Obter ou criar sessão
        session = await self.session_manager.get_or_create_session(phone_number)
        
        # Processar NLP
        nlp_result = await self.nlp.process(message)
        
        # Estado inicial
        initial_state = ConversationState(
            messages=[{"role": "user", "content": message}],
            session=session,
            nlp_result=nlp_result,
            response="",
            next_action=""
        )
        
        # Executar grafo
        final_state = await self.graph.ainvoke(initial_state)
        
        # Atualizar sessão
        session.memory.messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        session.memory.messages.append({
            "role": "assistant",
            "content": final_state["response"],
            "timestamp": datetime.now().isoformat()
        })
        
        await self.session_manager.update_session(session)
        
        return final_state["response"]
    
    async def _process_nlp(self, state: ConversationState) -> ConversationState:
        """Processar NLP (já feito antes, apenas passa adiante)"""
        return state
    
    def _route_by_intent(self, state: ConversationState) -> str:
        """Rotear para handler baseado na intenção"""
        return state["nlp_result"].intent
    
    async def _handle_greeting(self, state: ConversationState) -> ConversationState:
        """Handler para saudações"""
        state["response"] = (
            "Olá! 👋 Bem-vindo ao FacilIAuto!\n\n"
            "Sou seu assistente virtual e vou te ajudar a encontrar o carro ideal.\n\n"
            "Para começar, me conta: qual é o seu orçamento aproximado?"
        )
        state["session"].state = SessionState.COLLECTING_PROFILE
        return state
    
    async def _collect_profile(self, state: ConversationState) -> ConversationState:
        """Coletar informações do perfil"""
        # Extrair entidades da mensagem
        for entity in state["nlp_result"].entities:
            if entity.type == "budget":
                # Atualizar orçamento no perfil
                budget_value = float(entity.value)
                if not state["session"].user_profile.orcamento_min:
                    state["session"].user_profile.orcamento_min = budget_value * 0.8
                    state["session"].user_profile.orcamento_max = budget_value * 1.2
        
        # Calcular completude do perfil
        profile = state["session"].user_profile
        completeness = sum([
            1 if profile.orcamento_min else 0,
            1 if profile.uso_principal else 0,
            1 if profile.city else 0,
            1 if len(profile.prioridades) >= 3 else 0,
        ]) / 4.0
        
        profile.completeness = completeness
        
        # Determinar próxima pergunta
        if not profile.orcamento_min:
            state["response"] = "Qual é o seu orçamento aproximado para o carro?"
        elif not profile.uso_principal:
            state["response"] = "Como você pretende usar o carro? (trabalho, família, lazer, etc)"
        elif not profile.city:
            state["response"] = "Em qual cidade você está procurando?"
        elif len(profile.prioridades) < 3:
            state["response"] = (
                "Quais são suas prioridades? Escolha 3:\n"
                "1️⃣ Economia de combustível\n"
                "2️⃣ Espaço interno\n"
                "3️⃣ Performance\n"
                "4️⃣ Conforto\n"
                "5️⃣ Segurança"
            )
        else:
            # Perfil completo, gerar recomendações
            state["response"] = (
                "Perfeito! ✅\n\n"
                "Já tenho todas as informações necessárias.\n"
                "Deixa eu buscar os melhores carros para você... 🔍"
            )
            state["next_action"] = "generate_recommendations"
        
        return state
    
    async def _generate_recommendations(self, state: ConversationState) -> ConversationState:
        """Gerar recomendações usando backend existente"""
        from services.backend_client import BackendClient
        
        client = BackendClient()
        profile = state["session"].user_profile
        
        # Converter para formato do backend
        user_profile = {
            "orcamento_min": profile.orcamento_min,
            "orcamento_max": profile.orcamento_max,
            "uso_principal": profile.uso_principal,
            "city": profile.city,
            "state": profile.state,
            "prioridades": profile.prioridades,
            "marcas_preferidas": profile.marcas_preferidas,
            "tipos_preferidos": profile.tipos_preferidos,
        }
        
        # Chamar API de recomendação
        recommendations = await client.get_recommendations(user_profile)
        
        # Formatar resposta
        if recommendations:
            response_text = "🎯 Encontrei ótimas opções para você!\n\n"
            
            for i, rec in enumerate(recommendations[:3], 1):
                car = rec["car"]
                score = rec["match_percentage"]
                justification = rec["justification"]
                
                response_text += (
                    f"{i}. *{car['marca']} {car['modelo']}* ({car['ano']})\n"
                    f"   💰 R$ {car['preco']:,.2f}\n"
                    f"   ⭐ {score}% de compatibilidade\n"
                    f"   📝 {justification}\n\n"
                )
            
            response_text += (
                "Digite o número do carro para ver mais detalhes "
                "ou 'mais opções' para ver outros carros."
            )
            
            state["response"] = response_text
            state["session"].current_recommendations = [
                rec["car"]["id"] for rec in recommendations[:3]
            ]
            state["session"].state = SessionState.SHOWING_RECOMMENDATIONS
        else:
            state["response"] = (
                "Hmm, não encontrei carros que atendam exatamente seu perfil. 😕\n\n"
                "Que tal ajustarmos o orçamento ou as preferências?"
            )
        
        return state
    
    async def _show_car_details(self, state: ConversationState) -> ConversationState:
        """Mostrar detalhes de um carro específico"""
        # Implementar lógica de detalhes
        state["response"] = "Detalhes do carro..."
        return state
    
    async def _compare_cars(self, state: ConversationState) -> ConversationState:
        """Comparar múltiplos carros"""
        # Implementar lógica de comparação
        state["response"] = "Comparação de carros..."
        return state
    
    async def _human_handoff(self, state: ConversationState) -> ConversationState:
        """Transferir para atendimento humano"""
        state["response"] = (
            "Entendi que você gostaria de falar com um atendente humano. 👤\n\n"
            "Estou transferindo você agora. Um de nossos especialistas "
            "entrará em contato em breve!"
        )
        state["session"].state = SessionState.HUMAN_HANDOFF
        
        # Notificar equipe de atendimento (via Celery)
        from tasks import notify_human_handoff
        notify_human_handoff.delay(
            phone_number=state["session"].phone_number,
            session_id=state["session"].session_id,
            context=state["session"].dict()
        )
        
        return state
    
    async def _apply_guardrails(self, state: ConversationState) -> ConversationState:
        """Aplicar guardrails para evitar duplicações"""
        from services.guardrails import GuardrailsService
        
        guardrails = GuardrailsService()
        
        # Deduplicação por hash
        response_hash = guardrails.hash_content(state["response"])
        
        # Verificar se já foi enviado recentemente
        recent_hashes_key = f"recent_hashes:{state['session'].phone_number}"
        recent_hashes = await self.session_manager.redis.lrange(
            recent_hashes_key, 0, 4
        )
        
        if response_hash.encode() in recent_hashes:
            # Resposta duplicada, reformular
            state["response"] = guardrails.rephrase_response(state["response"])
        
        # Adicionar hash à lista de recentes
        await self.session_manager.redis.lpush(recent_hashes_key, response_hash)
        await self.session_manager.redis.ltrim(recent_hashes_key, 0, 4)
        await self.session_manager.redis.expire(recent_hashes_key, 3600)
        
        # Aplicar filtros de estilo
        state["response"] = guardrails.apply_style_filters(state["response"])
        
        return state
```

**Tecnologias**:
- LangGraph para grafo de estados
- Checkpoints para recuperação
- Guardrails para qualidade de resposta
- Integração com backend existente


---

## Data Models

### Database Schema (PostgreSQL)

```sql
-- Tabela de usuários/leads
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    gdpr_consent BOOLEAN DEFAULT FALSE,
    gdpr_consent_date TIMESTAMP
);

-- Tabela de sessões (histórico)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    phone_number VARCHAR(20) NOT NULL,
    state VARCHAR(50) NOT NULL,
    qualification_score FLOAT DEFAULT 0.0,
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    total_messages INT DEFAULT 0,
    INDEX idx_phone (phone_number),
    INDEX idx_session_id (session_id)
);

-- Tabela de mensagens
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id),
    message_id VARCHAR(255) UNIQUE NOT NULL,
    direction VARCHAR(10) NOT NULL, -- inbound, outbound
    content TEXT NOT NULL,
    message_type VARCHAR(20) NOT NULL, -- text, audio, image, etc
    intent VARCHAR(50),
    sentiment VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_session (session_id),
    INDEX idx_created (created_at)
);

-- Tabela de leads qualificados
CREATE TABLE qualified_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_id UUID REFERENCES sessions(id),
    qualification_score FLOAT NOT NULL,
    profile_data JSONB NOT NULL,
    recommended_cars JSONB,
    assigned_to_dealer UUID,
    status VARCHAR(50) DEFAULT 'new', -- new, contacted, converted, lost
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_score (qualification_score),
    INDEX idx_status (status)
);

-- Tabela de interações com carros
CREATE TABLE car_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_id UUID REFERENCES sessions(id),
    car_id VARCHAR(255) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL, -- viewed, liked, disliked, contacted
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user (user_id),
    INDEX idx_car (car_id)
);

-- Tabela de handoffs para humanos
CREATE TABLE human_handoffs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id),
    user_id UUID REFERENCES users(id),
    reason TEXT,
    context JSONB,
    assigned_to VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    rating INT, -- 1-5
    feedback TEXT,
    INDEX idx_status (status)
);

-- Tabela de métricas agregadas
CREATE TABLE metrics_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    total_sessions INT DEFAULT 0,
    total_messages INT DEFAULT 0,
    total_qualified_leads INT DEFAULT 0,
    avg_qualification_score FLOAT DEFAULT 0.0,
    avg_messages_per_session FLOAT DEFAULT 0.0,
    avg_response_time_ms FLOAT DEFAULT 0.0,
    nlp_accuracy FLOAT DEFAULT 0.0,
    handoff_rate FLOAT DEFAULT 0.0,
    conversion_rate FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date)
);
```

### DuckDB Schema (Analytical Queries)

```sql
-- Contexto estruturado para consultas rápidas
CREATE TABLE conversation_context (
    session_id VARCHAR PRIMARY KEY,
    phone_number VARCHAR NOT NULL,
    summary TEXT,
    key_entities JSON,
    user_profile JSON,
    last_updated TIMESTAMP,
    message_count INT
);

-- Histórico de mensagens para análise
CREATE TABLE message_history (
    message_id VARCHAR PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    content TEXT,
    intent VARCHAR,
    entities JSON,
    sentiment VARCHAR,
    timestamp TIMESTAMP
);

-- Embeddings para busca semântica
CREATE TABLE message_embeddings (
    message_id VARCHAR PRIMARY KEY,
    embedding FLOAT[768], -- Dimensão do modelo
    timestamp TIMESTAMP
);
```

---

## Error Handling

### Error Categories

**1. WhatsApp API Errors**
- Rate limiting (429): Retry com backoff exponencial
- Invalid token (401): Alertar equipe, renovar token
- Webhook timeout (504): Processar de forma assíncrona
- Message delivery failed: Tentar reenvio até 3x

**2. NLP Processing Errors**
- Low confidence (<0.5): Solicitar esclarecimento ao usuário
- Unknown intent: Oferecer opções de menu
- Entity extraction failed: Fazer perguntas diretas
- Language detection failed: Assumir pt-BR

**3. Backend Integration Errors**
- API timeout: Usar cache de recomendações anteriores
- API down: Ativar circuit breaker, modo degradado
- Invalid response: Logar erro, responder com mensagem genérica
- Rate limit exceeded: Enfileirar requisição

**4. Database Errors**
- Connection timeout: Retry com backoff
- Deadlock: Retry transação
- Constraint violation: Logar e notificar
- Disk full: Alertar infraestrutura

**5. Session Management Errors**
- Session expired: Criar nova sessão, explicar ao usuário
- Lock timeout: Retry após delay
- Corrupted session data: Criar nova sessão
- Redis unavailable: Usar fallback em memória (temporário)

### Error Response Strategy

```python
class ErrorHandler:
    """Gerenciador centralizado de erros"""
    
    async def handle_error(
        self, 
        error: Exception, 
        context: dict
    ) -> str:
        """
        Tratar erro e retornar mensagem apropriada
        
        Args:
            error: Exceção capturada
            context: Contexto da operação
            
        Returns:
            Mensagem amigável para o usuário
        """
        # Logar erro
        logger.error(
            f"Error: {type(error).__name__}",
            extra={
                "error": str(error),
                "context": context,
                "traceback": traceback.format_exc()
            }
        )
        
        # Determinar tipo de erro
        if isinstance(error, WhatsAppAPIError):
            return await self._handle_whatsapp_error(error, context)
        elif isinstance(error, NLPProcessingError):
            return await self._handle_nlp_error(error, context)
        elif isinstance(error, BackendAPIError):
            return await self._handle_backend_error(error, context)
        elif isinstance(error, DatabaseError):
            return await self._handle_database_error(error, context)
        else:
            return await self._handle_unknown_error(error, context)
    
    async def _handle_whatsapp_error(
        self, 
        error: WhatsAppAPIError, 
        context: dict
    ) -> str:
        """Tratar erros da API do WhatsApp"""
        if error.status_code == 429:
            # Rate limit
            return (
                "Desculpe, estamos com muitas mensagens no momento. 😅\n"
                "Vou responder em alguns segundos!"
            )
        elif error.status_code == 401:
            # Token inválido
            await self._alert_team("WhatsApp token expired")
            return (
                "Ops, tivemos um problema técnico. 🔧\n"
                "Nossa equipe já foi notificada. Tente novamente em alguns minutos."
            )
        else:
            return (
                "Desculpe, não consegui enviar a mensagem. 📱\n"
                "Pode tentar novamente?"
            )
    
    async def _handle_nlp_error(
        self, 
        error: NLPProcessingError, 
        context: dict
    ) -> str:
        """Tratar erros de processamento NLP"""
        return (
            "Desculpe, não entendi muito bem. 🤔\n\n"
            "Pode reformular sua pergunta? Ou escolha uma opção:\n"
            "1️⃣ Ver recomendações de carros\n"
            "2️⃣ Falar com atendente\n"
            "3️⃣ Recomeçar conversa"
        )
    
    async def _handle_backend_error(
        self, 
        error: BackendAPIError, 
        context: dict
    ) -> str:
        """Tratar erros do backend"""
        # Ativar circuit breaker se muitos erros
        if await self._should_activate_circuit_breaker():
            await self._activate_circuit_breaker()
        
        return (
            "Estou com dificuldade para buscar os carros agora. 🔍\n\n"
            "Mas não se preocupe! Posso te passar para um atendente "
            "que vai te ajudar. Quer falar com alguém?"
        )
    
    async def _handle_database_error(
        self, 
        error: DatabaseError, 
        context: dict
    ) -> str:
        """Tratar erros de banco de dados"""
        await self._alert_team(f"Database error: {error}")
        
        return (
            "Tivemos um probleminha técnico aqui. 🔧\n\n"
            "Mas já estamos resolvendo! Pode tentar novamente em 1 minuto?"
        )
    
    async def _handle_unknown_error(
        self, 
        error: Exception, 
        context: dict
    ) -> str:
        """Tratar erros desconhecidos"""
        await self._alert_team(f"Unknown error: {error}")
        
        return (
            "Ops, algo inesperado aconteceu. 😅\n\n"
            "Nossa equipe já foi notificada. "
            "Quer que eu te passe para um atendente?"
        )
    
    async def _should_activate_circuit_breaker(self) -> bool:
        """Verificar se deve ativar circuit breaker"""
        # Verificar taxa de erro nos últimos 5 minutos
        error_count = await self.redis.get("error_count:backend:5min")
        return int(error_count or 0) > 10
    
    async def _activate_circuit_breaker(self):
        """Ativar circuit breaker"""
        await self.redis.setex("circuit_breaker:backend", 300, "1")
        await self._alert_team("Circuit breaker activated for backend")
    
    async def _alert_team(self, message: str):
        """Alertar equipe técnica"""
        # Enviar para Slack/PagerDuty
        pass
```

---

## Testing Strategy

### Test Pyramid

```
                    /\
                   /  \
                  / E2E \          10% - Testes End-to-End
                 /______\
                /        \
               / Integration\      30% - Testes de Integração
              /____________\
             /              \
            /   Unit Tests   \    60% - Testes Unitários
           /__________________\
```

### 1. Unit Tests (60% - TDD)

**Cobertura**: >= 80% conforme metodologia XP

```python
# tests/test_nlp_service.py
import pytest
from services.nlp_service import NLPService, Intent

@pytest.fixture
def nlp_service():
    return NLPService()

class TestNLPService:
    """Testes unitários do serviço NLP"""
    
    @pytest.mark.asyncio
    async def test_classify_greeting_intent(self, nlp_service):
        """Deve classificar saudações corretamente"""
        # Arrange
        messages = ["oi", "olá", "bom dia", "boa tarde"]
        
        # Act & Assert
        for msg in messages:
            result = await nlp_service.process(msg)
            assert result.intent == Intent.GREETING
            assert result.confidence >= 0.85
    
    @pytest.mark.asyncio
    async def test_extract_budget_entity(self, nlp_service):
        """Deve extrair orçamento da mensagem"""
        # Arrange
        message = "Tenho até 50 mil para gastar"
        
        # Act
        result = await nlp_service.process(message)
        
        # Assert
        budget_entities = [e for e in result.entities if e.type == "budget"]
        assert len(budget_entities) == 1
        assert float(budget_entities[0].value) == 50000
    
    @pytest.mark.asyncio
    async def test_handle_unknown_intent(self, nlp_service):
        """Deve retornar UNKNOWN para mensagens não reconhecidas"""
        # Arrange
        message = "xpto abc 123"
        
        # Act
        result = await nlp_service.process(message)
        
        # Assert
        assert result.intent == Intent.UNKNOWN
        assert result.confidence < 0.5
```


```python
# tests/test_session_manager.py
import pytest
from services.session_manager import SessionManager, SessionState

@pytest.fixture
async def session_manager(redis_client, duckdb_conn):
    return SessionManager(redis_client, duckdb_conn)

class TestSessionManager:
    """Testes unitários do gerenciador de sessões"""
    
    @pytest.mark.asyncio
    async def test_create_new_session(self, session_manager):
        """Deve criar nova sessão para número desconhecido"""
        # Arrange
        phone = "+5511999999999"
        
        # Act
        session = await session_manager.get_or_create_session(phone)
        
        # Assert
        assert session.phone_number == phone
        assert session.state == SessionState.GREETING
        assert session.turn_id == 0
    
    @pytest.mark.asyncio
    async def test_retrieve_existing_session(self, session_manager):
        """Deve recuperar sessão existente"""
        # Arrange
        phone = "+5511999999999"
        session1 = await session_manager.get_or_create_session(phone)
        session1.turn_id = 5
        await session_manager.update_session(session1)
        
        # Act
        session2 = await session_manager.get_or_create_session(phone)
        
        # Assert
        assert session2.session_id == session1.session_id
        assert session2.turn_id == 6  # Incrementado
    
    @pytest.mark.asyncio
    async def test_idempotency_prevents_duplicate_processing(
        self, 
        session_manager
    ):
        """Deve prevenir processamento duplicado com idempotência"""
        # Arrange
        phone = "+5511999999999"
        session = await session_manager.get_or_create_session(phone)
        
        # Act
        result1 = await session_manager.update_session(session)
        result2 = await session_manager.update_session(session)
        
        # Assert
        assert result1 is True  # Primeira atualização OK
        assert result2 is False  # Segunda bloqueada por idempotência
```

### 2. Integration Tests (30%)

```python
# tests/test_conversation_flow.py
import pytest
from services.conversation_engine import ConversationEngine
from services.nlp_service import NLPService
from services.session_manager import SessionManager

@pytest.fixture
async def conversation_engine(nlp_service, session_manager):
    return ConversationEngine(nlp_service, session_manager)

class TestConversationFlow:
    """Testes de integração do fluxo conversacional"""
    
    @pytest.mark.asyncio
    async def test_complete_qualification_flow(self, conversation_engine):
        """Deve completar fluxo de qualificação do lead"""
        # Arrange
        phone = "+5511999999999"
        messages = [
            "Oi",
            "Tenho até 60 mil",
            "Vou usar para trabalho",
            "Moro em São Paulo",
            "Priorizo economia, espaço e segurança"
        ]
        
        # Act
        responses = []
        for msg in messages:
            response = await conversation_engine.process_message(phone, msg)
            responses.append(response)
        
        # Assert
        assert "Bem-vindo" in responses[0]
        assert "orçamento" in responses[1].lower()
        assert "usar" in responses[2].lower()
        assert "cidade" in responses[3].lower()
        assert "recomendações" in responses[4].lower() or "carros" in responses[4].lower()
    
    @pytest.mark.asyncio
    async def test_handoff_to_human(self, conversation_engine):
        """Deve transferir para humano quando solicitado"""
        # Arrange
        phone = "+5511999999999"
        message = "Quero falar com um atendente"
        
        # Act
        response = await conversation_engine.process_message(phone, message)
        
        # Assert
        assert "atendente" in response.lower()
        assert "transferindo" in response.lower()
        
        # Verificar que sessão foi marcada para handoff
        session = await conversation_engine.session_manager.get_or_create_session(phone)
        assert session.state == SessionState.HUMAN_HANDOFF
    
    @pytest.mark.asyncio
    async def test_backend_integration_recommendations(
        self, 
        conversation_engine,
        mock_backend_api
    ):
        """Deve integrar com backend para gerar recomendações"""
        # Arrange
        phone = "+5511999999999"
        
        # Simular perfil completo
        session = await conversation_engine.session_manager.get_or_create_session(phone)
        session.user_profile.orcamento_min = 40000
        session.user_profile.orcamento_max = 60000
        session.user_profile.uso_principal = "trabalho"
        session.user_profile.city = "São Paulo"
        session.user_profile.prioridades = {
            "economia": 5,
            "espaco": 4,
            "seguranca": 4
        }
        await conversation_engine.session_manager.update_session(session)
        
        # Act
        response = await conversation_engine.process_message(
            phone, 
            "Me mostre os carros"
        )
        
        # Assert
        assert "R$" in response  # Deve conter preços
        assert "%" in response  # Deve conter scores
        assert mock_backend_api.called  # Backend foi chamado
```

### 3. E2E Tests (10%)

```python
# tests/e2e/test_whatsapp_flow.py
import pytest
from playwright.async_api import async_playwright

@pytest.mark.e2e
class TestWhatsAppE2E:
    """Testes End-to-End simulando usuário real"""
    
    @pytest.mark.asyncio
    async def test_complete_user_journey(self, whatsapp_simulator):
        """
        Simular jornada completa do usuário:
        1. Enviar mensagem inicial
        2. Responder perguntas de qualificação
        3. Receber recomendações
        4. Ver detalhes de carro
        5. Solicitar contato com concessionária
        """
        # Arrange
        phone = "+5511999999999"
        
        # Act & Assert
        # 1. Saudação inicial
        response1 = await whatsapp_simulator.send_message(phone, "Oi")
        assert "Bem-vindo" in response1
        assert whatsapp_simulator.message_delivered(response1)
        
        # 2. Informar orçamento
        response2 = await whatsapp_simulator.send_message(
            phone, 
            "Tenho 50 mil"
        )
        assert "uso" in response2.lower() or "usar" in response2.lower()
        
        # 3. Informar uso
        response3 = await whatsapp_simulator.send_message(
            phone, 
            "Para trabalho"
        )
        assert "cidade" in response3.lower()
        
        # 4. Informar localização
        response4 = await whatsapp_simulator.send_message(
            phone, 
            "São Paulo"
        )
        assert "prioridades" in response4.lower()
        
        # 5. Informar prioridades
        response5 = await whatsapp_simulator.send_message(
            phone, 
            "Economia, espaço e segurança"
        )
        assert "recomendações" in response5.lower() or "carros" in response5.lower()
        
        # 6. Receber recomendações
        await asyncio.sleep(2)  # Aguardar processamento
        response6 = await whatsapp_simulator.get_last_message(phone)
        assert "R$" in response6
        assert "%" in response6
        assert len(response6.split("\n")) > 10  # Múltiplas linhas
        
        # 7. Solicitar detalhes
        response7 = await whatsapp_simulator.send_message(phone, "1")
        assert "detalhes" in response7.lower() or "especificações" in response7.lower()
        
        # 8. Solicitar contato
        response8 = await whatsapp_simulator.send_message(
            phone, 
            "Quero falar com a concessionária"
        )
        assert "contato" in response8.lower()
        assert "whatsapp" in response8.lower() or "telefone" in response8.lower()
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, whatsapp_simulator):
        """
        Testar performance com múltiplos usuários simultâneos
        
        Requisitos:
        - 100 conversas simultâneas
        - Latência P95 < 3s
        - Taxa de erro < 1%
        """
        # Arrange
        num_users = 100
        phones = [f"+551199999{i:04d}" for i in range(num_users)]
        
        # Act
        start_time = time.time()
        tasks = [
            whatsapp_simulator.send_message(phone, "Oi")
            for phone in phones
        ]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Assert
        # Todas as mensagens foram entregues
        assert len(responses) == num_users
        
        # Calcular latências
        latencies = [r.latency_ms for r in responses]
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
        
        assert p95_latency < 3000, f"P95 latency {p95_latency}ms > 3000ms"
        
        # Taxa de erro
        errors = [r for r in responses if r.error]
        error_rate = len(errors) / num_users
        
        assert error_rate < 0.01, f"Error rate {error_rate:.2%} > 1%"
    
    @pytest.mark.asyncio
    async def test_nlp_accuracy(self, whatsapp_simulator, test_dataset):
        """
        Testar precisão do NLP com dataset de 500+ mensagens reais
        
        Requisito: Precisão >= 85%
        """
        # Arrange
        phone = "+5511999999999"
        correct_predictions = 0
        total_predictions = 0
        
        # Act
        for test_case in test_dataset:
            message = test_case["message"]
            expected_intent = test_case["intent"]
            
            response = await whatsapp_simulator.send_message(phone, message)
            predicted_intent = await whatsapp_simulator.get_last_intent(phone)
            
            if predicted_intent == expected_intent:
                correct_predictions += 1
            total_predictions += 1
        
        # Assert
        accuracy = correct_predictions / total_predictions
        assert accuracy >= 0.85, f"NLP accuracy {accuracy:.2%} < 85%"
```

### Test Execution

```bash
# Rodar todos os testes
pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

# Rodar apenas testes unitários (rápido, TDD)
pytest tests/test_*.py -v -m "not integration and not e2e"

# Rodar testes de integração
pytest tests/test_*.py -v -m integration

# Rodar testes E2E (lento, CI/CD)
pytest tests/e2e/ -v -m e2e --timeout=300

# Rodar com coverage mínimo de 80%
pytest tests/ --cov=. --cov-fail-under=80
```

### CI/CD Pipeline

```yaml
# .github/workflows/chatbot-tests.yml
name: Chatbot Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run unit tests
        run: |
          pytest tests/ -v -m "not integration and not e2e" \
            --cov=. --cov-report=xml --cov-fail-under=80
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
  
  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    services:
      redis:
        image: redis:7
        ports:
          - 6379:6379
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run integration tests
        run: |
          pytest tests/ -v -m integration
        env:
          REDIS_URL: redis://localhost:6379
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test
  
  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio playwright
          playwright install
      
      - name: Start services
        run: |
          docker-compose up -d
          sleep 10  # Aguardar serviços iniciarem
      
      - name: Run E2E tests
        run: |
          pytest tests/e2e/ -v -m e2e --timeout=300
      
      - name: Stop services
        if: always()
        run: docker-compose down
```

---

## Deployment Strategy

### Infrastructure (Kubernetes)

```yaml
# k8s/chatbot-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: whatsapp-chatbot
  labels:
    app: whatsapp-chatbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: whatsapp-chatbot
  template:
    metadata:
      labels:
        app: whatsapp-chatbot
    spec:
      containers:
      - name: chatbot
        image: faciliauto/whatsapp-chatbot:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: redis-url
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: database-url
        - name: WHATSAPP_TOKEN
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: whatsapp-token
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: whatsapp-chatbot
spec:
  selector:
    app: whatsapp-chatbot
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: whatsapp-chatbot-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: whatsapp-chatbot
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Blue-Green Deployment

```bash
# deploy.sh
#!/bin/bash

# Build nova versão
docker build -t faciliauto/whatsapp-chatbot:$VERSION .

# Push para registry
docker push faciliauto/whatsapp-chatbot:$VERSION

# Deploy green environment
kubectl apply -f k8s/chatbot-deployment-green.yaml

# Aguardar pods ficarem ready
kubectl wait --for=condition=ready pod -l app=whatsapp-chatbot-green --timeout=300s

# Rodar smoke tests
pytest tests/smoke/ -v

# Switch traffic para green
kubectl patch service whatsapp-chatbot -p '{"spec":{"selector":{"version":"green"}}}'

# Monitorar por 5 minutos
sleep 300

# Se tudo OK, remover blue
kubectl delete deployment whatsapp-chatbot-blue

# Se houver problema, rollback
# kubectl patch service whatsapp-chatbot -p '{"spec":{"selector":{"version":"blue"}}}'
```

---

## Monitoring and Observability

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Contadores
messages_received = Counter(
    'chatbot_messages_received_total',
    'Total de mensagens recebidas',
    ['direction', 'type']
)

messages_sent = Counter(
    'chatbot_messages_sent_total',
    'Total de mensagens enviadas',
    ['status']
)

nlp_predictions = Counter(
    'chatbot_nlp_predictions_total',
    'Total de predições NLP',
    ['intent', 'confidence_bucket']
)

leads_qualified = Counter(
    'chatbot_leads_qualified_total',
    'Total de leads qualificados',
    ['score_bucket']
)

# Histogramas
response_latency = Histogram(
    'chatbot_response_latency_seconds',
    'Latência de resposta',
    ['endpoint']
)

nlp_processing_time = Histogram(
    'chatbot_nlp_processing_seconds',
    'Tempo de processamento NLP'
)

# Gauges
active_sessions = Gauge(
    'chatbot_active_sessions',
    'Número de sessões ativas'
)

redis_connections = Gauge(
    'chatbot_redis_connections',
    'Conexões ativas no Redis'
)
```

### Grafana Dashboards

**Dashboard 1: Overview**
- Total de mensagens (24h, 7d, 30d)
- Taxa de qualificação de leads
- Latência média e P95
- Taxa de erro
- Sessões ativas

**Dashboard 2: NLP Performance**
- Distribuição de intenções
- Precisão por intenção
- Tempo de processamento
- Taxa de unknown intents
- Análise de sentimento

**Dashboard 3: Business Metrics**
- Leads qualificados por dia
- Score médio de qualificação
- Taxa de conversão
- Handoffs para humanos
- Carros mais recomendados

**Dashboard 4: Infrastructure**
- CPU e memória por pod
- Latência de rede
- Redis hit rate
- Database connections
- Celery queue size

---

## Security and Compliance

### LGPD Compliance

**1. Consentimento**
```python
async def request_gdpr_consent(phone_number: str):
    """Solicitar consentimento LGPD"""
    message = (
        "📋 *Termos de Uso e Privacidade*\n\n"
        "Para continuar, preciso do seu consentimento para:\n"
        "✅ Coletar e processar seus dados pessoais\n"
        "✅ Armazenar histórico de conversas\n"
        "✅ Compartilhar informações com concessionárias\n\n"
        "Seus dados são protegidos conforme a LGPD.\n"
        "Você pode solicitar exclusão a qualquer momento.\n\n"
        "Digite 'ACEITO' para continuar."
    )
    await send_whatsapp_message(phone_number, message)
```

**2. Direito ao Esquecimento**
```python
async def handle_data_deletion_request(phone_number: str):
    """Processar solicitação de exclusão de dados"""
    # Anonimizar dados no PostgreSQL
    await db.execute(
        "UPDATE users SET name = 'DELETED', email = 'DELETED' "
        "WHERE phone_number = $1",
        phone_number
    )
    
    # Remover sessão do Redis
    await redis.delete(f"session:{phone_number}")
    
    # Remover contexto do DuckDB
    await duckdb.execute(
        "DELETE FROM conversation_context WHERE phone_number = ?",
        [phone_number]
    )
    
    # Logar auditoria
    await audit_log.log(
        event="data_deletion",
        phone_number=phone_number,
        timestamp=datetime.now()
    )
    
    message = (
        "✅ Seus dados foram excluídos com sucesso.\n\n"
        "Obrigado por usar o FacilIAuto!"
    )
    await send_whatsapp_message(phone_number, message)
```

### Security Best Practices

**1. Criptografia**
- TLS 1.3 para todas as comunicações
- AES-256 para dados sensíveis em repouso
- Tokens JWT com expiração de 1 hora
- Secrets gerenciados via HashiCorp Vault

**2. Autenticação e Autorização**
- API keys para WhatsApp Business API
- JWT para comunicação entre serviços
- Rate limiting por número de telefone
- IP whitelisting para webhooks

**3. Auditoria**
- Logs de todas as operações sensíveis
- Retenção de logs por 1 ano
- Alertas para atividades suspeitas
- Compliance reports mensais

---

## Conclusion

Este design apresenta uma arquitetura robusta, escalável e alinhada com as melhores práticas de XP e E2E testing para o chatbot WhatsApp do FacilIAuto. A solução integra-se perfeitamente com o ecossistema existente, aproveitando o UnifiedRecommendationEngine e os 12 agentes especializados, enquanto implementa tecnologias modernas como PydanticAI, LangGraph, Redis, DuckDB, Guardrails e Celery para garantir conversas naturais, performáticas e sem duplicações.

**Próximos Passos**: Criar o plano de implementação (tasks.md) com tarefas detalhadas seguindo metodologia XP.
```

