"""Idempotency and debounce utilities for Celery tasks."""

import hashlib
import json
import logging
import time
from typing import Any, Callable, Dict, Optional

import redis
from celery import Task

from config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class IdempotencyManager:
    """Manager for task idempotency using Redis."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize idempotency manager.

        Args:
            redis_client: Redis client instance (optional)
        """
        if redis_client is None:
            redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
        self.redis = redis_client

    def generate_idempotency_key(
        self,
        session_id: str,
        turn_id: int,
        task_name: Optional[str] = None,
    ) -> str:
        """
        Generate idempotency key for a task.

        Format: idempotency:{task_name}:{session_id}:{turn_id}

        Args:
            session_id: Session ID
            turn_id: Turn ID (conversation turn number)
            task_name: Optional task name for namespacing

        Returns:
            Idempotency key string
        """
        if task_name:
            return f"idempotency:{task_name}:{session_id}:{turn_id}"
        return f"idempotency:{session_id}:{turn_id}"

    def is_processed(self, idempotency_key: str) -> bool:
        """
        Check if a task with this idempotency key has been processed.

        Args:
            idempotency_key: Idempotency key to check

        Returns:
            True if already processed, False otherwise
        """
        return self.redis.exists(idempotency_key) > 0

    def mark_processed(
        self,
        idempotency_key: str,
        result: Any = None,
        ttl: int = 3600,
    ) -> bool:
        """
        Mark a task as processed.

        Args:
            idempotency_key: Idempotency key
            result: Optional result to store
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if marked successfully, False if already existed
        """
        result_json = json.dumps(result) if result else "processed"

        # Use SET NX to ensure atomicity
        was_set = self.redis.set(
            idempotency_key,
            result_json,
            nx=True,  # Only set if not exists
            ex=ttl,
        )

        if was_set:
            logger.info(f"Marked task as processed: {idempotency_key}")
        else:
            logger.warning(f"Task already processed: {idempotency_key}")

        return bool(was_set)

    def get_result(self, idempotency_key: str) -> Optional[Any]:
        """
        Get the result of a previously processed task.

        Args:
            idempotency_key: Idempotency key

        Returns:
            Stored result or None if not found
        """
        result = self.redis.get(idempotency_key)
        if result and result != "processed":
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return result
        return None


class DebounceManager:
    """Manager for debouncing rapid events."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize debounce manager.

        Args:
            redis_client: Redis client instance (optional)
        """
        if redis_client is None:
            redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
        self.redis = redis_client

    def generate_debounce_key(
        self,
        user_id: str,
        event_type: str,
    ) -> str:
        """
        Generate debounce key for an event.

        Format: debounce:{event_type}:{user_id}

        Args:
            user_id: User identifier
            event_type: Type of event to debounce

        Returns:
            Debounce key string
        """
        return f"debounce:{event_type}:{user_id}"

    def should_process(
        self,
        debounce_key: str,
        window_seconds: int = 5,
    ) -> bool:
        """
        Check if an event should be processed based on debounce window.

        Args:
            debounce_key: Debounce key
            window_seconds: Debounce window in seconds

        Returns:
            True if should process, False if within debounce window
        """
        # Try to set the key with NX (only if not exists)
        was_set = self.redis.set(
            debounce_key,
            time.time(),
            nx=True,
            ex=window_seconds,
        )

        if was_set:
            logger.debug(f"Event allowed (debounce): {debounce_key}")
            return True
        else:
            logger.debug(f"Event debounced: {debounce_key}")
            return False

    def accumulate_event(
        self,
        accumulator_key: str,
        event_data: Dict[str, Any],
        ttl: int = 10,
    ) -> int:
        """
        Accumulate events for batch processing.

        Args:
            accumulator_key: Key for accumulating events
            event_data: Event data to accumulate
            ttl: Time to live for accumulator

        Returns:
            Number of accumulated events
        """
        # Add event to list
        self.redis.rpush(accumulator_key, json.dumps(event_data))

        # Set expiry if this is the first event
        if self.redis.ttl(accumulator_key) == -1:
            self.redis.expire(accumulator_key, ttl)

        # Return count of accumulated events
        return self.redis.llen(accumulator_key)

    def get_accumulated_events(
        self,
        accumulator_key: str,
        clear: bool = True,
    ) -> list:
        """
        Get accumulated events.

        Args:
            accumulator_key: Key for accumulated events
            clear: Whether to clear the accumulator after reading

        Returns:
            List of accumulated events
        """
        # Get all events
        events_json = self.redis.lrange(accumulator_key, 0, -1)

        # Parse events
        events = []
        for event_json in events_json:
            try:
                events.append(json.loads(event_json))
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse event: {event_json}")

        # Clear if requested
        if clear:
            self.redis.delete(accumulator_key)

        return events


