# Session Manager Documentation

## Overview

The SessionManager is a core component of the FacilIAuto WhatsApp chatbot that manages conversation sessions using Redis for fast access and DuckDB for persistent storage. It implements distributed locking, idempotency, and automatic expiration.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SessionManager                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │    Redis     │         │   DuckDB     │             │
│  │              │         │              │             │
│  │ - Sessions   │────────▶│ - Archived   │             │
│  │ - Locks      │  Async  │   Sessions   │             │
│  │ - Idempotency│         │ - Messages   │             │
│  └──────────────┘         └──────────────┘             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Distributed Locks (Redis SET NX)

Prevents race conditions when multiple requests try to create the same session:

```python
# Acquire lock with automatic expiration
lock_acquired = await redis.set(
    lock_key,
    "1",
    nx=True,  # Set if not exists
    ex=10     # Expire after 10 seconds
)
```

### 2. Idempotency (session_id:turn_id)

Ensures each conversation turn is processed only once:

```python
# Idempotency key format: "session_id:turn_id"
idempotency_key = f"idempotency:{session.session_id}:{session.turn_id}"

# Check if already processed
if await redis.exists(idempotency_key):
    return False  # Already processed
```

### 3. Automatic Expiration (TTL 24h)

Sessions automatically expire after 24 hours of inactivity:

```python
# Store with TTL
await redis.setex(
    session_key,
    86400,  # 24 hours
    session.model_dump_json()
)
```

### 4. Asynchronous Persistence

Sessions are persisted to DuckDB asynchronously to avoid blocking:

```python
# Schedule background task
asyncio.create_task(self._save_to_duckdb_async(session))
```

## Data Models

### SessionData

Main session model with typed fields:

```python
class SessionData(BaseModel):
    session_id: str              # Format: "phone:timestamp"
    phone_number: str            # International format
    state: SessionState          # Current conversation state
    turn_id: int                 # Idempotency counter
    memory: ConversationMemory   # Message history
    user_profile: UserProfileData # User information
    current_recommendations: List[str]
    created_at: datetime
    updated_at: datetime
    ttl_seconds: int = 86400
    consent_given: bool
    consent_timestamp: Optional[datetime]
```

### UserProfileData

User profile with automatic score calculation:

```python
class UserProfileData(BaseModel):
    # Budget
    orcamento_min: Optional[float]
    orcamento_max: Optional[float]
    
    # Usage and location
    uso_principal: Optional[str]
    city: Optional[str]
    state: Optional[str]
    
    # Preferences
    prioridades: Dict[str, int]
    marcas_preferidas: List[str]
    tipos_preferidos: List[str]
    
    # Engagement
    urgencia: Optional[str]
    interacoes_count: int
    
    # Computed properties
    @computed_field
    @property
    def completeness(self) -> float:
        """Profile completeness (0.0 to 1.0)"""
        
    @computed_field
    @property
    def qualification_score(self) -> float:
        """Lead qualification score (0 to 100)"""
```

### ConversationMemory

Conversation history with validation:

```python
class ConversationMemory(BaseModel):
    messages: List[Dict[str, str]]  # role, content, timestamp
    summary: str                     # Incremental summary
    last_updated: datetime
    
    def add_message(self, role: str, content: str) -> None:
        """Add message to history"""
        
    def get_recent_messages(self, n: int = 5) -> List[Dict]:
        """Get N most recent messages"""
```

## Usage Examples

### Basic Usage

```python
import redis.asyncio as redis
from src.services.session_manager import SessionManager

# Initialize
redis_client = redis.Redis(host="localhost", port=6379)
manager = SessionManager(redis_client)

# Create or get session
session = await manager.get_or_create_session("+5511999999999")

# Add message
session.add_message("user", "Olá!")
session.add_message("assistant", "Olá! Como posso ajudar?")

# Update session
await manager.update_session(session)

# Get session
session = await manager.get_session("+5511999999999")

# Expire session
await manager.expire_session("+5511999999999")
```

### Profile Management

```python
# Collect user data
session.user_profile.orcamento_min = 50000
session.user_profile.orcamento_max = 80000
session.user_profile.uso_principal = "trabalho"
session.user_profile.city = "São Paulo"
session.user_profile.prioridades = {
    "economia": 5,
    "conforto": 4,
    "seguranca": 5
}

# Check completeness
print(f"Profile: {session.user_profile.completeness * 100}% complete")
print(f"Score: {session.user_profile.qualification_score}/100")

# Update session
await manager.update_session(session)
```

### LGPD Consent

```python
# Check consent
if not session.consent_given:
    # Request consent from user
    session.give_consent()
    await manager.update_session(session)

# Consent is now recorded with timestamp
print(f"Consent given at: {session.consent_timestamp}")
```

### User History

