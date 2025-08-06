"""
Configurações do banco de dados PostgreSQL
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Configurações do banco PostgreSQL
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "carencia_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "schema": os.getenv("DB_SCHEMA", "public"),
}

# URL de conexão PostgreSQL
DATABASE_URL = f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

# Engine SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=False,  # Mude para True para ver SQL logs
)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos SQLAlchemy
Base = declarative_base()


def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        from sqlalchemy import text

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Erro ao conectar com o banco: {e}")
        return False
