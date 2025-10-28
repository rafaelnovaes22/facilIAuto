"""
Initialize databases (PostgreSQL and DuckDB)

This script:
1. Creates PostgreSQL tables using Alembic migrations
2. Creates DuckDB tables
3. Optionally seeds test data
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from alembic.config import Config
from alembic import command

from src.models.db_connection import get_duckdb_connection, init_postgres_db
from src.models.duckdb_schema import DuckDBSchema


def init_postgres(seed_data: bool = False) -> None:
    """
    Initialize PostgreSQL database using Alembic
    
    Args:
        seed_data: Whether to run seed data migration
    """
    print("🔧 Initializing PostgreSQL database...")
    
    # Get alembic config
    alembic_cfg = Config("alembic.ini")
    
    try:
        # Run migrations
        print("  ↳ Running migrations...")
        command.upgrade(alembic_cfg, "head" if seed_data else "001")
        print("  ✅ PostgreSQL migrations completed")
    except Exception as e:
        print(f"  ❌ Error running migrations: {e}")
        raise


def init_duckdb() -> None:
    """Initialize DuckDB database"""
    print("🔧 Initializing DuckDB database...")
    
    try:
        conn = get_duckdb_connection()
        DuckDBSchema.create_tables(conn)
        conn.close()
        print("  ✅ DuckDB tables created")
    except Exception as e:
        print(f"  ❌ Error creating DuckDB tables: {e}")
        raise


def verify_setup() -> None:
    """Verify database setup"""
    print("\n🔍 Verifying database setup...")
    
    # Verify PostgreSQL
    try:
        from src.models.db_connection import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"  ✅ PostgreSQL: {user_count} users in database")
    except Exception as e:
        print(f"  ❌ PostgreSQL verification failed: {e}")
    
    # Verify DuckDB
    try:
        conn = get_duckdb_connection()
        result = conn.execute("SELECT COUNT(*) FROM conversation_context").fetchone()
        context_count = result[0] if result else 0
        print(f"  ✅ DuckDB: {context_count} conversation contexts in database")
        conn.close()
    except Exception as e:
        print(f"  ❌ DuckDB verification failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Initialize chatbot databases")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Include seed data for testing",
    )
    parser.add_argument(
        "--skip-postgres",
        action="store_true",
        help="Skip PostgreSQL initialization",
    )
    parser.add_argument(
        "--skip-duckdb",
        action="store_true",
        help="Skip DuckDB initialization",
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 FacilIAuto Chatbot - Database Initialization")
    print("=" * 60)
    print()
    
    try:
        # Initialize PostgreSQL
        if not args.skip_postgres:
            init_postgres(seed_data=args.seed)
        else:
            print("⏭️  Skipping PostgreSQL initialization")
        
        print()
        
        # Initialize DuckDB
        if not args.skip_duckdb:
            init_duckdb()
        else:
            print("⏭️  Skipping DuckDB initialization")
        
        # Verify setup
        verify_setup()
        
        print()
        print("=" * 60)
        print("✅ Database initialization completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Database initialization failed: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
