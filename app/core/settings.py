import os
from dataclasses import dataclass


@dataclass
class Settings:
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "carencia_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "public")

    # App
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_STRUCTURED_LOGS: str = os.getenv("ENABLE_STRUCTURED_LOGS", "true")


settings = Settings()
