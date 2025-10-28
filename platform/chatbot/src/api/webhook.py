"""WhatsApp webhook endpoints."""

import hashlib
import hmac
import json
import logging
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

router = APIRouter()


class WhatsAppMessage(BaseModel):
    """WhatsApp message model."""

    message_id: str = Field(..., alias="id")
    from_number: str = Field(..., alias="from")
    timestamp: str
    type: str
    text: Dict[str, Any] | None = None
    image: Dict[str, Any] | None = None
    audio: Dict[str, Any] | None = None
    document: Dict[str, Any] | None = None
    location: Dict[str, Any] | None = None

    class Config:
        populate_by_name = True


class WebhookPayload(BaseModel):
    """WhatsApp webhook payload model."""

    object: str
    entry: list[Dict[str, Any]]


def verify_webhook_signature(payload: bytes, signature: str | None) -> bool:
    """
    Verify webhook signature from Meta.

    Args:
        payload: Raw request body
        signature: X-Hub-Signature-256 header value

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature:
        logger.warning("Missing X-Hub-Signature-256 header")
        return False

    # Extract signature (format: sha256=<signature>)
    if not signature.startswith("sha256="):
        logger.warning("Invalid signature format")
        return False

    expected_signature = signature[7:]  # Remove 'sha256=' prefix

    # Calculate HMAC
    secret = settings.whatsapp_webhook_secret.encode("utf-8")
    calculated_signature = hmac.new(
        secret, payload, hashlib.sha256
    ).hexdigest()

    # Compare signatures (constant-time comparison)
    is_valid = hmac.compare_digest(calculated_signature, expected_signature)

    if not is_valid:
        logger.warning("Invalid webhook signature")

    return is_valid


async def is_duplicate_message(message_id: str) -> bool:
    """
    Check if message has already been processed.

    Args:
        message_id: WhatsApp message ID

    Returns:
        True if message is duplicate, False otherwise
    """
    # TODO: Implement Redis-based deduplication
    # For now, return False (no deduplication)
    from src.services.redis_client import get_redis_client

    redis = await get_redis_client()
    if redis is None:
        logger.warning("Redis not available, skipping deduplication")
        return False

    # Check if message_id exists in Redis
    key = f"msg_processed:{message_id}"
    exists = await redis.exists(key)

    if exists:
        logger.info(f"Duplicate message detected: {message_id}")
        return True

    # Mark message as processed (TTL: 24 hours)
    await redis.setex(key, 86400, "1")
    return False


@router.get("/whatsapp")
async def verify_webhook(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None,
) -> Response:
    """
    Webhook verification endpoint for Meta.

    Meta sends a GET request to verify the webhook URL.
    We must return the hub.challenge value if the verify token matches.

    Args:
        hub_mode: Should be "subscribe"
        hub_challenge: Challenge string to return
        hub_verify_token: Verification token to validate

    Returns:
        Plain text response with challenge value
    """
    logger.info(
        f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}"
    )

    # Validate parameters
    if not all([hub_mode, hub_challenge, hub_verify_token]):
        logger.error("Missing required parameters for webhook verification")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required parameters",
        )

    # Verify token
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        logger.info("Webhook verification successful")
        return Response(content=hub_challenge, media_type="text/plain")

    logger.error(f"Invalid verify token: {hub_verify_token}")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid verify token",
    )


@router.post("/whatsapp")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256"),
) -> Dict[str, str]:
    """
    Receive webhook notifications from WhatsApp.

    This endpoint receives messages, status updates, and other events
    from WhatsApp Business API.

    Args:
        request: FastAPI request object
        x_hub_signature_256: Signature header for verification

    Returns:
        Success response
    """
    # Read raw body for signature verification
    body = await request.body()

    # Verify signature
    if not verify_webhook_signature(body, x_hub_signature_256):
        logger.error("Webhook signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    # Parse JSON payload
    try:
        payload_dict = json.loads(body)
        payload = WebhookPayload(**payload_dict)
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload format",
        )

    logger.info(f"Received webhook: object={payload.object}")

    # Process webhook entries
    if payload.object == "whatsapp_business_account":
        for entry in payload.entry:
            # Extract changes
            changes = entry.get("changes", [])

            for change in changes:
                field = change.get("field")
                value = change.get("value", {})

                if field == "messages":
                    # Process incoming messages
                    messages = value.get("messages", [])

                    for msg_data in messages:
                        try:
                            message = WhatsAppMessage(**msg_data)

                            # Check for duplicates
                            if await is_duplicate_message(message.message_id):
                                logger.info(
                                    f"Skipping duplicate message: {message.message_id}"
                                )
                                continue

                            # Queue message for async processing
                            await queue_message_processing(message)

                        except Exception as e:
                            logger.error(f"Failed to process message: {e}")
                            # Continue processing other messages

                elif field == "message_status":
                    # Handle message status updates (sent, delivered, read, failed)
                    statuses = value.get("statuses", [])
                    for status_data in statuses:
                        logger.info(f"Message status update: {status_data}")
                        # TODO: Update message status in database

    # Return 200 OK immediately
    return {"status": "ok"}


async def queue_message_processing(message: WhatsAppMessage) -> None:
    """
    Queue message for asynchronous processing via Celery.

    This function extracts the message content and queues it for
    processing by Celery workers. The webhook returns 200 OK immediately
    while processing happens in the background.

    Args:
        message: WhatsApp message to process
    """
    logger.info(
        f"Queuing message for processing: {message.message_id} from {message.from_number}"
    )

    # Extract message content based on type
    content = None
    media_id = None
    media_url = None

    if message.type == "text" and message.text:
        content = message.text.get("body", "")
    elif message.type == "image" and message.image:
        media_id = message.image.get("id")
        media_url = message.image.get("link")
        content = message.image.get("caption", "[Image]")
    elif message.type == "audio" and message.audio:
        media_id = message.audio.get("id")
        content = "[Audio message]"
    elif message.type == "document" and message.document:
        media_id = message.document.get("id")
        content = f"[Document: {message.document.get('filename', 'unknown')}]"
    elif message.type == "location" and message.location:
        lat = message.location.get("latitude")
        lon = message.location.get("longitude")
        content = f"[Location: {lat}, {lon}]"
    else:
        content = f"[Unsupported message type: {message.type}]"

    logger.info(f"Message content: {content}")

    # Prepare message data for Celery task
    message_data = {
        "message_id": message.message_id,
        "from_number": message.from_number,
        "message_type": message.type,
        "content": content,
        "timestamp": message.timestamp,
        "media_id": media_id,
        "media_url": media_url,
    }

    # Queue for Celery processing
    try:
        from src.tasks.message_processor import process_message_task

        # Use apply_async for better control
        task = process_message_task.apply_async(
            kwargs=message_data,
            queue="default",
            priority=5,  # Medium priority
        )
        logger.info(
            f"Message {message.message_id} queued successfully (task_id: {task.id})"
        )
    except Exception as e:
        logger.error(f"Failed to queue message: {e}", exc_info=True)
        # Don't raise exception - we already returned 200 OK to WhatsApp
        # The message will be lost, but we avoid blocking the webhook
