"""
Serviço de validação de imagens para o sistema FacilIAuto
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, cast

import aiohttp
from pydantic import BaseModel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageValidationError(Enum):
    """Tipos de erros de validação de imagem"""

    NETWORK_ERROR = "network_error"
    NOT_FOUND = "not_found"
    TIMEOUT = "timeout"
    INVALID_FORMAT = "invalid_format"
    ACCESS_DENIED = "access_denied"
    SERVER_ERROR = "server_error"
    UNKNOWN_ERROR = "unknown_error"


class ImageValidationResult(BaseModel):
    """Resultado da validação de uma imagem"""

    url: str
    is_valid: bool
    error_type: Optional[ImageValidationError] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    validated_at: datetime = datetime.now()


class ImageValidationService:
    """Serviço para validação de URLs de imagens"""

    def __init__(self, timeout: int = 10, max_concurrent: int = 10):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.session: Optional[aiohttp.ClientSession] = None

        # Tipos de conteúdo válidos para imagens
        self.valid_content_types = {
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
            "image/bmp",
        }

    async def __aenter__(self):
        """Context manager para gerenciar sessão HTTP"""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": "FacilIAuto-ImageValidator/1.0"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fechar sessão HTTP"""
        if self.session:
            await self.session.close()

    async def validate_image_url(self, url: str) -> ImageValidationResult:
        """
        Valida uma única URL de imagem

        Args:
            url: URL da imagem para validar

        Returns:
            ImageValidationResult com detalhes da validação
        """
        start_time = datetime.now()

        try:
            # Verificar se a URL é válida
            if not url or not url.startswith(("http://", "https://")):
                return ImageValidationResult(
                    url=url,
                    is_valid=False,
                    error_type=ImageValidationError.INVALID_FORMAT,
                    error_message="URL inválida ou não é HTTP/HTTPS",
                )

            # Fazer requisição HEAD primeiro (mais rápido)
            if self.session is None:
                raise RuntimeError(
                    "ClientSession não inicializada. Use como context manager."
                )
            async with self.session.head(url) as response:
                response_time = int(
                    (datetime.now() - start_time).total_seconds() * 1000
                )

                # Verificar status code
                if response.status == 200:
                    content_type = response.headers.get("content-type", "").lower()
                    content_length = response.headers.get("content-length")

                    # Verificar se é realmente uma imagem
                    if any(ct in content_type for ct in self.valid_content_types):
                        return ImageValidationResult(
                            url=url,
                            is_valid=True,
                            response_time_ms=response_time,
                            content_type=content_type,
                            content_length=int(content_length)
                            if content_length
                            else None,
                        )
                    else:
                        return ImageValidationResult(
                            url=url,
                            is_valid=False,
                            error_type=ImageValidationError.INVALID_FORMAT,
                            error_message=f"Tipo de conteúdo inválido: {content_type}",
                            response_time_ms=response_time,
                        )

                elif response.status == 404:
                    return ImageValidationResult(
                        url=url,
                        is_valid=False,
                        error_type=ImageValidationError.NOT_FOUND,
                        error_message="Imagem não encontrada (404)",
                        response_time_ms=response_time,
                    )

                elif response.status == 403:
                    return ImageValidationResult(
                        url=url,
                        is_valid=False,
                        error_type=ImageValidationError.ACCESS_DENIED,
                        error_message="Acesso negado (403)",
                        response_time_ms=response_time,
                    )

                elif response.status >= 500:
                    return ImageValidationResult(
                        url=url,
                        is_valid=False,
                        error_type=ImageValidationError.SERVER_ERROR,
                        error_message=f"Erro do servidor ({response.status})",
                        response_time_ms=response_time,
                    )

                else:
                    return ImageValidationResult(
                        url=url,
                        is_valid=False,
                        error_type=ImageValidationError.UNKNOWN_ERROR,
                        error_message=f"Status HTTP inesperado: {response.status}",
                        response_time_ms=response_time,
                    )

        except asyncio.TimeoutError:
            return ImageValidationResult(
                url=url,
                is_valid=False,
                error_type=ImageValidationError.TIMEOUT,
                error_message=f"Timeout após {self.timeout} segundos",
            )

        except aiohttp.ClientError as e:
            return ImageValidationResult(
                url=url,
                is_valid=False,
                error_type=ImageValidationError.NETWORK_ERROR,
                error_message=f"Erro de rede: {str(e)}",
            )

        except Exception as e:
            logger.error(f"Erro inesperado ao validar {url}: {str(e)}")
            return ImageValidationResult(
                url=url,
                is_valid=False,
                error_type=ImageValidationError.UNKNOWN_ERROR,
                error_message=f"Erro inesperado: {str(e)}",
            )

    async def validate_multiple_urls(
        self, urls: List[str]
    ) -> List[ImageValidationResult]:
        """
        Valida múltiplas URLs de imagem em paralelo

        Args:
            urls: Lista de URLs para validar

        Returns:
            Lista de ImageValidationResult
        """
        if not urls:
            return []

        # Limitar concorrência para não sobrecarregar os servidores
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def validate_with_semaphore(url: str) -> ImageValidationResult:
            async with semaphore:
                return await self.validate_image_url(url)

        # Executar validações em paralelo
        tasks = [validate_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Processar resultados e tratar exceções
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Erro ao validar URL {urls[i]}: {str(result)}")
                processed_results.append(
                    ImageValidationResult(
                        url=urls[i],
                        is_valid=False,
                        error_type=ImageValidationError.UNKNOWN_ERROR,
                        error_message=f"Erro na validação: {str(result)}",
                    )
                )
            else:
                processed_results.append(cast(ImageValidationResult, result))

        return processed_results

    def get_validation_summary(
        self, results: List[ImageValidationResult]
    ) -> Dict[str, Any]:
        """
        Gera um resumo dos resultados de validação

        Args:
            results: Lista de resultados de validação

        Returns:
            Dicionário com estatísticas de validação
        """
        if not results:
            return {"total": 0, "valid": 0, "invalid": 0, "error_breakdown": {}}

        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        invalid = total - valid

        # Contar tipos de erro
        error_breakdown: Dict[str, int] = {}
        for result in results:
            if not result.is_valid and result.error_type:
                error_type = result.error_type.value
                error_breakdown[error_type] = error_breakdown.get(error_type, 0) + 1

        # Calcular tempo médio de resposta
        response_times = [
            r.response_time_ms for r in results if r.response_time_ms is not None
        ]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else None
        )

        return {
            "total": total,
            "valid": valid,
            "invalid": invalid,
            "success_rate": round((valid / total) * 100, 2),
            "error_breakdown": error_breakdown,
            "avg_response_time_ms": round(avg_response_time, 2)
            if avg_response_time
            else None,
        }


# Função utilitária para uso simples
async def validate_image_urls(
    urls: List[str], timeout: int = 10
) -> List[ImageValidationResult]:
    """
    Função utilitária para validar URLs de imagem

    Args:
        urls: Lista de URLs para validar
        timeout: Timeout em segundos para cada requisição

    Returns:
        Lista de resultados de validação
    """
    async with ImageValidationService(timeout=timeout) as validator:
        return await validator.validate_multiple_urls(urls)


# Função síncrona para compatibilidade
def validate_image_urls_sync(
    urls: List[str], timeout: int = 10
) -> List[ImageValidationResult]:
    """
    Versão síncrona da validação de URLs

    Args:
        urls: Lista de URLs para validar
        timeout: Timeout em segundos para cada requisição

    Returns:
        Lista de resultados de validação
    """
    return asyncio.run(validate_image_urls(urls, timeout))
