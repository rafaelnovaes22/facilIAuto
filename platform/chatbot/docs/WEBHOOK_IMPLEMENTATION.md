# Webhook Handler Implementation

## Overview

This document describes the implementation of the WhatsApp webhook handler (Task 8) for the FacilIAuto chatbot. The webhook handler is responsible for receiving messages from WhatsApp Business API, validating them, and queuing them for asynchronous processing.

## Architecture

```
WhatsApp Business API
        ↓
    Webhook POST
        ↓
  Signature Validation
        ↓
  Message Deduplication
        ↓
  Queue for Processing (Celery)
        ↓
    Return 200 OK
```

## Components

### 1. Webhook Endpoints (`src/api/webhook.py`)

#### GET /webhook/whatsapp
- **Purpose**: Webhook verification by Meta
- **Parameters**:
  - `hub.mode`: Should be "subscribe"
  - `hub.challenge`: Challenge string to return
  - `hub.verify_token`: Token to validate
- **Response**: Plain text with challenge value

#### POST /webhook/whatsapp
- **Purpose**: Receive messages and events from WhatsApp
- **Headers**:
  - `X-Hub-Signature-256`: HMAC signature for validation
- **Body**: JSON payload with messages and events
- **Response**: `{"status": "ok"}`

### 2. Signature Verification

The webhook validates all incoming requests using HMAC-SHA256:

```python
def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature from Meta."""
    secret = settings.whatsapp_webhook_secret.encode("utf-8")
    calculated_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(calculated_signature, expected_signature)
```

**Security Features**:
- Constant-time comparison to prevent timing attacks
- Validates signature format (must start with "sha256=")
- Rejects requests with missing or invalid signatures

### 3. Message Deduplication

Messages are deduplicated using Redis to prevent duplicate processing:

```python
async def is_duplicate_message(message_id: str) -> bool:
    """Check if message has already been processed."""
    key = f"msg_processed:{message_id}"
    exists = await redis.exists(key)
    
    if exists:
        return True
    
    # Mark as processed (TTL: 24 hours)
    await redis.setex(key, 86400, "1")
    return False
```

**Features**:
- 24-hour TTL for processed message IDs
- Redis-based for distributed systems
- Graceful fallback if Redis unavailable

### 4. Asynchronous Processing

Messages are queued for processing via Celery:

```python
async def queue_message_processing(message: WhatsAppMessage) -> None:
    """Queue message for asynchronous processing."""
    message_data = {
        "message_id": message.message_id,
        "from_number": message.from_number,
        "message_type": message.type,
        "content": content,
        "timestamp": message.timestamp,
    }
    
    # Queue for Celery (Task 9)
    process_message_task.delay(**message_data)
```

**Supported Message Types**:
- Text messages
- Image messages (with caption)
- Audio messages
- Document messages
- Location messages

### 5. WhatsApp Client (`src/services/whatsapp_client.py`)

The WhatsApp client provides methods for sending messages:

#### send_text_message()
```python
await client.send_text_message(
    to="5511999999999",
    text="Olá! Bem-vindo ao FacilIAuto!",
    preview_url=False
)
```

#### send_image_message()
```python
await client.send_image_message(
    to="5511999999999",
    image_url="https://example.com/car.jpg",
    caption="Honda Civic 2023"
)
```

#### send_template_message()
```python
await client.send_template_message(
    to="5511999999999",
    template_name="welcome_message",
    components=[...]
)
```

#### send_interactive_message()
```python
await client.send_interactive_message(
    to="5511999999999",
    body_text="Escolha uma opção:",
    buttons=[
        {"id": "opt1", "title": "Ver carros"},
        {"id": "opt2", "title": "Falar com vendedor"}
    ]
)
```

**Features**:
- Automatic retry with exponential backoff (3 attempts)
- Timeout handling (30 seconds)
- Input validation (text length, URL format, etc)
- Comprehensive error logging

## Configuration

Required environment variables in `.env`:

```bash
# WhatsApp Business API
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_VERIFY_TOKEN=faciliauto_webhook_2024
WHATSAPP_WEBHOOK_SECRET=your_app_secret

# Redis
REDIS_URL=redis://localhost:6379/0
```

## Testing

### Unit Tests

Run webhook tests:
```bash
pytest tests/test_webhook.py -v
```

Run WhatsApp client tests:
```bash
pytest tests/test_whatsapp_client.py -v
```

### Manual Testing

1. **Verify webhook**:
```bash
curl "http://localhost:8000/webhook/whatsapp?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=faciliauto_webhook_2024"
```

2. **Send test message** (requires valid signature):
```bash
python scripts/test_whatsapp_webhook.py
```

3. **Test message sending**:
```bash
python scripts/test_whatsapp_send.py
```

## Error Handling

### Webhook Errors

| Error | Status Code | Description |
|-------|-------------|-------------|
| Invalid signature | 401 | Signature verification failed |
| Missing signature | 401 | X-Hub-Signature-256 header missing |
| Invalid payload | 400 | JSON parsing failed |
| Invalid verify token | 403 | Webhook verification failed |

### Client Errors

| Error | Retry | Description |
|-------|-------|-------------|
| Timeout | Yes (3x) | Request timeout after 30s |
| Network error | Yes (3x) | Connection failed |
| HTTP 4xx | No | Client error (invalid request) |
| HTTP 5xx | Yes (3x) | Server error |

## Performance

- **Webhook response time**: < 100ms (returns 200 OK immediately)
- **Message processing**: Asynchronous via Celery
- **Deduplication overhead**: < 5ms (Redis lookup)
- **Signature verification**: < 1ms

## Security

1. **Signature Verification**: All webhooks validated with HMAC-SHA256
2. **Constant-time Comparison**: Prevents timing attacks
3. **HTTPS Only**: Image URLs must use HTTPS
4. **Rate Limiting**: Handled by API Gateway (Kong)
5. **Input Validation**: All inputs validated with Pydantic

## Monitoring

Metrics exposed at `/metrics`:

- `whatsapp_messages_received_total`: Total messages received
- `whatsapp_messages_sent_total`: Total messages sent
- `whatsapp_webhook_errors_total`: Total webhook errors
- `whatsapp_signature_failures_total`: Signature validation failures
- `whatsapp_duplicate_messages_total`: Duplicate messages detected

## Next Steps

1. **Task 9**: Implement Celery workers for message processing
2. **Task 10**: Implement lead qualification system
3. **Task 11**: Implement notification system

## References

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Webhook Security](https://developers.facebook.com/docs/graph-api/webhooks/getting-started#verification-requests)
- [Message Types](https://developers.facebook.com/docs/whatsapp/cloud-api/messages)
