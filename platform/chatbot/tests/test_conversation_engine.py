"""
Tests for Conversation Engine.

Tests the LangGraph-based conversation flow, state management,
and integration with NLP and Guardrails services.
"""

import pytest
from datetime import datetime

from src.services.conversation_engine import ConversationEngine, ConversationState
from src.services.nlp_service import NLPService, NLPResult, Intent, Sentiment
from src.services.guardrails import GuardrailsService
from src.models.session import SessionData, SessionState


@pytest.fixture
def nlp_service():
    """Create NLP service instance."""
    return NLPService()


@pytest.fixture
def guardrails_service():
    """Create Guardrails service instance."""
    return GuardrailsService()


@pytest.fixture
def conversation_engine(nlp_service, guardrails_service):
    """Create Conversation Engine instance."""
    return ConversationEngine(nlp_service, guardrails_service)


@pytest.fixture
def sample_session():
    """Create sample session."""
    return SessionData(
        session_id="5511999999999:1234567890",
        phone_number="5511999999999",
        state=SessionState.GREETING
    )


@pytest.fixture
def sample_nlp_result():
    """Create sample NLP result."""
    return NLPResult(
        intent=Intent.GREETING,
        confidence=0.95,
        entities=[],
        sentiment=Sentiment.POSITIVE,
        normalized_text="oi",
        processing_time_ms=10.0
    )


class TestConversationEngine:
    """Test suite for ConversationEngine."""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, conversation_engine):
        """Test that engine initializes correctly."""
        assert conversation_engine is not None
        assert conversation_engine.nlp is not None
        assert conversation_engine.guardrails is not None
        assert conversation_engine.graph is not None
        assert conversation_engine.checkpointer is not None
    
    @pytest.mark.asyncio
    async def test_process_greeting(
        self,
        conversation_engine,
        sample_session,
        sample_nlp_result
    ):
        """Test processing a greeting message."""
        message = "Oi"
        
        response, updated_session = await conversation_engine.process_message(
            sample_session,
            message,
            sample_nlp_result
        )
        
        # Verify response is not empty
        assert response is not None
        assert len(response) > 0
        
        # Verify session was updated
        assert updated_session.turn_id > sample_session.turn_id
        assert len(updated_session.memory.messages) > 0
        
        # Verify greeting response contains welcome message
        assert "bem-vindo" in response.lower() or "olá" in response.lower()
    
    @pytest.mark.asyncio
    async def test_process_budget_inquiry(
        self,
        conversation_engine,
        nlp_service,
        guardrails_service
    ):
        """Test processing a budget inquiry."""
        # Create session with consent given
        session = SessionData(
            session_id="5511999999999:1234567890",
            phone_number="5511999999999",
            state=SessionState.COLLECTING_PROFILE
        )
        session.give_consent()
        
        message = "Meu orçamento é 50 mil"
        nlp_result = await nlp_service.process(message)
        
        response, updated_session = await conversation_engine.process_message(
            session,
            message,
            nlp_result
        )
        
        # Verify budget was extracted
        assert updated_session.user_profile.orcamento_min is not None
        
        # Verify response asks for next information
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_state_transitions(
        self,
        conversation_engine,
        sample_session,
        sample_nlp_result
    ):
        """Test that state transitions work correctly."""
        sample_session.give_consent()
        sample_session.state = SessionState.COLLECTING_PROFILE
        
        message = "Quero um carro para trabalho"
        
        response, updated_session = await conversation_engine.process_message(
            sample_session,
            message,
            sample_nlp_result
        )
        
        # Verify session state is still collecting or moved forward
        assert updated_session.state in [
            SessionState.COLLECTING_PROFILE,
            SessionState.GENERATING_RECOMMENDATIONS
        ]
    
    @pytest.mark.asyncio
    async def test_human_handoff_request(
        self,
        conversation_engine,
        nlp_service,
        sample_session
    ):
        """Test human handoff request."""
        message = "Quero falar com um atendente"
        nlp_result = await nlp_service.process(message)
        
        response, updated_session = await conversation_engine.process_message(
            sample_session,
            message,
            nlp_result
        )
        
        # Verify handoff was triggered
        assert "atendente" in response.lower() or "humano" in response.lower()
        assert updated_session.state == SessionState.HUMAN_HANDOFF
    
    @pytest.mark.asyncio
    async def test_checkpoint_recovery(self, conversation_engine, sample_session):
        """Test checkpoint recovery."""
        # Get checkpoint (should be empty for new session)
        checkpoint = await conversation_engine.get_checkpoint(sample_session.session_id)
        
        # Checkpoint should be dict (empty or with data)
        assert isinstance(checkpoint, dict)
    
    @pytest.mark.asyncio
    async def test_graph_visualization(self, conversation_engine):
        """Test graph visualization generation."""
        viz = conversation_engine.get_graph_visualization()
        
        # Should return a string
        assert isinstance(viz, str)
        assert len(viz) > 0


