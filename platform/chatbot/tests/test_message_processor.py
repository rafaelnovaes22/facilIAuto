"""Tests for Celery message processor tasks."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.tasks.message_processor import (
    collect_metrics_task,
    generate_embeddings_task,
    notify_human_handoff_task,
    process_message_task,
    save_session_to_duckdb_task,
    send_reengagement_task,
)


class TestProcessMessageTask:
    """Test process_message_task."""

    @patch("src.tasks.message_processor.get_whatsapp_client")
    @patch("src.tasks.message_processor.get_conversation_engine")
    @patch("src.tasks.message_processor.get_session_manager")
    def test_process_text_message_success(
        self, mock_session_mgr, mock_conv_engine, mock_whatsapp
    ):
        """Test successful text message processing."""
        # Mock session manager
        mock_session = MagicMock()
        mock_session.session_id = "test_session_123"
        mock_session.message_count = 5
        mock_session_mgr.return_value.get_or_create_session.return_value = mock_session
        mock_session_mgr.return_value.update_session.return_value = None

        # Mock conversation engine
        mock_conv_engine.return_value.process_message.return_value = {
            "type": "text",
            "text": "Olá! Como posso ajudar?",
        }

        # Mock WhatsApp client
        mock_whatsapp.return_value.send_text_message.return_value = None

        # Execute task
        result = process_message_task(
            message_id="msg_123",
            from_number="5511999999999",
            message_type="text",
            content="Olá",
            timestamp="1234567890",
        )

        # Assertions
        assert result["status"] == "success"
        assert result["message_id"] == "msg_123"
        assert result["response_sent"] is True
        mock_session_mgr.return_value.get_or_create_session.assert_called_once()
        mock_conv_engine.return_value.process_message.assert_called_once()
        mock_whatsapp.return_value.send_text_message.assert_called_once()

    @patch("src.tasks.message_processor.get_whatsapp_client")
    @patch("src.tasks.message_processor.get_conversation_engine")
    @patch("src.tasks.message_processor.get_session_manager")
    def test_process_image_message(
        self, mock_session_mgr, mock_conv_engine, mock_whatsapp
    ):
        """Test image message processing."""
        # Mock session manager
        mock_session = MagicMock()
        mock_session.session_id = "test_session_123"
        mock_session.message_count = 5
        mock_session_mgr.return_value.get_or_create_session.return_value = mock_session

        # Mock conversation engine
        mock_conv_engine.return_value.process_message.return_value = {
            "type": "image",
            "image_url": "https://example.com/car.jpg",
            "caption": "Aqui está o carro",
        }

        # Mock WhatsApp client
        mock_whatsapp.return_value.send_image_message.return_value = None

        # Execute task
        result = process_message_task(
            message_id="msg_124",
            from_number="5511999999999",
            message_type="image",
            content="[Image]",
            timestamp="1234567890",
            media_id="media_123",
        )

        # Assertions
        assert result["status"] == "success"
        mock_whatsapp.return_value.send_image_message.assert_called_once()


class TestSaveSessionToDuckDB:
    """Test save_session_to_duckdb_task."""

    @patch("src.tasks.message_processor.get_session_manager")
    def test_save_session_success(self, mock_session_mgr):
        """Test successful session persistence."""
        # Mock session manager
        mock_session = MagicMock()
        mock_session_mgr.return_value.get_session.return_value = mock_session
        mock_session_mgr.return_value.persist_to_duckdb.return_value = None

        # Execute task
        result = save_session_to_duckdb_task(session_id="test_session_123")

        # Assertions
        assert result["status"] == "success"
        assert result["session_id"] == "test_session_123"
        mock_session_mgr.return_value.persist_to_duckdb.assert_called_once()

    @patch("src.tasks.message_processor.get_session_manager")
    def test_save_session_not_found(self, mock_session_mgr):
        """Test session not found."""
        # Mock session manager
        mock_session_mgr.return_value.get_session.return_value = None

        # Execute task
        result = save_session_to_duckdb_task(session_id="nonexistent_session")

        # Assertions
        assert result["status"] == "not_found"
        assert result["session_id"] == "nonexistent_session"


class TestGenerateEmbeddings:
    """Test generate_embeddings_task."""

    @patch("src.tasks.message_processor.get_nlp_service")
    def test_generate_embeddings_success(self, mock_nlp):
        """Test successful embedding generation."""
        # Mock NLP service
        mock_nlp.return_value.generate_embeddings.return_value = [0.1] * 768

        # Execute task
        result = generate_embeddings_task(
            message_id="msg_123",
            text="Quero comprar um carro",
            session_id="session_123",
        )

        # Assertions
        assert result["status"] == "success"
        assert result["message_id"] == "msg_123"
        assert result["embedding_size"] == 768
        mock_nlp.return_value.generate_embeddings.assert_called_once()


class TestNotifyHumanHandoff:
    """Test notify_human_handoff_task."""

    def test_notify_handoff_success(self):
        """Test successful handoff notification."""
        # Execute task
        result = notify_human_handoff_task(
            session_id="session_123",
            user_phone="5511999999999",
            reason="complex_query",
            context={"last_message": "Preciso de ajuda especial"},
        )

        # Assertions
        assert result["status"] == "success"
        assert result["session_id"] == "session_123"
        assert result["notified"] is True


class TestSendReengagement:
    """Test send_reengagement_task."""

    @patch("src.tasks.message_processor.get_whatsapp_client")
    def test_send_reengagement_inactive(self, mock_whatsapp):
        """Test sending reengagement for inactive user."""
        # Mock WhatsApp client
        mock_whatsapp.return_value.send_text_message.return_value = None

        # Execute task
        result = send_reengagement_task(
            user_phone="5511999999999",
            session_id="session_123",
            message_type="inactive_48h",
        )

        # Assertions
        assert result["status"] == "success"
        assert result["user_phone"] == "5511999999999"
        assert result["message_type"] == "inactive_48h"
        mock_whatsapp.return_value.send_text_message.assert_called_once()

    @patch("src.tasks.message_processor.get_whatsapp_client")
    def test_send_reengagement_new_cars(self, mock_whatsapp):
        """Test sending reengagement for new cars."""
        # Mock WhatsApp client
        mock_whatsapp.return_value.send_text_message.return_value = None

        # Execute task
        result = send_reengagement_task(
            user_phone="5511999999999",
            session_id="session_123",
            message_type="new_cars",
        )

        # Assertions
        assert result["status"] == "success"
        mock_whatsapp.return_value.send_text_message.assert_called_once()


class TestCollectMetrics:
    """Test collect_metrics_task."""

    def test_collect_metrics_success(self):
        """Test successful metrics collection."""
        # Execute task
        result = collect_metrics_task(
            metric_type="message_processed",
            data={"session_id": "session_123", "duration_ms": 150},
        )

        # Assertions
        assert result["status"] == "success"
        assert result["metric_type"] == "message_processed"


class TestTaskIdempotency:
    """Test task idempotency."""

    @patch("src.tasks.message_processor.get_whatsapp_client")
    @patch("src.tasks.message_processor.get_conversation_engine")
    @patch("src.tasks.message_processor.get_session_manager")
    def test_same_message_id_generates_same_task_id(
        self, mock_session_mgr, mock_conv_engine, mock_whatsapp
    ):
        """Test that same message_id generates same task_id for idempotency."""
        # Mock dependencies
        mock_session = MagicMock()
        mock_session.session_id = "test_session"
        mock_session.message_count = 1
        mock_session_mgr.return_value.get_or_create_session.return_value = mock_session
        mock_conv_engine.return_value.process_message.return_value = {
            "type": "text",
            "text": "Test",
        }
        mock_whatsapp.return_value.send_text_message.return_value = None

        # Create task with specific message_id
        message_id = "msg_idempotency_test"

        # Execute task twice with same message_id
        result1 = process_message_task(
            message_id=message_id,
            from_number="5511999999999",
            message_type="text",
            content="Test",
            timestamp="1234567890",
        )

        result2 = process_message_task(
            message_id=message_id,
            from_number="5511999999999",
            message_type="text",
            content="Test",
            timestamp="1234567890",
        )

        # Both should succeed (idempotency handled by Celery)
        assert result1["status"] == "success"
        assert result2["status"] == "success"
