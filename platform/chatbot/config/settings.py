"""Application settings and configuration."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "FacilIAuto Chatbot"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # WhatsApp
    whatsapp_api_url: str = "https://graph.facebook.com/v18.0"
    whatsapp_phone_number_id: str = ""
    whatsapp_access_token: str = ""
    whatsapp_verify_token: str = "faciliauto_webhook_2024"
    whatsapp_webhook_secret: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 50
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5

    # PostgreSQL
    postgres_url: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "faciliauto_chatbot"
    postgres_user: str = "faciliauto"
    postgres_password: str

    # DuckDB
    duckdb_path: str = "./data/chatbot.duckdb"
    duckdb_memory_limit: str = "2GB"
    duckdb_threads: int = 4

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Backend API
    backend_api_url: str = "http://localhost:8001"
    backend_api_timeout: int = 30
    backend_api_max_retries: int = 3

    # Session
    session_ttl_seconds: int = 86400
    max_conversation_history: int = 50

    # NLP
    nlp_model_name: str = "neuralmind/bert-base-portuguese-cased"
    nlp_confidence_threshold: float = 0.85
    spacy_model: str = "pt_core_news_lg"

    # LLM
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.7

    # Lead Qualification
    lead_qualification_threshold: int = 60
    lead_high_score_threshold: int = 80

    # Security
    secret_key: str
    encryption_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"

    # Monitoring
    prometheus_enabled: bool = True
    sentry_dsn: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
