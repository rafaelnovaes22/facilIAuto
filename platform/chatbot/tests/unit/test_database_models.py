"""
Unit tests for database models
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.database import Base, User, Session, Message, QualifiedLead


@pytest.fixture
def db_engine():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    """Create database session for testing"""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


class TestUserModel:
    """Tests for User model"""

    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            phone_number="+5511999999999",
            name="Test User",
            email="test@example.com",
            consent_given=True,
            consent_timestamp=datetime.utcnow(),
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.phone_number == "+5511999999999"
        assert user.is_active is True

    def test_user_unique_phone(self, db_session):
        """Test that phone numbers must be unique"""
        user1 = User(phone_number="+5511999999999", consent_given=True)
        db_session.add(user1)
        db_session.commit()

        user2 = User(phone_number="+5511999999999", consent_given=True)
        db_session.add(user2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestSessionModel:
    """Tests for Session model"""

    def test_create_session(self, db_session):
        """Test creating a session"""
        # Create user first
        user = User(phone_number="+5511999999999", consent_given=True)
        db_session.add(user)
        db_session.commit()

        # Create session
        session = Session(
            session_id="test_session_001",
            user_id=user.id,
            state="greeting",
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db_session.add(session)
        db_session.commit()

        assert session.id is not None
        assert session.session_id == "test_session_001"
        assert session.turn_id == 0
        assert session.qualification_score == 0.0

    def test_session_with_profile(self, db_session):
        """Test session with user profile JSON"""
        user = User(phone_number="+5511999999999", consent_given=True)
        db_session.add(user)
        db_session.commit()

        profile = {
            "orcamento_min": 50000,
            "orcamento_max": 80000,
            "uso_principal": "trabalho",
            "city": "São Paulo",
        }

        session = Session(
            session_id="test_session_002",
            user_id=user.id,
            user_profile=profile,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db_session.add(session)
        db_session.commit()

        # Retrieve and verify
        retrieved = db_session.query(Session).filter_by(session_id="test_session_002").first()
        assert retrieved.user_profile["orcamento_min"] == 50000
        assert retrieved.user_profile["city"] == "São Paulo"


class TestMessageModel:
    """Tests for Message model"""

    def test_create_message(self, db_session):
        """Test creating a message"""
        # Setup user and session
        user = User(phone_number="+5511999999999", consent_given=True)
        db_session.add(user)
        db_session.commit()

        session = Session(
            session_id="test_session_003",
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db_session.add(session)
        db_session.commit()

        # Create message
        message = Message(
            message_id="msg_001",
            session_id=session.id,
            role="user",
            content="Olá, quero comprar um carro",
            intent="greeting",
            sentiment="neutral",
            confidence=0.95,
        )
        db_session.add(message)
        db_session.commit()

        assert message.id is not None
        assert message.role == "user"
        assert message.confidence == 0.95

    def test_message_with_entities(self, db_session):
        """Test message with entities JSON"""
        user = User(phone_number="+5511999999999", consent_given=True)
        db_session.add(user)
        db_session.commit()

        session = Session(
            session_id="test_session_004",
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db_session.add(session)
        db_session.commit()

        entities = [
            {"type": "budget", "value": "50000", "confidence": 0.92},
            {"type": "brand", "value": "Toyota", "confidence": 0.88},
        ]

        message = Message(
            message_id="msg_002",
            session_id=session.id,
            role="user",
            content="Quero um Toyota até 50 mil",
            entities=entities,
        )
        db_session.add(message)
        db_session.commit()

        # Retrieve and verify
        retrieved = db_session.query(Message).filter_by(message_id="msg_002").first()
        assert len(retrieved.entities) == 2
        assert retrieved.entities[0]["type"] == "budget"


class TestQualifiedLeadModel:
    """Tests for QualifiedLead model"""

    def test_create_qualified_lead(self, db_session):
        """Test creating a qualified lead"""
        user = User(phone_number="+5511999999999", consent_given=True)
        db_session.add(user)
        db_session.commit()

        profile = {
            "orcamento_min": 80000,
            "orcamento_max": 120000,
            "uso_principal": "família",
        }

        lead = QualifiedLead(
            user_id=user.id,
            session_id="session_005",
            qualification_score=75.0,
            priority="high",
            user_profile=profile,
            conversation_summary="Cliente procura SUV para família",
        )
        db_session.add(lead)
        db_session.commit()

        assert lead.id is not None
        assert lead.qualification_score == 75.0
        assert lead.priority == "high"
        assert lead.contacted is False
        assert lead.converted is False


class TestRelationships:
    """Tests for model relationships"""

    def test_user_sessions_relationship(self, db_session):
        """Test User -> Sessions relationship"""
        user = User(phone_number="+5511999999999", consent_given=True)
        db_session.add(user)
        db_session.commit()

        # Create multiple sessions
        for i in range(3):
            session = Session(
                session_id=f"session_{i}",
                user_id=user.id,
                expires_at=datetime.utcnow() + timedelta(hours=24),
            )
            db_session.add(session)
        db_session.commit()

        # Verify relationship
        retrieved_user = db_session.query(User).filter_by(phone_number="+5511999999999").first()
        assert len(retrieved_user.sessions) == 3

    def test_session_messages_relationship(self, db_session):
        """Test Session -> Messages relationship"""
        user = User(phone_number="+5511999999999", consent_given=True)
        db_session.add(user)
        db_session.commit()

        session = Session(
            session_id="session_006",
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db_session.add(session)
        db_session.commit()

        # Create multiple messages
        for i in range(5):
            message = Message(
                message_id=f"msg_{i}",
                session_id=session.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
            )
            db_session.add(message)
        db_session.commit()

        # Verify relationship
        retrieved_session = db_session.query(Session).filter_by(session_id="session_006").first()
        assert len(retrieved_session.messages) == 5

    def test_cascade_delete(self, db_session):
        """Test cascade delete on user deletion"""
        user = User(phone_number="+5511999999999", consent_given=True)
        db_session.add(user)
        db_session.commit()

        session = Session(
            session_id="session_007",
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db_session.add(session)
        db_session.commit()

        message = Message(
            message_id="msg_cascade",
            session_id=session.id,
            role="user",
            content="Test cascade",
        )
        db_session.add(message)
        db_session.commit()

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Verify cascade
        assert db_session.query(Session).filter_by(session_id="session_007").first() is None
        assert db_session.query(Message).filter_by(message_id="msg_cascade").first() is None
