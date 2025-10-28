# Idempotency and Debounce Implementation

## Overview

This document describes the idempotency and debounce mechanisms implemented for Celery tasks in the FacilIAuto WhatsApp chatbot. These mechanisms ensure reliable message processing, prevent duplicate operations, and optimize resource usage.

## Key Concepts

### Idempotency

**Definition**: An operation is idempotent if executing it multiple times produces the same result as executing it once.

**Why it matters**: In distributed systems, network failures, retries, and race conditions can cause the same task to be executed multiple times. Idempotency ensures that duplicate executions don't cause problems.

**Implementation**: We use Redis with atomic operations (SET NX) to track which tasks have been processed.

### Debounce

**Definition**: Debouncing consolidates multiple rapid events into a single operation.

**Why it matters**: Users may send multiple messages quickly (e.g., typing corrections). Processing each message separately wastes resources and creates a poor user experience.

**Implementation**: We use Redis with time-based windows to detect and consolidate rapid events.

### Deduplication

**Definition**: Preventing the same job from being queued multiple times.

**Why it matters**: Multiple webhook deliveries or system retries can queue identical jobs. Deduplication prevents wasted processing.

**Implementation**: We generate a hash of task parameters and use Redis to track recent jobs.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Incoming Message                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Message-Level Idempotency Check                 │
│         Key: idempotency:message:{message_id}                │
│         TTL: 24 hours                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Debounce Check                             │
│         Key: debounce:message:{user_id}                      │
│         Window: 2 seconds                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─── Within window ───┐
                         │                      │
                         ▼                      ▼
                   Process Now          Accumulate Event
                         │                      │
                         │                      ▼
                         │              Wait for window
                         │                      │
                         │                      ▼
                         │              Consolidate Messages
                         │                      │
                         └──────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────┐
│              Turn-Level Idempotency Check                    │
│         Key: idempotency:{task}:{session_id}:{turn_id}       │
│         TTL: 1 hour                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                   Execute Task
                         │
                         ▼
                   Mark as Processed
```

## Components

### 1. IdempotencyManager

Manages task-level idempotency using Redis.

**Key Methods**:
- `generate_idempotency_key(session_id, turn_id, task_name)`: Generate unique key
- `is_processed(key)`: Check if task was already processed
- `mark_processed(key, result, ttl)`: Mark task as processed
- `get_result(key)`: Retrieve cached result

**Usage Example**:
```python
from src.utils.idempotency import IdempotencyManager

manager = IdempotencyManager()

# Generate key
key = manager.generate_idempotency_key(
    session_id="session123",
    turn_id=5,
    task_name="process_message"
)

# Check if processed
if manager.is_processed(key):
    result = manager.get_result(key)
    return result

# Process task
result = do_work()

# Mark as processed
manager.mark_processed(key, result, ttl=3600)
```

### 2. DebounceManager

Manages event debouncing and accumulation.

**Key Methods**:
- `generate_debounce_key(user_id, event_type)`: Generate debounce key
- `should_process(key, window_seconds)`: Check if event should be processed
- `accumulate_event(key, data, ttl)`: Accumulate event for batch processing
- `get_accumulated_events(key, clear)`: Retrieve accumulated events

**Usage Example**:
```python
from src.utils.idempotency import DebounceManager

manager = DebounceManager()

# Check if should process
key = manager.generate_debounce_key(
    user_id="user123",
    event_type="message"
)

if not manager.should_process(key, window_seconds=2):
    # Accumulate for later
    count = manager.accumulate_event(
        f"accumulator:messages:{user_id}",
        {"message": "Hello"},
        ttl=5
    )
    
    # Process batch if threshold reached
    if count >= 3:
        events = manager.get_accumulated_events(
            f"accumulator:messages:{user_id}",
            clear=True
        )
        process_batch(events)
```

### 3. DeduplicationManager

Prevents duplicate job execution.

**Key Methods**:
- `generate_job_hash(task_name, args, kwargs)`: Generate job hash
- `is_duplicate(hash, window_seconds)`: Check if job is duplicate
- `mark_job(hash, window_seconds)`: Mark job as seen

**Usage Example**:
```python
from src.utils.idempotency import DeduplicationManager

