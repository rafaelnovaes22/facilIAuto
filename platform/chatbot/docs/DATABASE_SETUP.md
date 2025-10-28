# Database Setup Guide

This guide explains how to set up and manage the databases for the FacilIAuto WhatsApp Chatbot.

## Overview

The chatbot uses two databases:

1. **PostgreSQL** - Primary relational database for persistent data
   - Users, sessions, messages
   - Qualified leads, car interactions
   - Human handoffs, daily metrics

2. **DuckDB** - Analytical database for fast queries
   - Conversation context (structured summaries)
   - Message history (optimized for analytics)
   - Message embeddings (for semantic search)

## Prerequisites

- Python 3.11+
- PostgreSQL 14+ (running locally or via Docker)
- Poetry or pip for dependency management

## Environment Variables

Create a `.env` file in the `platform/chatbot` directory:

```bash
# PostgreSQL Configuration
POSTGRES_USER=faciliauto
POSTGRES_PASSWORD=faciliauto123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=faciliauto_chatbot

# DuckDB Configuration
DUCKDB_PATH=data/chatbot.duckdb

# SQL Echo (for debugging)
SQL_ECHO=false
```

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Start PostgreSQL and Redis
cd platform/chatbot
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
sleep 5

# Initialize databases
python scripts/init_databases.py --seed
```

### Option 2: Manual Setup

1. **Start PostgreSQL**

```bash
# Using Docker
docker run -d \
  --name faciliauto-postgres \
  -e POSTGRES_USER=faciliauto \
  -e POSTGRES_PASSWORD=faciliauto123 \
  -e POSTGRES_DB=faciliauto_chatbot \
  -p 5432:5432 \
  postgres:14

# Or use your local PostgreSQL installation
```

2. **Initialize Databases**

```bash
cd platform/chatbot

# Without seed data
python scripts/init_databases.py

# With seed data (for testing)
python scripts/init_databases.py --seed
```

## Database Schema

### PostgreSQL Tables

#### users
Stores WhatsApp user information
- `id` (PK)
- `phone_number` (unique)
- `name`, `email`
- `consent_given`, `consent_timestamp` (LGPD compliance)
- `created_at`, `updated_at`, `is_active`

#### sessions
Stores conversation sessions
- `id` (PK)
- `session_id` (unique)
- `user_id` (FK → users)
- `state` (conversation state)
- `turn_id` (for idempotency)
- `user_profile` (JSON)
- `current_recommendations` (JSON)
- `qualification_score`
- `expires_at` (TTL)

#### messages
Stores all messages exchanged
- `id` (PK)
- `message_id` (unique)
- `session_id` (FK → sessions)
- `role` (user/assistant)
- `content`, `message_type`
- `intent`, `sentiment`, `confidence`
- `entities` (JSON)

#### qualified_leads
Stores qualified leads for dealerships
- `id` (PK)
- `user_id` (FK → users)
- `session_id`
- `qualification_score`, `priority`
- `user_profile` (JSON)
- `recommended_cars` (JSON)
- `contacted`, `converted`

#### car_interactions
Tracks user interactions with cars
- `id` (PK)
- `session_id` (FK → sessions)
- `car_id`
- `interaction_type` (view, like, dislike, compare)
- `feedback`

#### human_handoffs
Tracks transfers to human agents
- `id` (PK)
- `session_id` (FK → sessions)
- `reason`, `context` (JSON)
- `status`, `assigned_to`
- `rating`, `feedback`

#### metrics_daily
Aggregated daily statistics
- `id` (PK)
- `date` (unique)
- `total_messages`, `total_sessions`, `total_users`
- `total_qualified_leads`, `total_handoffs`
- `avg_response_time_ms`, `avg_qualification_score`
- `nlp_accuracy`, `conversion_rate`

### DuckDB Tables

#### conversation_context
Structured conversation summaries
- `session_id`, `phone_number`
- `turn_id`
- `summary`, `key_entities` (JSON)
- `user_profile` (JSON)
- `state`

#### message_history
Message history optimized for analytics
- `message_id`, `session_id`, `phone_number`
- `role`, `content`, `message_type`
- `intent`, `sentiment`, `confidence`
- `entities` (JSON)
- `response_time_ms`

#### message_embeddings
Message embeddings for semantic search
- `message_id`, `session_id`, `phone_number`
- `content`
- `embedding` (DOUBLE[])
- `model_name`

## Migrations

### Creating a New Migration

```bash
cd platform/chatbot

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Or create empty migration
alembic revision -m "Description of changes"
```

### Running Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade 001

# Downgrade one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade 001

# Show current revision
alembic current

# Show migration history
alembic history
```

### Seed Data

The seed data migration (`002_seed_test_data.py`) includes:
- 3 test users
- 2 test sessions
- 4 test messages
- 1 qualified lead

To apply seed data:
```bash
alembic upgrade 002
```

To remove seed data:
```bash
alembic downgrade 001
```

## Backup and Restore

### PostgreSQL

```bash
# Backup
pg_dump -U faciliauto -h localhost faciliauto_chatbot > backup.sql

# Restore
psql -U faciliauto -h localhost faciliauto_chatbot < backup.sql
```

### DuckDB

```bash
# Backup (just copy the file)
cp data/chatbot.duckdb data/chatbot.duckdb.backup

# Restore
cp data/chatbot.duckdb.backup data/chatbot.duckdb
```

## Troubleshooting

### Connection Refused

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check PostgreSQL logs
docker logs faciliauto-postgres

# Test connection
psql -U faciliauto -h localhost -d faciliauto_chatbot
```

### Migration Errors

```bash
# Check current revision
alembic current

# Check migration history
alembic history

# Stamp database to specific revision (use with caution)
alembic stamp head
```

### DuckDB Locked

```bash
# Close all connections
# DuckDB is single-writer, ensure no other processes are using it

# If needed, delete and recreate
rm data/chatbot.duckdb
python scripts/init_databases.py --skip-postgres
```

## Performance Optimization

### PostgreSQL

1. **Indexes** - Already created for common queries
2. **Connection Pooling** - Configured in `db_connection.py`
3. **Vacuum** - Run periodically
   ```sql
   VACUUM ANALYZE;
   ```

### DuckDB

1. **Batch Inserts** - Use bulk operations
2. **Columnar Storage** - Optimized for analytics
3. **Compression** - Automatic

## Monitoring

### Check Database Size

```sql
-- PostgreSQL
SELECT pg_size_pretty(pg_database_size('faciliauto_chatbot'));

-- DuckDB
SELECT pg_size_pretty(pg_database_size());
```

### Check Table Sizes

```sql
-- PostgreSQL
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check Row Counts

```sql
-- PostgreSQL
SELECT 
    schemaname,
    tablename,
    n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
```

## Security

1. **Encryption at Rest** - Configure PostgreSQL encryption
2. **Encryption in Transit** - Use SSL/TLS connections
3. **Access Control** - Use strong passwords, limit network access
4. **LGPD Compliance** - Implement data retention policies

## Next Steps

After setting up the databases:

1. Configure Redis for session management
2. Set up Celery for async tasks
3. Implement NLP service
4. Build conversation engine

See the main [README.md](../README.md) for the complete setup guide.
