"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from config.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    # Startup
    print(f"Starting {settings.app_name}...")
    # Initialize Redis connection
    from src.services.redis_client import get_redis_client
    await get_redis_client()
    # Initialize WhatsApp client
    from src.services.whatsapp_client import get_whatsapp_client
    await get_whatsapp_client()
    yield
    # Shutdown
    print(f"Shutting down {settings.app_name}...")
    # Close WhatsApp client
    from src.services.whatsapp_client import close_whatsapp_client
    await close_whatsapp_client()
    # Close Redis connection
    from src.services.redis_client import close_redis_client
    await close_redis_client()


app = FastAPI(
    title=settings.app_name,
    description="WhatsApp Chatbot for FacilIAuto - Intelligent vehicle recommendations",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "0.1.0",
    }


@app.get("/ready")
async def readiness_check() -> dict:
    """Readiness check endpoint."""
    # TODO: Check connections to Redis, PostgreSQL, etc.
    return {
        "status": "ready",
        "checks": {
            "redis": "ok",
            "postgres": "ok",
            "duckdb": "ok",
        },
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


# Import and include routers
from src.api.webhook import router as webhook_router
app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])