manager = DeduplicationManager()

# Generate hash
job_hash = manager.generate_job_hash(
    task_name="generate_embeddings",
    args=(),
    kwargs={"message_id": "msg123", "text": "Hello"}
)

# Check for duplicate
if manager.is_duplicate(job_hash, window_seconds=3600):
    return {"status": "duplicate"}

# Mark job
manager.mark_job(job_hash, window_seconds=3600)

# Execute job
result = do_work()
```

### 4. IdempotentTask Base Class

Celery task base class with automatic idempotency.

**Features**:
- Automatically generates idempotency keys from `session_id` and `turn_id`
- Checks for processed tasks before execution
- Caches results for duplicate requests
- Marks tasks as processed after execution

**Usage Example**:
```python
from config.celery_config import celery_app
from src.utils.idempotency import IdempotentTask

@celery_app.task(
    bind=True,
    base=IdempotentTask,
    name="my_task"
)
def my_task(self, session_id: str, turn_id: int, data: dict):
    # Task automatically handles idempotency
    return process_data(data)

# Call with session_id and turn_id for automatic idempotency
my_task.apply_async(
    kwargs={
        "session_id": "session123",
        "turn_id": 5,
        "data": {"key": "value"}
    }
)
```

## Task-Specific Implementations

### process_message_task

**Idempotency Strategy**: Message-level + Turn-level
- **Message-level**: Uses `message_id` to prevent duplicate processing of the same WhatsApp message
- **Turn-level**: Uses `session_id:turn_id` for conversation state updates

**Debounce Strategy**: 2-second window
- Consolidates rapid messages from the same user
- Accumulates up to 3 messages before processing
- Joins accumulated messages into single context

**Key**: `idempotency:message:{message_id}`
**TTL**: 24 hours

### save_session_to_duckdb_task

**Idempotency Strategy**: Turn-level
- Uses `session_id:turn_id` to prevent duplicate persistence
- Ensures each conversation turn is saved exactly once

**Key**: `idempotency:save_session_to_duckdb:{session_id}:{turn_id}`
**TTL**: 1 hour

### generate_embeddings_task

**Deduplication Strategy**: Content-based
- Generates hash from `message_id` and `text`
- Prevents generating embeddings for the same content multiple times

**Window**: 1 hour

### send_reengagement_task

**Debounce Strategy**: 24-hour window
- Prevents sending multiple reengagement messages to the same user
- Separate debounce keys for different message types

**Key**: `debounce:reengagement_{message_type}:{user_id}`
**Window**: 24 hours

### collect_metrics_task

**Deduplication Strategy**: Parameter-based
- Generates hash from `metric_type` and `data`
- Prevents collecting duplicate metrics within 60 seconds

**Window**: 60 seconds

## Redis Key Patterns

### Idempotency Keys
```
idempotency:message:{message_id}
idempotency:{task_name}:{session_id}:{turn_id}
```

### Debounce Keys
```
debounce:{event_type}:{user_id}
```

### Accumulator Keys
```
accumulator:messages:{user_id}
```

### Job Hash Keys
```
job_hash:{sha256_hash}
```

## Configuration

### Redis Settings

```python
# config/settings.py
REDIS_URL = "redis://localhost:6379/0"
```

### Celery Settings

```python
# config/celery_config.py
task_acks_late = True  # Acknowledge after task completion
task_reject_on_worker_lost = True  # Reject on worker failure
task_track_started = True  # Track task start time
```

## Testing

### Unit Tests

Run unit tests for idempotency utilities:

```bash
pytest tests/unit/test_idempotency.py -v
```

### Integration Tests

Test idempotency in real scenarios:

```bash
# Start Redis
docker-compose up -d redis

# Start Celery worker
python start_worker.py

# Run integration tests
pytest tests/integration/test_task_idempotency.py -v
```

### Manual Testing

Test message-level idempotency:

```bash
# Send duplicate webhook
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "id": "msg123",
            "from": "5511999999999",
            "text": {"body": "Hello"}
          }]
        }
      }]
    }]
  }'