class DeduplicationManager:
    """Manager for deduplicating jobs."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize deduplication manager.

        Args:
            redis_client: Redis client instance (optional)
        """
        if redis_client is None:
            redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
        self.redis = redis_client

    def generate_job_hash(self, task_name: str, args: tuple, kwargs: dict) -> str:
        """
        Generate a hash for a job based on its parameters.

        Args:
            task_name: Name of the task
            args: Task arguments
            kwargs: Task keyword arguments

        Returns:
            Hash string
        """
        # Create a deterministic representation
        job_repr = {
            "task": task_name,
            "args": args,
            "kwargs": sorted(kwargs.items()),
        }

        # Generate hash
        job_json = json.dumps(job_repr, sort_keys=True)
        return hashlib.sha256(job_json.encode()).hexdigest()

    def is_duplicate(
        self,
        job_hash: str,
        window_seconds: int = 60,
    ) -> bool:
        """
        Check if a job is a duplicate within the time window.

        Args:
            job_hash: Job hash
            window_seconds: Deduplication window in seconds

        Returns:
            True if duplicate, False otherwise
        """
        key = f"job_hash:{job_hash}"
        return self.redis.exists(key) > 0

    def mark_job(
        self,
        job_hash: str,
        window_seconds: int = 60,
    ) -> bool:
        """
        Mark a job as seen.

        Args:
            job_hash: Job hash
            window_seconds: Deduplication window in seconds

        Returns:
            True if marked successfully, False if already existed
        """
        key = f"job_hash:{job_hash}"

        was_set = self.redis.set(
            key,
            time.time(),
            nx=True,
            ex=window_seconds,
        )

        return bool(was_set)


class IdempotentTask(Task):
    """
    Base Celery task class with idempotency support.

    This task class automatically handles idempotency using Redis.
    Tasks that inherit from this class will not be executed multiple
    times with the same idempotency key.
    """

    def apply_async(
        self,
        args=None,
        kwargs=None,
        task_id=None,
        idempotency_key=None,
        **options,
    ):
        """
        Apply task asynchronously with idempotency support.

        Args:
            args: Task arguments
            kwargs: Task keyword arguments
            task_id: Task ID
            idempotency_key: Custom idempotency key
            **options: Additional Celery options

        Returns:
            AsyncResult
        """
        # Generate idempotency key if not provided
        if not idempotency_key and kwargs:
            if "session_id" in kwargs and "turn_id" in kwargs:
                idempotency_manager = IdempotencyManager()
                idempotency_key = idempotency_manager.generate_idempotency_key(
                    session_id=kwargs["session_id"],
                    turn_id=kwargs["turn_id"],
                    task_name=self.name,
                )

                # Check if already processed
                if idempotency_manager.is_processed(idempotency_key):
                    logger.info(
                        f"Task {self.name} already processed with key {idempotency_key}"
                    )
                    # Return cached result
                    result = idempotency_manager.get_result(idempotency_key)
                    # Create a fake AsyncResult
                    from celery.result import AsyncResult

                    return AsyncResult(idempotency_key)

                # Store idempotency key in kwargs for the task
                kwargs["_idempotency_key"] = idempotency_key

        return super().apply_async(args, kwargs, task_id=task_id, **options)

    def __call__(self, *args, **kwargs):
        """
        Execute task with idempotency check.

        Args:
            *args: Task arguments
            **kwargs: Task keyword arguments

        Returns:
            Task result
        """
        # Extract idempotency key if present
        idempotency_key = kwargs.pop("_idempotency_key", None)

        if idempotency_key:
            idempotency_manager = IdempotencyManager()

            # Double-check if already processed
            if idempotency_manager.is_processed(idempotency_key):
                logger.info(f"Task {self.name} already processed: {idempotency_key}")
                return idempotency_manager.get_result(idempotency_key)

            # Execute task
            result = super().__call__(*args, **kwargs)

            # Mark as processed
            idempotency_manager.mark_processed(idempotency_key, result)

            return result
        else:
            # No idempotency key, execute normally
            return super().__call__(*args, **kwargs)


def debounce_task(window_seconds: int = 5):
    """
    Decorator to debounce task execution.

    Args:
        window_seconds: Debounce window in seconds

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Extract user_id for debouncing
            user_id = kwargs.get("user_id") or kwargs.get("phone_number")

            if user_id:
                debounce_manager = DebounceManager()
                debounce_key = debounce_manager.generate_debounce_key(
                    user_id=user_id,
                    event_type=func.__name__,
                )

                if not debounce_manager.should_process(debounce_key, window_seconds):
                    logger.info(f"Task {func.__name__} debounced for user {user_id}")
                    return {"status": "debounced", "user_id": user_id}

            return func(*args, **kwargs)

        return wrapper

    return decorator


def deduplicate_job(window_seconds: int = 60):
    """
    Decorator to deduplicate job execution.

    Args:
        window_seconds: Deduplication window in seconds

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            dedup_manager = DeduplicationManager()

            # Generate job hash
            job_hash = dedup_manager.generate_job_hash(
                task_name=func.__name__,
                args=args,
                kwargs=kwargs,
            )

            # Check if duplicate
            if dedup_manager.is_duplicate(job_hash, window_seconds):
                logger.info(f"Duplicate job detected: {func.__name__}")
                return {"status": "duplicate", "job_hash": job_hash}

            # Mark job
            if not dedup_manager.mark_job(job_hash, window_seconds):
                logger.warning(f"Race condition detected for job: {func.__name__}")
                return {"status": "duplicate", "job_hash": job_hash}

            return func(*args, **kwargs)

        return wrapper

    return decorator
