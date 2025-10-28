"""
Session Manager service using Redis and DuckDB.

Manages conversation sessions with distributed locks, idempotency,
and asynchronous persistence to DuckDB.
"""

import asyncio
import json
import time
from typing import Optional
from datetime import datetime

import redis.asyncio as redis
import duckdb

from ..models.session import SessionData, SessionState
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """
    Gerenciador de sessões com Redis e DuckDB.
    
    Funcionalidades:
    - Criação e recuperação de sessões com locks distribuídos
    - Atualização idempotente usando session_id:turn_id
    - Expiração automática com TTL de 24h
    - Persistência assíncrona no DuckDB
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        duckdb_path: str = "data/chatbot_context.duckdb"
    ):
        """
        Inicializa o SessionManager.
        
        Args:
            redis_client: Cliente Redis assíncrono
            duckdb_path: Caminho para o banco DuckDB
        """
        self.redis = redis_client
        self.duckdb_path = duckdb_path
        self._ensure_duckdb_tables()
    
    def _ensure_duckdb_tables(self) -> None:
        """Garante que as tabelas do DuckDB existem."""
        try:
            conn = duckdb.connect(self.duckdb_path)
            
            # Tabela de sessões arquivadas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS archived_sessions (
                    session_id VARCHAR PRIMARY KEY,
                    phone_number VARCHAR NOT NULL,
                    state VARCHAR NOT NULL,
                    turn_id INTEGER NOT NULL,
                    user_profile JSON,
                    memory_summary TEXT,
                    qualification_score DOUBLE,
                    completeness DOUBLE,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de histórico de mensagens
            conn.execute("""
                CREATE TABLE IF NOT EXISTS message_history (
                    id INTEGER PRIMARY KEY,
                    session_id VARCHAR NOT NULL,
                    role VARCHAR NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES archived_sessions(session_id)
                )
            """)
            
            # Índices para performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_phone 
                ON archived_sessions(phone_number)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_updated 
                ON archived_sessions(updated_at)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON message_history(session_id)
            """)
            
            conn.close()
            logger.info("DuckDB tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing DuckDB tables: {e}")
            raise
    
    async def get_or_create_session(self, phone_number: str) -> SessionData:
        """
        Obtém sessão existente ou cria nova com lock distribuído.
        
        Usa Redis SET NX (set if not exists) para evitar race conditions
        quando múltiplas requisições tentam criar a mesma sessão.
        
        Args:
            phone_number: Número de telefone do WhatsApp
            
        Returns:
            SessionData: Sessão existente ou nova
            
        Raises:
            Exception: Se houver erro ao acessar Redis
        """
        session_key = f"session:{phone_number}"
        
        try:
            # Tentar obter sessão existente do Redis
            session_json = await self.redis.get(session_key)
            
            if session_json:
                session_dict = json.loads(session_json)
                session = SessionData(**session_dict)
                
                # Verificar se expirou
                if session.is_expired():
                    logger.info(f"Session expired for {phone_number}, creating new one")
                    await self._archive_session(session)
                    await self.redis.delete(session_key)
                else:
                    logger.info(f"Retrieved existing session for {phone_number}")
                    return session
            
            # Criar nova sessão com lock distribuído
            lock_key = f"lock:{session_key}"
            lock_timeout = 10  # segundos
            
            # Tentar adquirir lock
            lock_acquired = await self.redis.set(
                lock_key,
                "1",
                nx=True,  # Set if not exists
                ex=lock_timeout  # Expira após 10s
            )
            
            if not lock_acquired:
                # Aguardar lock ser liberado e tentar novamente
                logger.info(f"Waiting for lock on {phone_number}")
                await asyncio.sleep(0.1)
                return await self.get_or_create_session(phone_number)
            
            try:
                # Verificar novamente se sessão foi criada enquanto aguardávamos
                session_json = await self.redis.get(session_key)
                if session_json:
                    session_dict = json.loads(session_json)
                    return SessionData(**session_dict)
                
                # Criar nova sessão
                session_id = f"{phone_number}:{int(time.time())}"
                session = SessionData(
                    session_id=session_id,
                    phone_number=phone_number,
                    state=SessionState.GREETING
                )
                
                # Salvar no Redis com TTL
                await self.redis.setex(
                    session_key,
                    session.ttl_seconds,
                    session.model_dump_json()
                )
                
                logger.info(f"Created new session {session_id} for {phone_number}")
                return session
                
            finally:
                # Liberar lock
                await self.redis.delete(lock_key)
                
        except Exception as e:
            logger.error(f"Error in get_or_create_session for {phone_number}: {e}")
            raise
    
    async def update_session(self, session: SessionData) -> bool:
        """
        Atualiza sessão com idempotência.
        
        Usa session_id:turn_id como chave de idempotência para garantir
        que cada turno seja processado apenas uma vez.
        
        Args:
            session: Sessão a ser atualizada
            
        Returns:
            bool: True se atualizado, False se já foi processado
            
        Raises:
            Exception: Se houver erro ao acessar Redis
        """
        try:
            # Incrementar turn_id
            session.increment_turn()
            
            # Chave de idempotência
            idempotency_key = f"idempotency:{session.get_idempotency_key()}"
            
            # Verificar se já foi processado
            already_processed = await self.redis.exists(idempotency_key)
            if already_processed:
                logger.warning(
                    f"Turn {session.turn_id} for session {session.session_id} "
                    "already processed (idempotent)"
                )
                return False
            
            # Marcar como processado (TTL de 1 hora)
            await self.redis.setex(idempotency_key, 3600, "1")
            
            # Atualizar sessão no Redis
            session_key = f"session:{session.phone_number}"
            await self.redis.setex(
                session_key,
                session.ttl_seconds,
                session.model_dump_json()
            )
            
            logger.info(
                f"Updated session {session.session_id} "
                f"(turn {session.turn_id}, state: {session.state})"
            )
            
            # Agendar persistência assíncrona no DuckDB
            # Nota: Em produção, isso seria feito via Celery task
            asyncio.create_task(self._save_to_duckdb_async(session))
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating session {session.session_id}: {e}")
            raise
    
    async def expire_session(self, phone_number: str) -> bool:
        """
        Expira sessão manualmente e arquiva no DuckDB.
        
        Args:
            phone_number: Número de telefone
            
        Returns:
            bool: True se sessão foi expirada, False se não existia
        """
        try:
            session_key = f"session:{phone_number}"
            
            # Obter sessão antes de deletar
            session_json = await self.redis.get(session_key)
            if not session_json:
                logger.info(f"No session to expire for {phone_number}")
                return False
            
            session_dict = json.loads(session_json)
            session = SessionData(**session_dict)
            
            # Arquivar no DuckDB
            await self._archive_session(session)
            
            # Deletar do Redis
            await self.redis.delete(session_key)
            
            logger.info(f"Expired and archived session for {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error expiring session for {phone_number}: {e}")
            raise
    
    async def get_session(self, phone_number: str) -> Optional[SessionData]:
        """
        Obtém sessão existente sem criar nova.
        
        Args:
            phone_number: Número de telefone
            
        Returns:
            SessionData ou None se não existir
        """
        try:
            session_key = f"session:{phone_number}"
            session_json = await self.redis.get(session_key)
            
            if not session_json:
                return None
            
            session_dict = json.loads(session_json)
            session = SessionData(**session_dict)
            
            # Verificar se expirou
            if session.is_expired():
                await self.expire_session(phone_number)
                return None
            
            return session
            
        except Exception as e:
            logger.error(f"Error getting session for {phone_number}: {e}")
            return None
    
    async def _save_to_duckdb_async(self, session: SessionData) -> None:
        """
        Salva resumo da sessão no DuckDB de forma assíncrona.
        
        Em produção, isso seria uma Celery task. Por enquanto,
        executamos em background task.
        
        Args:
            session: Sessão a ser salva
        """
        try:
            # Executar em thread separada para não bloquear
            await asyncio.to_thread(self._save_to_duckdb_sync, session)
        except Exception as e:
            logger.error(f"Error saving session to DuckDB: {e}")
    
    def _save_to_duckdb_sync(self, session: SessionData) -> None:
        """
        Salva sessão no DuckDB (versão síncrona).
        
        Args:
            session: Sessão a ser salva
        """
        try:
            conn = duckdb.connect(self.duckdb_path)
            
            # Preparar dados
            user_profile_json = json.dumps(session.user_profile.model_dump())
            
            # Upsert na tabela de sessões
            conn.execute("""
                INSERT OR REPLACE INTO archived_sessions (
                    session_id, phone_number, state, turn_id,
                    user_profile, memory_summary, qualification_score,
                    completeness, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                session.session_id,
                session.phone_number,
                session.state.value,
                session.turn_id,
                user_profile_json,
                session.memory.summary,
                session.user_profile.qualification_score,
                session.user_profile.completeness,
                session.created_at,
                session.updated_at
            ])
            
            conn.close()
            logger.debug(f"Saved session {session.session_id} to DuckDB")
            
        except Exception as e:
            logger.error(f"Error in _save_to_duckdb_sync: {e}")
    
    async def _archive_session(self, session: SessionData) -> None:
        """
        Arquiva sessão completa no DuckDB incluindo mensagens.
        
        Args:
            session: Sessão a ser arquivada
        """
        try:
            await asyncio.to_thread(self._archive_session_sync, session)
        except Exception as e:
            logger.error(f"Error archiving session: {e}")
    
    def _archive_session_sync(self, session: SessionData) -> None:
        """
        Arquiva sessão no DuckDB (versão síncrona).
        
        Args:
            session: Sessão a ser arquivada
        """
        try:
            conn = duckdb.connect(self.duckdb_path)
            
            # Salvar sessão
            self._save_to_duckdb_sync(session)
            
            # Salvar mensagens
            for msg in session.memory.messages:
                conn.execute("""
                    INSERT INTO message_history (
                        session_id, role, content, timestamp
                    ) VALUES (?, ?, ?, ?)
                """, [
                    session.session_id,
                    msg["role"],
                    msg["content"],
                    datetime.fromisoformat(msg["timestamp"])
                ])
            
            conn.close()
            logger.info(f"Archived session {session.session_id} with messages")
            
        except Exception as e:
            logger.error(f"Error in _archive_session_sync: {e}")
    
    async def get_user_history(self, phone_number: str, limit: int = 5) -> list:
        """
        Obtém histórico de sessões anteriores do usuário.
        
        Args:
            phone_number: Número de telefone
            limit: Número máximo de sessões a retornar
            
        Returns:
            Lista de sessões anteriores
        """
        try:
            conn = duckdb.connect(self.duckdb_path)
            
            result = conn.execute("""
                SELECT session_id, state, qualification_score, 
                       completeness, created_at, updated_at
                FROM archived_sessions
                WHERE phone_number = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, [phone_number, limit]).fetchall()
            
            conn.close()
            
            return [
                {
                    "session_id": row[0],
                    "state": row[1],
                    "qualification_score": row[2],
                    "completeness": row[3],
                    "created_at": row[4],
                    "updated_at": row[5]
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Error getting user history: {e}")
            return []
    
    async def close(self) -> None:
        """Fecha conexões."""
        try:
            await self.redis.close()
            logger.info("SessionManager connections closed")
        except Exception as e:
            logger.error(f"Error closing SessionManager: {e}")
