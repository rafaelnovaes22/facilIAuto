"""Celery configuration."""

from celery import Celery
from kombu import Exchange, Queue

from config.settings import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "faciliauto_chatbot",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    # Rate limiting
    task_default_rate_limit="100/m",  # 100 tasks per minute
    # Queue configuration
    task_queues=(
        Queue(
            "default",
            Exchange("default"),
            routing_key="default",
            queue_arguments={"x-max-priority": 10},
        ),
        Queue(
            "high_priority",
            Exchange("high_priority"),
            routing_key="high_priority",
            queue_arguments={"x-max-priority": 10},
        ),
        Queue(
            "low_priority",
            Exchange("low_priority"),
            routing_key="low_priority",
            queue_arguments={"x-max-priority": 10},
        ),
    ),
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["src.tasks"])