# Send again - should be deduplicated
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "id": "msg123",
            "from": "5511999999999",
            "text": {"body": "Hello"}
          }]
        }
      }]
    }]
  }'
```

## Monitoring

### Redis Metrics

Monitor Redis key usage:

```bash
# Count idempotency keys
redis-cli KEYS "idempotency:*" | wc -l

# Count debounce keys
redis-cli KEYS "debounce:*" | wc -l

# Check memory usage
redis-cli INFO memory
```

### Celery Metrics

Monitor task execution:

```python
from prometheus_client import Counter, Histogram

# Idempotency hits
idempotency_hits = Counter(
    'celery_task_idempotency_hits_total',
    'Number of idempotent task hits',
    ['task_name']
)

# Debounce events
debounce_events = Counter(
    'celery_task_debounce_events_total',
    'Number of debounced events',
    ['event_type']
)

# Deduplication hits
deduplication_hits = Counter(
    'celery_task_deduplication_hits_total',
    'Number of deduplicated jobs',
    ['task_name']
)
```

## Best Practices

### 1. Choose Appropriate TTLs

- **Message-level idempotency**: 24 hours (WhatsApp message retention)
- **Turn-level idempotency**: 1 hour (session updates)
- **Debounce windows**: 2-5 seconds (user typing speed)
- **Deduplication windows**: 1 hour (typical retry intervals)

### 2. Use Atomic Operations

Always use Redis atomic operations (SET NX, RPUSH, etc.) to prevent race conditions.

### 3. Handle Edge Cases

- Network failures during Redis operations
- Redis unavailability (fallback to processing)
- Clock skew between servers

### 4. Monitor Key Growth

Set up alerts for excessive key growth:

```python
# Alert if idempotency keys exceed threshold
if redis.dbsize() > 1000000:
    alert("Redis key count exceeds threshold")
```

### 5. Clean Up Expired Keys

Redis automatically removes expired keys, but monitor memory usage:

```bash
# Check expired keys
redis-cli INFO stats | grep expired_keys
```

## Troubleshooting

### Issue: Tasks not being deduplicated

**Symptoms**: Same task executes multiple times

**Diagnosis**:
```bash
# Check if idempotency keys exist
redis-cli GET "idempotency:message:msg123"

# Check Celery logs
tail -f celery.log | grep "already processed"
```

**Solutions**:
- Verify Redis connectivity
- Check TTL values
- Ensure `session_id` and `turn_id` are passed correctly

### Issue: Messages being over-debounced

**Symptoms**: User messages not being processed

**Diagnosis**:
```bash
# Check debounce keys
redis-cli KEYS "debounce:*"

# Check accumulator
redis-cli LRANGE "accumulator:messages:user123" 0 -1
```

**Solutions**:
- Reduce debounce window
- Lower accumulation threshold
- Check for stuck accumulators

### Issue: High Redis memory usage

**Symptoms**: Redis memory growing continuously

**Diagnosis**:
```bash
# Check memory usage
redis-cli INFO memory

# Check key count by pattern
redis-cli --scan --pattern "idempotency:*" | wc -l
```

**Solutions**:
- Reduce TTL values
- Implement key eviction policy
- Scale Redis vertically or horizontally

## Performance Considerations

### Redis Operations

- **SET NX**: O(1) - Very fast
- **GET**: O(1) - Very fast
- **RPUSH**: O(1) - Very fast
- **LRANGE**: O(N) - Fast for small lists

### Overhead

- **Idempotency check**: ~1-2ms per task
- **Debounce check**: ~1-2ms per event
- **Deduplication check**: ~2-3ms per job (includes hashing)

### Optimization Tips

1. Use Redis pipelining for multiple operations
2. Set appropriate TTLs to limit key growth
3. Use Redis Cluster for horizontal scaling
4. Monitor and tune Redis configuration

## References

- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/tasks.html#tips-and-best-practices)
- [Redis Atomic Operations](https://redis.io/commands/set)
- [Idempotency Patterns](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- [Debouncing and Throttling](https://css-tricks.com/debouncing-throttling-explained-examples/)
