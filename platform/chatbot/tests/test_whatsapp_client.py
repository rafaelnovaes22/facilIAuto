"""Tests for WhatsApp client."""

import pytest
from httpx import AsyncClient, Response
from unittest.mock import AsyncMock, patch

from src.services.whatsapp_client import WhatsAppClient


@pytest.fixture
def whatsapp_client():
    """Create WhatsApp client instance."""
    return WhatsAppClient()


@pytest.fixture
def mock_response():
    """Create mock HTTP response."""
    return {
        "messaging_product": "whatsapp",
        "contacts": [{"input": "5511999999999", "wa_id": "5511999999999"}],
        "messages": [{"id": "wamid.test123"}],
    }


class TestSendTextMessage:
    """Test sending text messages."""

    @pytest.mark.asyncio
    @patch.object(AsyncClient, "post")
    async def test_send_text_message_success(
        self, mock_post, whatsapp_client, mock_response
    ):
        """Test successful text message sending."""
        # Mock HTTP response
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_response,
        )
        mock_post.return_value.raise_for_status = lambda: None

        result = await whatsapp_client.send_text_message(
            to="5511999999999",
            text="Olá! Bem-vindo ao FacilIAuto!",
        )

        assert result == mock_response
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_text_message_empty_text(self, whatsapp_client):
        """Test sending empty text message."""
        with pytest.raises(ValueError, match="Text must be between"):
            await whatsapp_client.send_text_message(
                to="5511999999999",
                text="",
            )

    @pytest.mark.asyncio
    async def test_send_text_message_too_long(self, whatsapp_client):
        """Test sending text message that's too long."""
        long_text = "a" * 5000  # Exceeds 4096 character limit

        with pytest.raises(ValueError, match="Text must be between"):
            await whatsapp_client.send_text_message(
                to="5511999999999",
                text=long_text,
            )


class TestSendImageMessage:
    """Test sending image messages."""

    @pytest.mark.asyncio
    @patch.object(AsyncClient, "post")
    async def test_send_image_message_success(
        self, mock_post, whatsapp_client, mock_response
    ):
        """Test successful image message sending."""
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_response,
        )
        mock_post.return_value.raise_for_status = lambda: None

        result = await whatsapp_client.send_image_message(
            to="5511999999999",
            image_url="https://example.com/car.jpg",
            caption="Honda Civic 2023",
        )

        assert result == mock_response
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_image_message_invalid_url(self, whatsapp_client):
        """Test sending image with non-HTTPS URL."""
        with pytest.raises(ValueError, match="Image URL must use HTTPS"):
            await whatsapp_client.send_image_message(
                to="5511999999999",
                image_url="http://example.com/car.jpg",
            )

    @pytest.mark.asyncio
    async def test_send_image_message_caption_too_long(self, whatsapp_client):
        """Test sending image with caption that's too long."""
        long_caption = "a" * 2000  # Exceeds 1024 character limit

        with pytest.raises(ValueError, match="Caption must be max"):
            await whatsapp_client.send_image_message(
                to="5511999999999",
                image_url="https://example.com/car.jpg",
                caption=long_caption,
            )


class TestSendTemplateMessage:
    """Test sending template messages."""

    @pytest.mark.asyncio
    @patch.object(AsyncClient, "post")
    async def test_send_template_message_success(
        self, mock_post, whatsapp_client, mock_response
    ):
        """Test successful template message sending."""
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_response,
        )
        mock_post.return_value.raise_for_status = lambda: None

        result = await whatsapp_client.send_template_message(
            to="5511999999999",
            template_name="welcome_message",
            components=[
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": "João"}],
                }
            ],
        )

        assert result == mock_response
        mock_post.assert_called_once()


class TestSendInteractiveMessage:
    """Test sending interactive messages."""

    @pytest.mark.asyncio
    @patch.object(AsyncClient, "post")
    async def test_send_interactive_message_success(
        self, mock_post, whatsapp_client, mock_response
    ):
        """Test successful interactive message sending."""
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_response,
        )
        mock_post.return_value.raise_for_status = lambda: None

        result = await whatsapp_client.send_interactive_message(
            to="5511999999999",
            body_text="Escolha uma opção:",
            buttons=[
                {"id": "opt1", "title": "Ver carros"},
                {"id": "opt2", "title": "Falar com vendedor"},
            ],
        )

        assert result == mock_response
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_interactive_message_too_many_buttons(self, whatsapp_client):
        """Test sending interactive message with too many buttons."""
        with pytest.raises(ValueError, match="Must provide 1-3 buttons"):
            await whatsapp_client.send_interactive_message(
                to="5511999999999",
                body_text="Escolha uma opção:",
                buttons=[
                    {"id": "opt1", "title": "Option 1"},
                    {"id": "opt2", "title": "Option 2"},
                    {"id": "opt3", "title": "Option 3"},
                    {"id": "opt4", "title": "Option 4"},
                ],
            )

    @pytest.mark.asyncio
    async def test_send_interactive_message_no_buttons(self, whatsapp_client):
        """Test sending interactive message with no buttons."""
        with pytest.raises(ValueError, match="Must provide 1-3 buttons"):
            await whatsapp_client.send_interactive_message(
                to="5511999999999",
                body_text="Escolha uma opção:",
                buttons=[],
            )


class TestRetryLogic:
    """Test retry logic for failed requests."""

    @pytest.mark.asyncio
    @patch.object(AsyncClient, "post")
    async def test_retry_on_timeout(self, mock_post, whatsapp_client):
        """Test retry on timeout error."""
        from httpx import TimeoutException

        # First two calls timeout, third succeeds
        mock_post.side_effect = [
            TimeoutException("Timeout"),
            TimeoutException("Timeout"),
            AsyncMock(
                status_code=200,
                json=lambda: {"messages": [{"id": "test"}]},
                raise_for_status=lambda: None,
            ),
        ]

        result = await whatsapp_client.send_text_message(
            to="5511999999999",
            text="Test message",
        )

        assert result == {"messages": [{"id": "test"}]}
        assert mock_post.call_count == 3