class TestGuardrailsService:
    """Test suite for GuardrailsService."""
    
    def test_guardrails_initialization(self, guardrails_service):
        """Test that guardrails service initializes correctly."""
        assert guardrails_service is not None
        assert guardrails_service.max_recent_messages == 5
    
    def test_hash_content(self, guardrails_service):
        """Test content hashing."""
        content1 = "Hello World"
        content2 = "hello world"  # Same content, different case
        
        hash1 = guardrails_service.hash_content(content1)
        hash2 = guardrails_service.hash_content(content2)
        
        # Hashes should be the same (case-insensitive)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex chars
    
    def test_check_duplicate_exact(self, guardrails_service, sample_session):
        """Test exact duplicate detection."""
        response = "Esta é uma resposta de teste"
        
        # Add response to session history
        sample_session.add_message("assistant", response)
        
        # Check for duplicate
        is_duplicate, reformulated = guardrails_service.check_duplicate(
            response,
            sample_session
        )
        
        assert is_duplicate is True
        assert reformulated is not None
        assert reformulated != response  # Should be reformulated
    
    def test_check_duplicate_similar(self, guardrails_service, sample_session):
        """Test similar content detection."""
        response1 = "Olá! Como posso ajudar você hoje?"
        response2 = "Olá! Como posso te ajudar hoje?"
        
        # Add first response to history
        sample_session.add_message("assistant", response1)
        
        # Check if second response is similar
        is_duplicate, reformulated = guardrails_service.check_duplicate(
            response2,
            sample_session
        )
        
        # Should detect high similarity
        assert is_duplicate is True
    
    def test_style_policies_length(self, guardrails_service):
        """Test style policy for message length."""
        # Too short
        short_response = "Ok"
        is_valid, corrected, violations = guardrails_service.apply_style_policies(
            short_response
        )
        
        assert is_valid is False
        assert "too short" in str(violations).lower()
        assert len(corrected) > len(short_response)
        
        # Too long
        long_response = "A" * 1500
        is_valid, corrected, violations = guardrails_service.apply_style_policies(
            long_response
        )
        
        assert is_valid is False
        assert "too long" in str(violations).lower()
        assert len(corrected) < len(long_response)
    
    def test_filter_repetitive_patterns(self, guardrails_service):
        """Test filtering of repetitive patterns."""
        response = "muito muito bom bom"
        filtered = guardrails_service.filter_repetitive_patterns(response)
        
        # Should remove consecutive duplicates
        assert "muito muito" not in filtered
        assert "bom bom" not in filtered
    
    def test_validate_response_complete(self, guardrails_service, sample_session):
        """Test complete response validation."""
        response = "Esta é uma resposta válida e bem formatada."
        
        validated, metadata = guardrails_service.validate_response(
            response,
            sample_session
        )
        
        # Should return validated response
        assert validated is not None
        assert len(validated) > 0
        
        # Metadata should contain validation info
        assert "is_duplicate" in metadata
        assert "style_violations" in metadata
        assert "timestamp" in metadata


class TestConversationState:
    """Test suite for ConversationState TypedDict."""
    
    def test_conversation_state_structure(self):
        """Test ConversationState structure."""
        # Create a sample state
        state: ConversationState = {
            "messages": [{"role": "user", "content": "test"}],
            "session": SessionData(
                session_id="test:123",
                phone_number="5511999999999"
            ),
            "nlp_result": NLPResult(
                intent=Intent.GREETING,
                confidence=0.9,
                entities=[],
                sentiment=Sentiment.NEUTRAL,
                normalized_text="test",
                processing_time_ms=10.0
            ),
            "response": "Test response",
            "next_action": "",
            "needs_handoff": False,
            "consecutive_failures": 0,
        }
        
        # Verify all required fields are present
        assert "messages" in state
        assert "session" in state
        assert "nlp_result" in state
        assert "response" in state
        assert "next_action" in state
        assert "needs_handoff" in state
        assert "consecutive_failures" in state


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