```python
# Get previous sessions
history = await manager.get_user_history("+5511999999999", limit=5)

for session_info in history:
    print(f"Session: {session_info['session_id']}")
    print(f"Score: {session_info['qualification_score']}")
    print(f"Updated: {session_info['updated_at']}")
```

## Qualification Scoring

The system automatically calculates a lead qualification score (0-100) based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Budget defined | 30% | Has min/max budget set |
| Urgency | 25% | Purchase timeline (immediate, 1-3 months, etc) |
| Clear preferences | 25% | Has priorities, usage, brands defined |
| Engagement | 20% | Number of interactions (messages) |

### Score Interpretation

- **High (≥60)**: Qualified lead, forward to dealership
- **Medium (40-59)**: Nurture with content, re-engage in 7 days
- **Low (<40)**: Early stage, continue qualification

## Profile Completeness

Completeness is calculated based on:

| Field | Weight | Description |
|-------|--------|-------------|
| Budget | 25% | Min and max budget defined |
| Usage | 25% | Primary vehicle usage |
| Location | 20% | City and state |
| Priorities | 30% | At least 3 priorities defined |

## DuckDB Schema

### archived_sessions

```sql
CREATE TABLE archived_sessions (
    session_id VARCHAR PRIMARY KEY,
    phone_number VARCHAR NOT NULL,
    state VARCHAR NOT NULL,
    turn_id INTEGER NOT NULL,
    user_profile JSON,
    memory_summary TEXT,
    qualification_score DOUBLE,
    completeness DOUBLE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### message_history

```sql
CREATE TABLE message_history (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (session_id) REFERENCES archived_sessions(session_id)
)
```

## Performance Considerations

### Redis Operations

- **Session retrieval**: O(1) - Direct key lookup
- **Lock acquisition**: O(1) - SET NX operation
- **Idempotency check**: O(1) - EXISTS operation

### DuckDB Operations

- **Session archive**: Async, non-blocking
- **History queries**: Indexed by phone_number and updated_at
- **Message queries**: Indexed by session_id

### Scalability

- Redis handles 100,000+ ops/sec
- DuckDB provides cheap analytical queries
- Async persistence prevents blocking
- Horizontal scaling via Redis Cluster

## Error Handling

The SessionManager handles various error scenarios:

```python
try:
    session = await manager.get_or_create_session(phone)
except redis.RedisError as e:
    logger.error(f"Redis error: {e}")
    # Fallback to DuckDB or return cached session
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Return default session or raise
```

## Testing

Run tests with:

```bash
pytest tests/test_session_manager.py -v
```

Key test scenarios:
- Session creation and retrieval
- Concurrent session creation (locks)
- Idempotent updates
- Profile completeness calculation
- Qualification score calculation
- Session expiration
- Message management
- LGPD consent

## Integration with Other Components

### NLP Service

```python
# After NLP processing
nlp_result = await nlp_service.process(message)
session.add_message("user", message)

# Extract entities and update profile
for entity in nlp_result.entities:
    if entity.type == "budget":
        session.user_profile.orcamento_min = entity.value * 0.8
        session.user_profile.orcamento_max = entity.value * 1.2

await manager.update_session(session)
```

### Conversation Engine

```python
# Get session
session = await manager.get_or_create_session(phone)

# Process conversation
response = await conversation_engine.process(session, message)

# Update session
session.add_message("assistant", response)
await manager.update_session(session)
```

### Celery Tasks

```python
# In production, use Celery for async persistence
from celery import shared_task

@shared_task
def save_session_to_duckdb(session_dict):
    """Save session to DuckDB asynchronously"""
    session = SessionData(**session_dict)
    # Save to DuckDB
```

## Configuration

Environment variables:

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# DuckDB
DUCKDB_PATH=data/chatbot_context.duckdb

# Session
SESSION_TTL_SECONDS=86400  # 24 hours
LOCK_TIMEOUT_SECONDS=10
IDEMPOTENCY_TTL_SECONDS=3600  # 1 hour
```

## Monitoring

Key metrics to monitor:

- Session creation rate
- Session retrieval latency
- Lock contention rate
- Idempotency rejection rate
- DuckDB write latency
- Redis memory usage
- Session expiration rate

## Future Enhancements

1. **Celery Integration**: Move DuckDB persistence to Celery tasks
2. **Redis Cluster**: Support for horizontal scaling
3. **Session Migration**: Hot migration between Redis instances
4. **Advanced Analytics**: ML-based qualification scoring
5. **Multi-language**: Support for multiple languages
6. **Session Replay**: Replay conversations for debugging
7. **A/B Testing**: Track different conversation flows

## References

- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Redis Distributed Locks](https://redis.io/docs/manual/patterns/distributed-locks/)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [LGPD Compliance](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)
