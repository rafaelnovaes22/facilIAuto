"""Redis client for caching and session management."""

import logging
from typing import Optional

import redis.asyncio as redis

from config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Global Redis client instance
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> Optional[redis.Redis]:
    """
    Get or create Redis client instance.

    Returns:
        Redis client or None if connection fails
    """
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    try:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.redis_max_connections,
            socket_timeout=settings.redis_socket_timeout,
            socket_connect_timeout=settings.redis_socket_connect_timeout,
        )

        # Test connection
        await _redis_client.ping()
        logger.info("Redis connection established")

        return _redis_client

    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return None


async def close_redis_client() -> None:
    """Close Redis client connection."""
    global _redis_client

    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")
