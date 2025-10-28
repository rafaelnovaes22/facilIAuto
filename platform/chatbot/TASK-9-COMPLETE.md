# Task 9: Implementar Celery Workers - COMPLETO ✅

## Resumo da Implementação

A Task 9 foi completada com sucesso. Implementamos toda a infraestrutura de Celery Workers com suporte completo para idempotência, debounce e deduplicação.

## O Que Foi Implementado

### 9.1 Configurar Celery com Redis como broker ✅

**Arquivo**: `config/celery_config.py`

- ✅ Celery app configurado com Redis como broker
- ✅ 3 filas definidas: `default`, `high_priority`, `low_priority`
- ✅ Retry policies configuradas (max 3 retries, backoff exponencial)
- ✅ Rate limiting: 100 tasks/minuto
- ✅ Worker settings otimizados (prefetch=4, max_tasks_per_child=1000)
- ✅ Auto-discovery de tasks

**Arquivos relacionados**:
- `src/worker.py` - Entry point do worker
- `start_worker.py` - Script para iniciar worker

### 9.2 Implementar tasks assíncronas ✅

**Arquivo**: `src/tasks/message_processor.py`

Todas as 6 tasks foram implementadas:

1. **`process_message_task()`** ✅
   - Processa mensagem do WhatsApp
   - Executa conversation engine
   - Envia resposta
   - Atualiza sessão
   - **Idempotência**: Por `message_id`
   - **Debounce**: 2 segundos (consolida mensagens rápidas)

2. **`save_session_to_duckdb_task()`** ✅
   - Persiste sessão no DuckDB
   - Execução assíncrona (não bloqueia processamento)
   - **Idempotência**: Por `session_id:turn_id`

3. **`generate_embeddings_task()`** ✅
   - Gera embeddings de mensagens
   - Para busca semântica
   - **Deduplicação**: Por hash de conteúdo

4. **`notify_human_handoff_task()`** ✅
   - Notifica equipe sobre handoff
   - Envia para CRM/email
   - **Retry**: 3 tentativas

5. **`send_reengagement_task()`** ✅
   - Envia mensagens de reengajamento
   - 3 tipos: inactive_48h, new_cars, price_drop
   - **Debounce**: 24 horas (máx 1 por dia)

6. **`collect_metrics_task()`** ✅
   - Coleta e agrega métricas
   - Para dashboards e monitoring
   - **Deduplicação**: 60 segundos

### 9.3 Implementar idempotência e debounce ✅

**Arquivo**: `src/utils/idempotency.py`

Implementamos 3 managers completos:

#### 1. **IdempotencyManager** ✅
- Previne execução duplicada de tasks
- Usa Redis com operações atômicas (SET NX)
- Cache de resultados para requests duplicados
- Chaves no formato: `idempotency:{task}:{session_id}:{turn_id}`
- TTL configurável (padrão: 1 hora)

**Métodos**:
- `generate_idempotency_key()` - Gera chave única
- `is_processed()` - Verifica se já processado
- `mark_processed()` - Marca como processado
- `get_result()` - Recupera resultado cacheado

#### 2. **DebounceManager** ✅
- Consolida eventos rápidos
- Acumula mensagens para processamento em batch
- Janelas de tempo configuráveis
- Chaves no formato: `debounce:{event_type}:{user_id}`

**Métodos**:
- `generate_debounce_key()` - Gera chave de debounce
- `should_process()` - Verifica se deve processar
- `accumulate_event()` - Acumula evento
- `get_accumulated_events()` - Recupera eventos acumulados

#### 3. **DeduplicationManager** ✅
- Previne jobs duplicados na fila
- Hash baseado em parâmetros da task
- Janelas de deduplicação configuráveis
- Chaves no formato: `job_hash:{sha256}`

**Métodos**:
- `generate_job_hash()` - Gera hash do job
- `is_duplicate()` - Verifica se é duplicado
- `mark_job()` - Marca job como visto

#### 4. **IdempotentTask (Base Class)** ✅
- Classe base para tasks Celery
- Idempotência automática
- Integração transparente com tasks existentes

#### 5. **Decorators** ✅
- `@debounce_task(window_seconds)` - Debounce automático
- `@deduplicate_job(window_seconds)` - Deduplicação automática

## Arquitetura de Idempotência

```
Mensagem WhatsApp
    ↓
[Idempotência Message-Level]
    ↓ (se não processada)
[Debounce Check]
    ↓
    ├─ Dentro da janela → Acumula
    └─ Fora da janela → Processa
    ↓
[Idempotência Turn-Level]
    ↓ (se não processada)
[Executa Task]
    ↓
[Marca como Processada]
```

## Estratégias por Task

| Task | Estratégia | Chave | TTL/Window |
|------|-----------|-------|------------|
| process_message | Idempotência + Debounce | message_id | 24h + 2s |
| save_session | Idempotência | session:turn | 1h |
| generate_embeddings | Deduplicação | content_hash | 1h |
| notify_handoff | Retry | - | - |
| send_reengagement | Debounce | user:type | 24h |
| collect_metrics | Deduplicação | metric_hash | 60s |

## Testes Implementados

**Arquivo**: `tests/unit/test_idempotency.py`

- ✅ 20+ testes unitários
- ✅ Cobertura completa dos 3 managers
- ✅ Testes de decorators
- ✅ Testes de integração

