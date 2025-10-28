"""WhatsApp Business API client for sending messages."""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class WhatsAppClient:
    """Client for WhatsApp Business API."""

    def __init__(self):
        """Initialize WhatsApp client."""
        self.api_url = settings.whatsapp_api_url
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.access_token = settings.whatsapp_access_token
        self.base_url = f"{self.api_url}/{self.phone_number_id}/messages"

        # HTTP client with timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
        )

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send request to WhatsApp API with retry logic.

        Args:
            payload: Request payload

        Returns:
            API response

        Raises:
            httpx.HTTPError: If request fails after retries
        """
        try:
            response = await self.client.post(
                self.base_url,
                json=payload,
                headers=self._build_headers(),
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Message sent successfully: {result}")
            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending message: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.TimeoutException as e:
            logger.error(f"Timeout sending message: {e}")
            raise
        except httpx.NetworkError as e:
            logger.error(f"Network error sending message: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            raise

    async def send_text_message(
        self,
        to: str,
        text: str,
        preview_url: bool = False,
    ) -> Dict[str, Any]:
        """
        Send text message to WhatsApp user.

        Args:
            to: Recipient phone number (with country code, no + sign)
            text: Message text (max 4096 characters)
            preview_url: Whether to show URL preview

        Returns:
            API response with message ID

        Example:
            >>> client = WhatsAppClient()
            >>> await client.send_text_message(
            ...     to="5511999999999",
            ...     text="Olá! Bem-vindo ao FacilIAuto!"
            ... )
        """
        if not text or len(text) > 4096:
            raise ValueError("Text must be between 1 and 4096 characters")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": text,
            },
        }

        logger.info(f"Sending text message to {to}")
        return await self._send_request(payload)

    async def send_image_message(
        self,
        to: str,
        image_url: str,
        caption: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send image message to WhatsApp user.

        Args:
            to: Recipient phone number
            image_url: Public URL of the image (HTTPS required)
            caption: Optional image caption (max 1024 characters)

        Returns:
            API response with message ID

        Example:
            >>> await client.send_image_message(
            ...     to="5511999999999",
            ...     image_url="https://example.com/car.jpg",
            ...     caption="Honda Civic 2023"
            ... )
        """
        if not image_url.startswith("https://"):
            raise ValueError("Image URL must use HTTPS")

        if caption and len(caption) > 1024:
            raise ValueError("Caption must be max 1024 characters")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "image",
            "image": {
                "link": image_url,
            },
        }

        if caption:
            payload["image"]["caption"] = caption

        logger.info(f"Sending image message to {to}")
        return await self._send_request(payload)

    async def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str = "pt_BR",
        components: Optional[list[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send template message to WhatsApp user.

        Template messages are pre-approved message formats used for
        notifications and marketing messages.

        Args:
            to: Recipient phone number
            template_name: Name of the approved template
            language_code: Template language (default: pt_BR)
            components: Template components (parameters, buttons, etc)

        Returns:
            API response with message ID

        Example:
            >>> await client.send_template_message(
            ...     to="5511999999999",
            ...     template_name="welcome_message",
            ...     components=[
            ...         {
            ...             "type": "body",
            ...             "parameters": [
            ...                 {"type": "text", "text": "João"}
            ...             ]
            ...         }
            ...     ]
            ... )
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code,
                },
            },
        }

        if components:
            payload["template"]["components"] = components

        logger.info(f"Sending template message '{template_name}' to {to}")
        return await self._send_request(payload)

    async def send_interactive_message(
        self,
        to: str,
        body_text: str,
        buttons: list[Dict[str, str]],
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send interactive message with buttons.

        Args:
            to: Recipient phone number
            body_text: Main message text
            buttons: List of buttons (max 3), each with 'id' and 'title'
            header_text: Optional header text
            footer_text: Optional footer text

        Returns:
            API response with message ID

        Example:
            >>> await client.send_interactive_message(
            ...     to="5511999999999",
            ...     body_text="Escolha uma opção:",
            ...     buttons=[
            ...         {"id": "opt1", "title": "Ver carros"},
            ...         {"id": "opt2", "title": "Falar com vendedor"}
            ...     ]
            ... )
        """
        if not buttons or len(buttons) > 3:
            raise ValueError("Must provide 1-3 buttons")

        # Build interactive payload
        interactive = {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": btn["id"],
                            "title": btn["title"][:20],  # Max 20 chars
                        },
                    }
                    for btn in buttons
                ]
            },
        }

        if header_text:
            interactive["header"] = {"type": "text", "text": header_text}

        if footer_text:
            interactive["footer"] = {"text": footer_text}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": interactive,
        }

        logger.info(f"Sending interactive message to {to}")
        return await self._send_request(payload)

    async def mark_message_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mark message as read.

        Args:
            message_id: WhatsApp message ID

        Returns:
            API response
        """
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }

        logger.info(f"Marking message {message_id} as read")
        return await self._send_request(payload)


# Global client instance
_whatsapp_client: Optional[WhatsAppClient] = None


async def get_whatsapp_client() -> WhatsAppClient:
    """
    Get or create WhatsApp client instance.

    Returns:
        WhatsApp client
    """
    global _whatsapp_client

    if _whatsapp_client is None:
        _whatsapp_client = WhatsAppClient()

    return _whatsapp_client


async def close_whatsapp_client() -> None:
    """Close WhatsApp client."""
    global _whatsapp_client

    if _whatsapp_client is not None:
        await _whatsapp_client.close()
        _whatsapp_client = None
        logger.info("WhatsApp client closed")
