# Webhook Quick Start Guide

## Setup

### 1. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your WhatsApp credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_ACCESS_TOKEN=your_permanent_access_token
WHATSAPP_VERIFY_TOKEN=faciliauto_webhook_2024
WHATSAPP_WEBHOOK_SECRET=your_app_secret_here
REDIS_URL=redis://localhost:6379/0
```

### 2. Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or using Docker Compose
docker-compose up -d redis
```

### 3. Start the Application

```bash
# Install dependencies
poetry install

# Run the server
poetry run uvicorn src.main:app --reload --port 8000
```

## Configure WhatsApp Webhook

### 1. Expose Local Server (Development)

Use ngrok to expose your local server:

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 2. Configure in Meta Developer Console

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Select your app
3. Go to WhatsApp > Configuration
4. Click "Edit" next to Webhook
5. Enter:
   - **Callback URL**: `https://your-domain.com/webhook/whatsapp`
   - **Verify Token**: `faciliauto_webhook_2024` (from your .env)
6. Click "Verify and Save"

### 3. Subscribe to Webhook Fields

Subscribe to these fields:
- ✅ messages
- ✅ message_status (optional)

## Test the Webhook

### Test Verification Endpoint

```bash
curl "http://localhost:8000/webhook/whatsapp?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=faciliauto_webhook_2024"
```

Expected response: `test123`

### Test Message Receiving

Send a message to your WhatsApp Business number. Check the logs:

```bash
# You should see:
INFO: Received webhook: object=whatsapp_business_account
INFO: Queuing message for processing: wamid.xxx from 5511999999999
INFO: Message content: Olá, quero comprar um carro
```

### Test Message Sending

```python
from src.services.whatsapp_client import get_whatsapp_client

# Get client
client = await get_whatsapp_client()

# Send text message
await client.send_text_message(
    to="5511999999999",  # Recipient number
    text="Olá! Bem-vindo ao FacilIAuto! 🚗"
)

# Send image
await client.send_image_message(
    to="5511999999999",
    image_url="https://example.com/car.jpg",
    caption="Honda Civic 2023"
)

# Send interactive message
await client.send_interactive_message(
    to="5511999999999",
    body_text="Como posso ajudar?",
    buttons=[
        {"id": "cars", "title": "Ver carros"},
        {"id": "help", "title": "Ajuda"}
    ]
)
```

## Verify Setup

Run the verification script:

```bash
python scripts/verify_setup.py
```

This checks:
- ✅ Environment variables configured
- ✅ Redis connection working
- ✅ WhatsApp API credentials valid
- ✅ Webhook endpoints responding

## Common Issues

### Issue: "Invalid signature"

**Cause**: `WHATSAPP_WEBHOOK_SECRET` doesn't match your app secret

**Solution**: 
1. Go to Meta Developer Console
2. Settings > Basic
3. Copy "App Secret"
4. Update `WHATSAPP_WEBHOOK_SECRET` in `.env`

### Issue: "Redis connection failed"

**Cause**: Redis not running

**Solution**:
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### Issue: "Webhook verification failed"

**Cause**: `WHATSAPP_VERIFY_TOKEN` doesn't match

**Solution**: Ensure the token in `.env` matches what you entered in Meta console

### Issue: "Message not received"

**Cause**: Webhook not subscribed to messages field

**Solution**:
1. Go to WhatsApp > Configuration
2. Click "Manage" next to Webhook
3. Ensure "messages" is checked

## Monitoring

### Check Health

```bash
curl http://localhost:8000/health
```

### Check Readiness

```bash
curl http://localhost:8000/ready
```

### View Metrics

```bash
curl http://localhost:8000/metrics
```

### View Logs

```bash
# Follow logs
tail -f logs/chatbot.log

# Search for errors
grep ERROR logs/chatbot.log
```

## Next Steps

1. ✅ Webhook receiving messages
2. 🔄 Implement Celery workers (Task 9)
3. 🔄 Integrate with Conversation Engine
4. 🔄 Test end-to-end flow

## Support

For issues or questions:
- Check logs: `logs/chatbot.log`
- Run diagnostics: `python scripts/verify_setup.py`
- Review documentation: `docs/WEBHOOK_IMPLEMENTATION.md`
