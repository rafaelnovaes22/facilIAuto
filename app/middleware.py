"""
🔍 Middleware de Logging e Métricas - FacilIAuto
Intercepta requisições para adicionar logging estruturado e coleta de métricas
"""
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_config import (
    clear_correlation_context,
    generate_correlation_id,
    get_logger,
    metrics_collector,
    set_correlation_context,
)

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que adiciona logging estruturado e coleta de métricas
    para todas as requisições HTTP
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Intercepta requisições para adicionar contexto de logging

        Args:
            request: Requisição HTTP
            call_next: Próximo middleware/handler

        Returns:
            Response HTTP com headers de correlação
        """
        # Gera correlation ID único para esta requisição
        correlation_id = generate_correlation_id()
        start_time = time.time()

        # Define contexto para logs
        set_correlation_context(correlation_id, start_time)

        # Extrai informações da requisição
        method = request.method
        url = str(request.url)
        path = request.url.path
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")

        # Log de início da requisição
        logger.info(
            f"Request started: {method} {path}",
            method=method,
            path=path,
            url=url,
            client_ip=client_ip,
            user_agent=user_agent,
            correlation_id=correlation_id,
        )

        try:
            # Executa a requisição
            response = await call_next(request)

            # Calcula tempo de resposta
            response_time = time.time() - start_time
            status_code = response.status_code

            # Adiciona header de correlação na resposta
            response.headers["X-Correlation-ID"] = correlation_id

            # Registra métricas
            metrics_collector.record_request(
                endpoint=self._normalize_endpoint(path),
                response_time=response_time,
                status_code=status_code,
            )

            # Log de conclusão da requisição
            log_level = "error" if status_code >= 400 else "info"
            getattr(logger, log_level)(
                f"Request completed: {method} {path} - {status_code}",
                method=method,
                path=path,
                status_code=status_code,
                response_time_ms=round(response_time * 1000, 2),
                correlation_id=correlation_id,
            )

            return response

        except Exception as exc:
            # Calcula tempo até o erro
            response_time = time.time() - start_time

            # Registra métricas de erro
            metrics_collector.record_request(
                endpoint=self._normalize_endpoint(path),
                response_time=response_time,
                status_code=500,
            )

            # Log de erro
            logger.error(
                f"Request failed: {method} {path} - {type(exc).__name__}",
                method=method,
                path=path,
                exception_type=type(exc).__name__,
                exception_message=str(exc),
                response_time_ms=round(response_time * 1000, 2),
                correlation_id=correlation_id,
            )

            # Re-raise a exceção para que o FastAPI possa lidar com ela
            raise exc

        finally:
            # Limpa contexto da requisição
            clear_correlation_context()

    def _get_client_ip(self, request: Request) -> str:
        """
        Extrai IP do cliente considerando proxies

        Args:
            request: Requisição HTTP

        Returns:
            Endereço IP do cliente
        """
        # Verifica headers de proxy (X-Forwarded-For, X-Real-IP)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Pega o primeiro IP da lista (cliente original)
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback para IP direto
        if request.client:
            return request.client.host

        return "unknown"

    def _normalize_endpoint(self, path: str) -> str:
        """
        Normaliza o path para agrupamento de métricas

        Args:
            path: Path da requisição

        Returns:
            Path normalizado (sem IDs dinâmicos)
        """
        # Substitui IDs numéricos por placeholder para agrupamento
        import re

        # Remove parâmetros dinâmicos comuns
        normalized = re.sub(r"/\d+", "/{id}", path)
        normalized = re.sub(r"/[a-f0-9-]{36}", "/{uuid}", normalized)  # UUIDs
        normalized = re.sub(r"/[a-f0-9]{32}", "/{hash}", normalized)  # Hashes

        return normalized


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware que adiciona headers de segurança básicos
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Adiciona headers de segurança na resposta
        """
        response = await call_next(request)

        # Headers de segurança básicos
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # CSP básico (Content Security Policy)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdnjs.cloudflare.com;"
        )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware simples de rate limiting
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_requests = {}  # {client_ip: [timestamps]}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Aplica rate limiting básico por IP
        """
        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Limpa timestamps antigos (mais de 1 minuto)
        if client_ip in self.client_requests:
            self.client_requests[client_ip] = [
                ts for ts in self.client_requests[client_ip] if current_time - ts < 60
            ]
        else:
            self.client_requests[client_ip] = []

        # Verifica se excedeu o limite
        if len(self.client_requests[client_ip]) >= self.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for IP: {client_ip}",
                client_ip=client_ip,
                requests_count=len(self.client_requests[client_ip]),
                limit=self.requests_per_minute,
            )

            # Retorna erro 429 (Too Many Requests)
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute",
                    "retry_after": 60,
                },
                headers={"Retry-After": "60"},
            )

        # Adiciona timestamp da requisição atual
        self.client_requests[client_ip].append(current_time)

        # Continua com a requisição
        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Extrai IP do cliente (mesmo método do LoggingMiddleware)"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"
