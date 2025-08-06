"""
Testes unitários para o serviço de validação de imagens
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.image_validation import (
    ImageValidationError,
    ImageValidationResult,
    ImageValidationService,
    validate_image_urls,
    validate_image_urls_sync,
)


class TestImageValidationService:
    """Testes para a classe ImageValidationService"""

    @pytest.mark.asyncio
    async def test_validate_valid_image_url(self):
        """Testa validação de URL de imagem válida"""
        service = ImageValidationService()

        # Mock da resposta HTTP
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {
            "content-type": "image/jpeg",
            "content-length": "12345",
        }

        with patch("aiohttp.ClientSession.head") as mock_head:
            mock_head.return_value.__aenter__.return_value = mock_response
            service.session = AsyncMock()

            result = await service.validate_image_url("https://example.com/image.jpg")

            assert result.is_valid is True
            assert result.url == "https://example.com/image.jpg"
            assert result.error_type is None
            assert result.content_type == "image/jpeg"
            assert result.content_length == 12345

    @pytest.mark.asyncio
    async def test_validate_invalid_url_format(self):
        """Testa validação de URL com formato inválido"""
        service = ImageValidationService()

        result = await service.validate_image_url("invalid-url")

        assert result.is_valid is False
        assert result.error_type == ImageValidationError.INVALID_FORMAT
        assert "URL inválida" in result.error_message

    @pytest.mark.asyncio
    async def test_validate_not_found_image(self):
        """Testa validação de imagem não encontrada (404)"""
        service = ImageValidationService()

        mock_response = AsyncMock()
        mock_response.status = 404

        with patch("aiohttp.ClientSession.head") as mock_head:
            mock_head.return_value.__aenter__.return_value = mock_response
            service.session = AsyncMock()

            result = await service.validate_image_url(
                "https://example.com/notfound.jpg"
            )

            assert result.is_valid is False
            assert result.error_type == ImageValidationError.NOT_FOUND
            assert "404" in result.error_message

    @pytest.mark.asyncio
    async def test_validate_invalid_content_type(self):
        """Testa validação de URL que não é imagem"""
        service = ImageValidationService()

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"content-type": "text/html", "content-length": "1000"}

        with patch("aiohttp.ClientSession.head") as mock_head:
            mock_head.return_value.__aenter__.return_value = mock_response
            service.session = AsyncMock()

            result = await service.validate_image_url("https://example.com/page.html")

            assert result.is_valid is False
            assert result.error_type == ImageValidationError.INVALID_FORMAT
            assert "text/html" in result.error_message

    @pytest.mark.asyncio
    async def test_validate_timeout_error(self):
        """Testa tratamento de timeout"""
        service = ImageValidationService(timeout=1)

        with patch("aiohttp.ClientSession.head") as mock_head:
            mock_head.side_effect = asyncio.TimeoutError()
            service.session = AsyncMock()

            result = await service.validate_image_url(
                "https://slow-server.com/image.jpg"
            )

            assert result.is_valid is False
            assert result.error_type == ImageValidationError.TIMEOUT
            assert "Timeout" in result.error_message

    @pytest.mark.asyncio
    async def test_validate_multiple_urls(self):
        """Testa validação de múltiplas URLs"""
        service = ImageValidationService()

        urls = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.png",
            "invalid-url",
        ]

        # Mock das respostas
        mock_response_1 = AsyncMock()
        mock_response_1.status = 200
        mock_response_1.headers = {"content-type": "image/jpeg"}

        mock_response_2 = AsyncMock()
        mock_response_2.status = 200
        mock_response_2.headers = {"content-type": "image/png"}

        with patch("aiohttp.ClientSession.head") as mock_head:
            mock_head.return_value.__aenter__.side_effect = [
                mock_response_1,
                mock_response_2,
            ]
            service.session = AsyncMock()

            results = await service.validate_multiple_urls(urls)

            assert len(results) == 3
            assert results[0].is_valid is True  # image1.jpg
            assert results[1].is_valid is True  # image2.png
            assert results[2].is_valid is False  # invalid-url

    def test_get_validation_summary(self):
        """Testa geração de resumo de validação"""
        service = ImageValidationService()

        results = [
            ImageValidationResult(url="url1", is_valid=True),
            ImageValidationResult(
                url="url2", is_valid=False, error_type=ImageValidationError.NOT_FOUND
            ),
            ImageValidationResult(
                url="url3", is_valid=False, error_type=ImageValidationError.TIMEOUT
            ),
            ImageValidationResult(url="url4", is_valid=True, response_time_ms=100),
        ]

        summary = service.get_validation_summary(results)

        assert summary["total"] == 4
        assert summary["valid"] == 2
        assert summary["invalid"] == 2
        assert summary["success_rate"] == 50.0
        assert summary["error_breakdown"]["not_found"] == 1
        assert summary["error_breakdown"]["timeout"] == 1


class TestUtilityFunctions:
    """Testes para funções utilitárias"""

    @pytest.mark.asyncio
    async def test_validate_image_urls_function(self):
        """Testa função utilitária assíncrona"""
        urls = ["https://example.com/image.jpg"]

        with patch("app.image_validation.ImageValidationService") as mock_service_class:
            mock_service = AsyncMock()
            mock_service.validate_multiple_urls.return_value = [
                ImageValidationResult(url=urls[0], is_valid=True)
            ]
            mock_service_class.return_value.__aenter__.return_value = mock_service

            results = await validate_image_urls(urls)

            assert len(results) == 1
            assert results[0].is_valid is True

    def test_validate_image_urls_sync_function(self):
        """Testa função utilitária síncrona"""
        urls = ["https://example.com/image.jpg"]

        with patch("asyncio.run") as mock_run:
            mock_run.return_value = [ImageValidationResult(url=urls[0], is_valid=True)]

            results = validate_image_urls_sync(urls)

            assert len(results) == 1
            mock_run.assert_called_once()


class TestImageValidationResult:
    """Testes para o modelo ImageValidationResult"""

    def test_create_valid_result(self):
        """Testa criação de resultado válido"""
        result = ImageValidationResult(
            url="https://example.com/image.jpg",
            is_valid=True,
            content_type="image/jpeg",
            response_time_ms=150,
        )

        assert result.url == "https://example.com/image.jpg"
        assert result.is_valid is True
        assert result.content_type == "image/jpeg"
        assert result.response_time_ms == 150
        assert result.error_type is None

    def test_create_invalid_result(self):
        """Testa criação de resultado inválido"""
        result = ImageValidationResult(
            url="https://example.com/notfound.jpg",
            is_valid=False,
            error_type=ImageValidationError.NOT_FOUND,
            error_message="Image not found",
        )

        assert result.url == "https://example.com/notfound.jpg"
        assert result.is_valid is False
        assert result.error_type == ImageValidationError.NOT_FOUND
        assert result.error_message == "Image not found"


# Fixtures para testes
@pytest.fixture
def sample_urls():
    """URLs de exemplo para testes"""
    return [
        "https://example.com/valid-image.jpg",
        "https://example.com/another-image.png",
        "https://broken-link.com/missing.jpg",
        "invalid-url-format",
    ]


@pytest.fixture
def mock_validation_results():
    """Resultados de validação de exemplo"""
    return [
        ImageValidationResult(url="url1", is_valid=True, response_time_ms=100),
        ImageValidationResult(
            url="url2", is_valid=False, error_type=ImageValidationError.NOT_FOUND
        ),
        ImageValidationResult(url="url3", is_valid=True, response_time_ms=200),
        ImageValidationResult(
            url="url4", is_valid=False, error_type=ImageValidationError.TIMEOUT
        ),
    ]