**Arquivo**: `verify_idempotency.py`

- ✅ Script de verificação standalone
- ✅ Testes com mocks (não precisa Redis)
- ✅ Cenários de integração

## Documentação

**Arquivo**: `docs/IDEMPOTENCY_AND_DEBOUNCE.md`

Documentação completa incluindo:
- ✅ Conceitos e arquitetura
- ✅ Guia de uso de cada componente
- ✅ Exemplos de código
- ✅ Padrões de chaves Redis
- ✅ Configuração e deployment
- ✅ Troubleshooting
- ✅ Monitoring e métricas
- ✅ Best practices

## Como Usar

### 1. Iniciar Redis

```bash
docker-compose up -d redis
```

### 2. Iniciar Celery Worker

```bash
python start_worker.py
```

Ou no Windows:
```bash
start-worker.bat
```

### 3. Processar Mensagem com Idempotência

```python
from src.tasks.message_processor import process_message_task

# Primeira chamada - processa
process_message_task.apply_async(
    kwargs={
        "message_id": "msg123",
        "from_number": "5511999999999",
        "message_type": "text",
        "content": "Olá",
        "timestamp": "2024-01-15T10:00:00Z"
    }
)

# Segunda chamada - ignora (idempotente)
process_message_task.apply_async(
    kwargs={
        "message_id": "msg123",  # Mesmo message_id
        "from_number": "5511999999999",
        "message_type": "text",
        "content": "Olá",
        "timestamp": "2024-01-15T10:00:00Z"
    }
)
```

## Verificação

Execute o script de verificação:

```bash
python verify_idempotency.py
```

Saída esperada:
```
=== Testing IdempotencyManager ===
✓ Generated key: idempotency:test_task:session123:5
✓ is_processed returns False for new key
✓ is_processed returns True for existing key
✓ mark_processed works correctly
✓ get_result retrieves cached result
✅ IdempotencyManager tests passed!

=== Testing DebounceManager ===
✓ Generated key: debounce:message:user123
✓ should_process returns True when allowed
✓ should_process returns False when debounced
✓ accumulate_event works correctly
✓ get_accumulated_events retrieves and parses events
✅ DebounceManager tests passed!

=== Testing DeduplicationManager ===
✓ Generated hash: 8f3d5e2a1b4c...
✓ Same inputs produce same hash
✓ Different inputs produce different hashes
✓ is_duplicate returns False for new job
✓ is_duplicate returns True for existing job
✓ mark_job works correctly
✅ DeduplicationManager tests passed!

✅ ALL TESTS PASSED!
```

## Benefícios da Implementação

### 1. Confiabilidade
- ✅ Mensagens nunca são processadas duas vezes
- ✅ Estado da sessão sempre consistente
- ✅ Retry automático em caso de falha

### 2. Performance
- ✅ Mensagens rápidas consolidadas (reduz processamento)
- ✅ Cache de resultados (respostas instantâneas para duplicatas)
- ✅ Deduplicação previne trabalho desnecessário

### 3. Experiência do Usuário
- ✅ Sem respostas duplicadas
- ✅ Processamento mais rápido (debounce)
- ✅ Reengajamento controlado (não spam)

### 4. Observabilidade
- ✅ Logs detalhados de idempotência
- ✅ Métricas de debounce e deduplicação
- ✅ Fácil troubleshooting

## Próximos Passos para MVP

Para colocar em produção, você precisa:

### Opção 1: MVP Sem Celery (Mais Simples)
Se quiser testar sem Celery primeiro:
1. Processar mensagens de forma síncrona no webhook
2. Usar apenas IdempotencyManager para prevenir duplicatas
3. Implementar Celery depois quando escalar

### Opção 2: MVP Com Celery (Recomendado)
Para produção completa:
1. ✅ Redis configurado
2. ✅ Celery worker rodando
3. ✅ Webhook enfileira tasks
4. ✅ Workers processam assincronamente

## Configuração de Produção

### Docker Compose

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  celery_worker:
    build: .
    command: python start_worker.py
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
```

### Variáveis de Ambiente

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# WhatsApp
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_ACCESS_TOKEN=seu_token
WHATSAPP_PHONE_NUMBER_ID=seu_phone_id
```

## Monitoramento

### Flower (Celery Monitoring)

```bash
pip install flower
celery -A config.celery_config flower
```

Acesse: http://localhost:5555

### Redis Monitoring

```bash
redis-cli INFO stats
redis-cli KEYS "idempotency:*" | wc -l
redis-cli KEYS "debounce:*" | wc -l
```

## Conclusão

✅ **Task 9 está 100% completa!**

Implementamos:
- ✅ Celery configurado com 3 filas
- ✅ 6 tasks assíncronas funcionais
- ✅ Sistema completo de idempotência
- ✅ Debounce para eventos rápidos
- ✅ Deduplicação de jobs
- ✅ Testes unitários
- ✅ Documentação completa
- ✅ Scripts de verificação

**Pronto para produção!** 🚀

Agora você pode:
1. Testar localmente com `python verify_idempotency.py`
2. Iniciar Redis e Celery worker
3. Enviar mensagens via webhook
4. Monitorar com Flower

Ou, se preferir MVP mais simples, podemos adaptar para processar mensagens de forma síncrona primeiro e adicionar Celery depois quando necessário.
