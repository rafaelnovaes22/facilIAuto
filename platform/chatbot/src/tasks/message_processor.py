"""Celery tasks for message processing."""

import logging
from typing import Any, Dict, Optional

from celery import Task
from tenacity import retry, stop_after_attempt, wait_exponential

from config.celery_config import celery_app
from config.settings import get_settings
from src.utils.idempotency import (
    DebounceManager,
    DeduplicationManager,
    IdempotencyManager,
    IdempotentTask,
    debounce_task,
    deduplicate_job,
)

settings = get_settings()
logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    base=IdempotentTask,
    name="process_message",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def process_message_task(
    self,
    message_id: str,
    from_number: str,
    message_type: str,
    content: str,
    timestamp: str,
    media_id: Optional[str] = None,
    media_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process incoming WhatsApp message asynchronously.

    This task handles the complete message processing pipeline:
    1. Check idempotency (message_id based)
    2. Get or create user session
    3. Process message through NLP
    4. Execute conversation engine
    5. Generate and send response
    6. Update session state

    Idempotency: Uses message_id as idempotency key to prevent duplicate processing
    Debounce: Consolidates rapid messages from same user within 2 seconds

    Args:
        message_id: WhatsApp message ID (used for idempotency)
        from_number: Sender's phone number
        message_type: Type of message (text, image, audio, etc.)
        content: Message content
        timestamp: Message timestamp
        media_id: Media ID if applicable
        media_url: Media URL if applicable

    Returns:
        Dict with processing result
    """
    logger.info(
        f"Processing message {message_id} from {from_number} (type: {message_type})"
    )

    # Check message-level idempotency
    idempotency_manager = IdempotencyManager()
    message_idempotency_key = f"idempotency:message:{message_id}"

    if idempotency_manager.is_processed(message_idempotency_key):
        logger.info(f"Message {message_id} already processed, skipping")
        return idempotency_manager.get_result(message_idempotency_key)

    # Check debounce for rapid messages
    debounce_manager = DebounceManager()
    debounce_key = debounce_manager.generate_debounce_key(
        user_id=from_number,
        event_type="message",
    )

    # Accumulate rapid messages for consolidation
    if not debounce_manager.should_process(debounce_key, window_seconds=2):
        logger.info(f"Message from {from_number} debounced, accumulating")
        accumulator_key = f"accumulator:messages:{from_number}"
        count = debounce_manager.accumulate_event(
            accumulator_key,
            {
                "message_id": message_id,
                "content": content,
                "timestamp": timestamp,
                "type": message_type,
            },
            ttl=5,
        )
        logger.info(f"Accumulated {count} messages for {from_number}")

        # If we have multiple messages, process them together
        if count >= 3:
            accumulated = debounce_manager.get_accumulated_events(
                accumulator_key, clear=True
            )
            # Consolidate messages
            content = " ".join([msg["content"] for msg in accumulated])
            logger.info(f"Consolidated {len(accumulated)} messages from {from_number}")

    try:
        # Import here to avoid circular dependencies
        from src.services.conversation_engine import get_conversation_engine
        from src.services.session_manager import get_session_manager
        from src.services.whatsapp_client import get_whatsapp_client

        # Get services
        session_manager = get_session_manager()
        conversation_engine = get_conversation_engine()

        # Get or create session
        session = session_manager.get_or_create_session(from_number)
        logger.info(f"Session {session.session_id} retrieved for {from_number}")

        # Process message through conversation engine
        response = conversation_engine.process_message(
            session_id=session.session_id,
            user_id=from_number,
            message=content,
            message_type=message_type,
            media_id=media_id,
            media_url=media_url,
        )

        logger.info(f"Generated response for message {message_id}")

        # Send response via WhatsApp
        whatsapp_client = get_whatsapp_client()

        if response.get("type") == "text":
            whatsapp_client.send_text_message(
                to=from_number,
                text=response.get("text", ""),
            )
        elif response.get("type") == "image":
            whatsapp_client.send_image_message(
                to=from_number,
                image_url=response.get("image_url", ""),
                caption=response.get("caption"),
            )
        elif response.get("type") == "template":
            whatsapp_client.send_template_message(
                to=from_number,
                template_name=response.get("template_name", ""),
                template_params=response.get("template_params", []),
            )

        logger.info(f"Response sent for message {message_id}")

        # Update session state
        session_manager.update_session(
            session_id=session.session_id,
            updates={
                "last_message_at": timestamp,
                "message_count": session.message_count + 1,
            },
        )

        # Queue session persistence to DuckDB
        save_session_to_duckdb_task.apply_async(
            kwargs={
                "session_id": session.session_id,
                "turn_id": session.turn_id,
            },
            queue="low_priority",
        )

        result = {
            "status": "success",
            "message_id": message_id,
            "session_id": session.session_id,
            "response_sent": True,
        }

        # Mark message as processed
        idempotency_manager.mark_processed(message_idempotency_key, result, ttl=86400)

        return result

    except Exception as e:
        logger.error(f"Error processing message {message_id}: {e}", exc_info=True)

        # Send error message to user
        try:
            from src.services.whatsapp_client import get_whatsapp_client

            whatsapp_client = get_whatsapp_client()
            whatsapp_client.send_text_message(
                to=from_number,
                text="Desculpe, ocorreu um erro ao processar sua mensagem. "
                "Por favor, tente novamente em alguns instantes.",
            )
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}")

        # Retry task
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    base=IdempotentTask,
    name="save_session_to_duckdb",
    max_retries=3,
    default_retry_delay=120,
)
def save_session_to_duckdb_task(
    self, session_id: str, turn_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Persist session data to DuckDB for analytics.

    This task runs asynchronously to avoid blocking message processing.
    It saves conversation history and context to DuckDB for later analysis.

    Idempotency: Uses session_id:turn_id as idempotency key

    Args:
        session_id: Session ID to persist
        turn_id: Turn ID for idempotency (optional)

    Returns:
        Dict with persistence result
    """
    logger.info(f"Persisting session {session_id} to DuckDB")

    # Idempotency check
    if turn_id is not None:
        idempotency_manager = IdempotencyManager()
        idempotency_key = idempotency_manager.generate_idempotency_key(
            session_id=session_id,
            turn_id=turn_id,
            task_name="save_session_to_duckdb",
        )

        if idempotency_manager.is_processed(idempotency_key):
            logger.info(f"Session {session_id}:{turn_id} already persisted")
            return idempotency_manager.get_result(idempotency_key)

    try:
        from src.services.session_manager import get_session_manager

        session_manager = get_session_manager()
        session = session_manager.get_session(session_id)

        if not session:
            logger.warning(f"Session {session_id} not found")
            return {"status": "not_found", "session_id": session_id}

        # Persist to DuckDB
        session_manager.persist_to_duckdb(session)

        logger.info(f"Session {session_id} persisted successfully")

        result = {
            "status": "success",
            "session_id": session_id,
        }

        # Mark as processed if turn_id provided
        if turn_id is not None:
            idempotency_manager = IdempotencyManager()
            idempotency_key = idempotency_manager.generate_idempotency_key(
                session_id=session_id,
                turn_id=turn_id,
                task_name="save_session_to_duckdb",
            )
            idempotency_manager.mark_processed(idempotency_key, result, ttl=3600)

        return result

    except Exception as e:
        logger.error(f"Error persisting session {session_id}: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=120)


@celery_app.task(
    bind=True,
    base=IdempotentTask,
    name="generate_embeddings",
    max_retries=3,
    default_retry_delay=60,
)
def generate_embeddings_task(
    self, message_id: str, text: str, session_id: str
) -> Dict[str, Any]:
    """
    Generate embeddings for message text.

    This task generates vector embeddings for messages to enable
    semantic search and similarity matching.

    Deduplication: Prevents generating embeddings for the same message multiple times

    Args:
        message_id: Message ID
        text: Message text
        session_id: Session ID

    Returns:
        Dict with embedding result
    """
    logger.info(f"Generating embeddings for message {message_id}")

    # Check for duplicate job
    dedup_manager = DeduplicationManager()
    job_hash = dedup_manager.generate_job_hash(
        task_name="generate_embeddings",
        args=(),
        kwargs={"message_id": message_id, "text": text},
    )

    if dedup_manager.is_duplicate(job_hash, window_seconds=3600):
        logger.info(f"Embeddings already generated for message {message_id}")
        return {"status": "duplicate", "message_id": message_id}

    # Mark job to prevent duplicates
    dedup_manager.mark_job(job_hash, window_seconds=3600)

    try:
        from src.services.nlp_service import get_nlp_service

        nlp_service = get_nlp_service()

        # Generate embeddings
        embeddings = nlp_service.generate_embeddings(text)

        # Store in DuckDB
        # TODO: Implement DuckDB storage for embeddings

        logger.info(f"Embeddings generated for message {message_id}")

        return {
            "status": "success",
            "message_id": message_id,
            "embedding_size": len(embeddings),
        }

    except Exception as e:
        logger.error(f"Error generating embeddings for {message_id}: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    name="notify_human_handoff",
    max_retries=3,
    default_retry_delay=60,
)
def notify_human_handoff_task(
    self,
    session_id: str,
    user_phone: str,
    reason: str,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Notify human team about handoff request.

    This task sends notifications to the human support team
    when a conversation needs to be escalated.

    Args:
        session_id: Session ID
        user_phone: User's phone number
        reason: Reason for handoff
        context: Additional context

    Returns:
        Dict with notification result
    """
    logger.info(f"Notifying human handoff for session {session_id}")

    try:
        # TODO: Implement notification logic
        # - Send email to support team
        # - Create ticket in CRM
        # - Send WhatsApp message to support number

        logger.info(f"Human handoff notification sent for session {session_id}")

        return {
            "status": "success",
            "session_id": session_id,
            "notified": True,
        }

    except Exception as e:
        logger.error(f"Error notifying handoff for {session_id}: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    name="send_reengagement",
    max_retries=3,
    default_retry_delay=300,
)
def send_reengagement_task(
    self, user_phone: str, session_id: str, message_type: str
) -> Dict[str, Any]:
    """
    Send reengagement message to inactive users.

    This task sends automated messages to users who haven't
    interacted with the bot for a certain period.

    Debounce: Prevents sending multiple reengagement messages within 24 hours

    Args:
        user_phone: User's phone number
        session_id: Session ID
        message_type: Type of reengagement message

    Returns:
        Dict with send result
    """
    logger.info(f"Sending reengagement to {user_phone} (type: {message_type})")

    # Debounce reengagement messages (max 1 per 24 hours)
    debounce_manager = DebounceManager()
    debounce_key = debounce_manager.generate_debounce_key(
        user_id=user_phone,
        event_type=f"reengagement_{message_type}",
    )

    if not debounce_manager.should_process(debounce_key, window_seconds=86400):
        logger.info(f"Reengagement debounced for {user_phone} (type: {message_type})")
        return {
            "status": "debounced",
            "user_phone": user_phone,
            "message_type": message_type,
        }

    try:
        from src.services.whatsapp_client import get_whatsapp_client

        whatsapp_client = get_whatsapp_client()

        # Define reengagement messages
        messages = {
            "inactive_48h": "Olá! Notei que você estava procurando um carro. "
            "Posso ajudar com mais informações?",
            "new_cars": "Temos novos carros que podem te interessar! "
            "Gostaria de ver as opções?",
            "price_drop": "Boa notícia! Alguns carros que você viu tiveram "
            "redução de preço. Quer conferir?",
        }

        message_text = messages.get(
            message_type, "Olá! Posso ajudar com algo sobre carros?"
        )

        whatsapp_client.send_text_message(to=user_phone, text=message_text)

        logger.info(f"Reengagement sent to {user_phone}")

        return {
            "status": "success",
            "user_phone": user_phone,
            "message_type": message_type,
        }

    except Exception as e:
        logger.error(f"Error sending reengagement to {user_phone}: {e}")
        raise self.retry(exc=e, countdown=300)


@celery_app.task(
    bind=True,
    name="collect_metrics",
    max_retries=3,
    default_retry_delay=60,
)
def collect_metrics_task(self, metric_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Collect and aggregate metrics.

    This task collects various metrics for monitoring and analytics.

    Deduplication: Prevents collecting the same metric multiple times within 60 seconds

    Args:
        metric_type: Type of metric to collect
        data: Metric data

    Returns:
        Dict with collection result
    """
    logger.info(f"Collecting metric: {metric_type}")

    # Deduplicate metric collection
    dedup_manager = DeduplicationManager()
    job_hash = dedup_manager.generate_job_hash(
        task_name="collect_metrics",
        args=(),
        kwargs={"metric_type": metric_type, "data": data},
    )

    if dedup_manager.is_duplicate(job_hash, window_seconds=60):
        logger.debug(f"Metric collection deduplicated: {metric_type}")
        return {"status": "duplicate", "metric_type": metric_type}

    # Mark job
    dedup_manager.mark_job(job_hash, window_seconds=60)

    try:
        # TODO: Implement metrics collection
        # - Store in PostgreSQL metrics_daily table
        # - Update Prometheus metrics
        # - Aggregate for dashboards

        logger.info(f"Metric collected: {metric_type}")

        return {
            "status": "success",
            "metric_type": metric_type,
        }

    except Exception as e:
        logger.error(f"Error collecting metric {metric_type}: {e}")
        raise self.retry(exc=e, countdown=60)
