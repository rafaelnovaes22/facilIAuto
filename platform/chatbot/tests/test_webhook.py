"""Tests for webhook endpoints."""

import hashlib
import hmac
import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from config.settings import get_settings
from src.main import app

settings = get_settings()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def create_signature(payload: str, secret: str) -> str:
    """Create HMAC signature for webhook payload."""
    signature = hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={signature}"


class TestWebhookVerification:
    """Test webhook verification endpoint."""

    def test_verify_webhook_success(self, client):
        """Test successful webhook verification."""
        response = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.challenge": "test_challenge_123",
                "hub.verify_token": settings.whatsapp_verify_token,
            },
        )

        assert response.status_code == 200
        assert response.text == "test_challenge_123"

    def test_verify_webhook_invalid_token(self, client):
        """Test webhook verification with invalid token."""
        response = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.challenge": "test_challenge_123",
                "hub.verify_token": "invalid_token",
            },
        )

        assert response.status_code == 403

    def test_verify_webhook_missing_params(self, client):
        """Test webhook verification with missing parameters."""
        response = client.get("/webhook/whatsapp")

        assert response.status_code == 400


class TestWebhookReceive:
    """Test webhook message receiving."""

    @pytest.fixture
    def sample_message_payload(self):
        """Create sample message payload."""
        return {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "123456789",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "5511999999999",
                                    "phone_number_id": "123456789",
                                },
                                "contacts": [
                                    {
                                        "profile": {"name": "Test User"},
                                        "wa_id": "5511888888888",
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "5511888888888",
                                        "id": "wamid.test123",
                                        "timestamp": "1234567890",
                                        "text": {"body": "Olá, quero comprar um carro"},
                                        "type": "text",
                                    }
                                ],
                            },
                            "field": "messages",
                        }
                    ],
                }
            ],
        }

    @patch("src.api.webhook.is_duplicate_message")
    @patch("src.api.webhook.queue_message_processing")
    def test_receive_webhook_success(
        self,
        mock_queue,
        mock_duplicate,
        client,
        sample_message_payload,
    ):
        """Test successful webhook message reception."""
        # Mock deduplication check
        mock_duplicate.return_value = False
        mock_queue.return_value = None

        # Create payload and signature
        payload_str = json.dumps(sample_message_payload)
        signature = create_signature(payload_str, settings.whatsapp_webhook_secret)

        # Send request
        response = client.post(
            "/webhook/whatsapp",
            content=payload_str,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": signature,
            },
        )

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_receive_webhook_invalid_signature(self, client, sample_message_payload):
        """Test webhook with invalid signature."""
        payload_str = json.dumps(sample_message_payload)

        response = client.post(
            "/webhook/whatsapp",
            content=payload_str,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": "sha256=invalid_signature",
            },
        )

        assert response.status_code == 401

    def test_receive_webhook_missing_signature(self, client, sample_message_payload):
        """Test webhook with missing signature."""
        payload_str = json.dumps(sample_message_payload)

        response = client.post(
            "/webhook/whatsapp",
            content=payload_str,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 401

    def test_receive_webhook_invalid_payload(self, client):
        """Test webhook with invalid JSON payload."""
        payload_str = "invalid json"
        signature = create_signature(payload_str, settings.whatsapp_webhook_secret)

        response = client.post(
            "/webhook/whatsapp",
            content=payload_str,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": signature,
            },
        )

        assert response.status_code == 400


class TestMessageDeduplication:
    """Test message deduplication."""

    @pytest.mark.asyncio
    @patch("src.api.webhook.get_redis_client")
    async def test_duplicate_message_detected(self, mock_redis):
        """Test duplicate message detection."""
        from src.api.webhook import is_duplicate_message

        # Mock Redis client
        mock_redis_instance = AsyncMock()
        mock_redis_instance.exists.return_value = True
        mock_redis.return_value = mock_redis_instance

        result = await is_duplicate_message("test_message_id")

        assert result is True
        mock_redis_instance.exists.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.api.webhook.get_redis_client")
    async def test_new_message_not_duplicate(self, mock_redis):
        """Test new message is not duplicate."""
        from src.api.webhook import is_duplicate_message

        # Mock Redis client
        mock_redis_instance = AsyncMock()
        mock_redis_instance.exists.return_value = False
        mock_redis_instance.setex.return_value = True
        mock_redis.return_value = mock_redis_instance

        result = await is_duplicate_message("test_message_id")

        assert result is False
        mock_redis_instance.exists.assert_called_once()
        mock_redis_instance.setex.assert_called_once()
