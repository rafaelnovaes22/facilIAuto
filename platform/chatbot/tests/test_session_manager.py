"""
Tests for SessionManager service.
"""

import pytest
import asyncio
from datetime import datetime
import redis.asyncio as redis

from src.models.session import SessionData, SessionState, UserProfileData
from src.services.session_manager import SessionManager


@pytest.fixture
async def redis_client():
    """Create Redis client for testing."""
    client = redis.Redis(
        host="localhost",
        port=6379,
        db=1,  # Use separate DB for tests
        decode_responses=False
    )
    yield client
    # Cleanup
    await client.flushdb()
    await client.close()


@pytest.fixture
async def session_manager(redis_client):
    """Create SessionManager instance for testing."""
    manager = SessionManager(
        redis_client=redis_client,
        duckdb_path=":memory:"  # Use in-memory DB for tests
    )
    yield manager
    await manager.close()


@pytest.mark.asyncio
async def test_create_new_session(session_manager):
    """Test creating a new session."""
    phone = "+5511999999999"
    
    session = await session_manager.get_or_create_session(phone)
    
    assert session is not None
    assert session.phone_number == phone
    assert session.state == SessionState.GREETING
    assert session.turn_id == 0
    assert not session.consent_given


@pytest.mark.asyncio
async def test_get_existing_session(session_manager):
    """Test retrieving an existing session."""
    phone = "+5511999999999"
    
    # Create session
    session1 = await session_manager.get_or_create_session(phone)
    session_id = session1.session_id
    
    # Retrieve same session
    session2 = await session_manager.get_or_create_session(phone)
    
    assert session2.session_id == session_id
    assert session2.phone_number == phone


@pytest.mark.asyncio
async def test_update_session(session_manager):
    """Test updating a session."""
    phone = "+5511999999999"
    
    # Create session
    session = await session_manager.get_or_create_session(phone)
    initial_turn = session.turn_id
    
    # Update session
    session.state = SessionState.COLLECTING_PROFILE
    session.add_message("user", "Olá!")
    
    updated = await session_manager.update_session(session)
    
    assert updated is True
    assert session.turn_id == initial_turn + 1
    assert len(session.memory.messages) == 1


@pytest.mark.asyncio
async def test_idempotency(session_manager):
    """Test idempotent updates."""
    phone = "+5511999999999"
    
    # Create session
    session = await session_manager.get_or_create_session(phone)
    
    # First update
    session.add_message("user", "Test")
    result1 = await session_manager.update_session(session)
    turn_id = session.turn_id
    
    # Try to update with same turn_id (should be idempotent)
    session.turn_id = turn_id - 1  # Reset to previous turn
    result2 = await session_manager.update_session(session)
    
    assert result1 is True
    assert result2 is False  # Should be rejected as duplicate


@pytest.mark.asyncio
async def test_expire_session(session_manager):
    """Test expiring a session."""
    phone = "+5511999999999"
    
    # Create session
    session = await session_manager.get_or_create_session(phone)
    
    # Expire session
    expired = await session_manager.expire_session(phone)
    
    assert expired is True
    
    # Verify session is gone
    retrieved = await session_manager.get_session(phone)
    assert retrieved is None


@pytest.mark.asyncio
async def test_concurrent_session_creation(session_manager):
    """Test that concurrent requests don't create duplicate sessions."""
    phone = "+5511999999999"
    
    # Create multiple concurrent requests
    tasks = [
        session_manager.get_or_create_session(phone)
        for _ in range(5)
    ]
    
    sessions = await asyncio.gather(*tasks)
    
    # All should have the same session_id
    session_ids = [s.session_id for s in sessions]
    assert len(set(session_ids)) == 1


@pytest.mark.asyncio
async def test_user_profile_completeness(session_manager):
    """Test user profile completeness calculation."""
    phone = "+5511999999999"
    
    session = await session_manager.get_or_create_session(phone)
    
    # Initially empty
    assert session.user_profile.completeness == 0.0
    
    # Add budget
    session.user_profile.orcamento_min = 50000
    session.user_profile.orcamento_max = 80000
    assert session.user_profile.completeness == 0.25
    
    # Add usage
    session.user_profile.uso_principal = "trabalho"
    assert session.user_profile.completeness == 0.50
    
    # Add location
    session.user_profile.city = "São Paulo"
    session.user_profile.state = "SP"
    assert session.user_profile.completeness == 0.70
    
    # Add priorities
    session.user_profile.prioridades = {
        "economia": 5,
        "conforto": 4,
        "seguranca": 5
    }
    assert session.user_profile.completeness == 1.0


@pytest.mark.asyncio
async def test_qualification_score(session_manager):
    """Test lead qualification score calculation."""
    phone = "+5511999999999"
    
    session = await session_manager.get_or_create_session(phone)
    profile = session.user_profile
    
    # Initially low score
    assert profile.qualification_score == 0.0
    
    # Add budget (30 points)
    profile.orcamento_min = 50000
    profile.orcamento_max = 80000
    assert profile.qualification_score == 30.0
    
    # Add urgency (25 points)
    profile.urgencia = "imediata"
    assert profile.qualification_score == 55.0
    
    # Add preferences (25 points)
    profile.uso_principal = "trabalho"
    profile.prioridades = {"economia": 5, "conforto": 4, "seguranca": 5}
    assert profile.qualification_score == 80.0
    
    # Add engagement (20 points)
    profile.interacoes_count = 5
    assert profile.qualification_score == 100.0


@pytest.mark.asyncio
async def test_session_messages(session_manager):
    """Test adding and retrieving messages."""
    phone = "+5511999999999"
    
    session = await session_manager.get_or_create_session(phone)
    
    # Add messages
    session.add_message("user", "Olá!")
    session.add_message("assistant", "Olá! Como posso ajudar?")
    session.add_message("user", "Quero comprar um carro")
    
    # Check messages
    assert len(session.memory.messages) == 3
    assert session.user_profile.interacoes_count == 3
    
    # Get recent messages
    recent = session.memory.get_recent_messages(2)
    assert len(recent) == 2
    assert recent[0]["content"] == "Olá! Como posso ajudar?"


@pytest.mark.asyncio
async def test_consent_management(session_manager):
    """Test LGPD consent management."""
    phone = "+5511999999999"
    
    session = await session_manager.get_or_create_session(phone)
    
    # Initially no consent
    assert not session.consent_given
    assert session.consent_timestamp is None
    
    # Give consent
    session.give_consent()
    
    assert session.consent_given
    assert session.consent_timestamp is not None
    assert isinstance(session.consent_timestamp, datetime)
