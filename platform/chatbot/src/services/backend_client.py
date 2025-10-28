"""
Backend Client - Cliente HTTP para API do FacilIAuto

Este módulo implementa um cliente HTTP robusto para comunicação com o backend
existente do FacilIAuto, incluindo:
- Retry com backoff exponencial
- Circuit breaker para proteção
- Cache de recomendações em Redis
- Fallback para cache quando backend indisponível

Requirements: 5.1, 5.2, 5.3, 5.4, 12.4
"""

import httpx
import asyncio
import hashlib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import logging

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Estados do Circuit Breaker"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit Breaker para proteção contra falhas em cascata
    
    Estados:
    - CLOSED: Operação normal
    - OPEN: Muitas falhas, rejeitar requisições
    - HALF_OPEN: Testando se serviço recuperou
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Executar função com circuit breaker"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker: Tentando recuperação (HALF_OPEN)")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    async def acall(self, func, *args, **kwargs):
        """Executar função assíncrona com circuit breaker"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker: Tentando recuperação (HALF_OPEN)")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Verificar se deve tentar resetar o circuit breaker"""
        if self.last_failure_time is None:
            return True
        
        return (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout
    
    def _on_success(self):
        """Callback de sucesso"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker: Recuperado (CLOSED)")
    
    def _on_failure(self):
        """Callback de falha"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker: ABERTO após {self.failure_count} falhas. "
                f"Tentará recuperar em {self.recovery_timeout}s"
            )


class BackendClient:
    """
    Cliente HTTP para API do FacilIAuto
    
    Features:
    - Retry automático com backoff exponencial
    - Circuit breaker para proteção
    - Cache de recomendações em Redis
    - Fallback para cache quando backend indisponível
    - Timeout configurável
    - Logging detalhado
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 12.4
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        redis_client = None,
        timeout: int = 30,
        cache_ttl: int = 3600  # 1 hora
    ):
        """
        Inicializar cliente
        
        Args:
            base_url: URL base da API do FacilIAuto
            redis_client: Cliente Redis para cache
            timeout: Timeout em segundos
            cache_ttl: TTL do cache em segundos (padrão: 1 hora)
        """
        self.base_url = base_url.rstrip("/")
        self.redis = redis_client
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        
        # HTTP client com timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True
        )
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=httpx.HTTPError
        )
        
        logger.info(f"BackendClient inicializado: {base_url}")
    
    async def close(self):
        """Fechar conexões"""
        await self.client.aclose()
    
    def _generate_cache_key(self, prefix: str, data: Dict) -> str:
        """
        Gerar chave de cache baseada em hash do perfil
        
        Args:
            prefix: Prefixo da chave
            data: Dados para gerar hash
            
        Returns:
            Chave de cache
        """
        # Serializar dados de forma determinística
        data_str = json.dumps(data, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        return f"{prefix}:{data_hash}"
    
    async def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """
        Obter dados do cache Redis
        
        Args:
            cache_key: Chave do cache
            
        Returns:
            Dados do cache ou None
        """
        if not self.redis:
            return None
        
        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                logger.info(f"Cache HIT: {cache_key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Erro ao ler cache: {e}")
        
        return None
    
    async def _save_to_cache(self, cache_key: str, data: Dict):
        """
        Salvar dados no cache Redis
        
        Args:
            cache_key: Chave do cache
            data: Dados para cachear
        """
        if not self.redis:
            return
        
        try:
            await self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(data)
            )
            logger.info(f"Cache SAVE: {cache_key} (TTL: {self.cache_ttl}s)")
        except Exception as e:
            logger.warning(f"Erro ao salvar cache: {e}")
    
    async def _invalidate_cache(self, pattern: str):
        """
        Invalidar cache por padrão
        
        Args:
            pattern: Padrão de chave para invalidar
        """
        if not self.redis:
            return
        
        try:
            # Buscar chaves que correspondem ao padrão
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"Cache INVALIDATED: {len(keys)} chaves removidas")
        except Exception as e:
            logger.warning(f"Erro ao invalidar cache: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict:
        """
        Fazer requisição HTTP com retry e circuit breaker
        
        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint da API
            **kwargs: Argumentos adicionais para httpx
            
        Returns:
            Resposta JSON
            
        Raises:
            httpx.HTTPError: Erro na requisição
        """
        url = f"{self.base_url}{endpoint}"
        
        async def _request():
            logger.debug(f"{method} {url}")
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        
        # Executar com circuit breaker
        return await self.circuit_breaker.acall(_request)
    
    async def get_recommendations(
        self,
        user_profile: Dict,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Obter recomendações de carros
        
        Endpoint: POST /recommend
        
        Args:
            user_profile: Perfil do usuário (formato UserProfile)
            use_cache: Se deve usar cache (padrão: True)
            
        Returns:
            Lista de recomendações
            
        Requirements: 5.1, 5.3, 12.4
        """
        # Gerar chave de cache
        cache_key = self._generate_cache_key("recommendations", user_profile)
        
        # Tentar obter do cache
        if use_cache:
            cached = await self._get_from_cache(cache_key)
            if cached:
                return cached
        
        try:
            # Fazer requisição
            response = await self._make_request(
                "POST",
                "/recommend",
                json=user_profile
            )
            
            recommendations = response.get("recommendations", [])
            
            # Salvar no cache
            if use_cache:
                await self._save_to_cache(cache_key, recommendations)
            
            logger.info(
                f"Recomendações obtidas: {len(recommendations)} carros "
                f"(orçamento: {user_profile.get('orcamento_min')}-{user_profile.get('orcamento_max')})"
            )
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Erro ao obter recomendações: {e}")
            
            # Fallback para cache se backend indisponível
            if use_cache:
                cached = await self._get_from_cache(cache_key)
                if cached:
                    logger.warning("Backend indisponível - usando cache como fallback")
                    return cached
            
            raise
    
    async def get_car_details(self, car_id: str) -> Dict:
        """
        Obter detalhes de um carro específico
        
        Endpoint: GET /cars/{car_id}
        
        Args:
            car_id: ID do carro
            
        Returns:
            Detalhes do carro
            
        Requirements: 5.2
        """
        try:
            car = await self._make_request(
                "GET",
                f"/cars/{car_id}"
            )
            
            logger.info(f"Detalhes do carro obtidos: {car_id}")
            return car
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Carro não encontrado: {car_id}")
                raise ValueError(f"Carro {car_id} não encontrado")
            raise
    
    async def submit_feedback(self, feedback: Dict) -> Dict:
        """
        Enviar feedback do usuário
        
        Endpoint: POST /feedback
        
        Args:
            feedback: Dados do feedback (formato UserFeedback)
            
        Returns:
            Resposta com histórico atualizado
            
        Requirements: 5.4
        """
        try:
            response = await self._make_request(
                "POST",
                "/feedback",
                json=feedback
            )
            
            logger.info(
                f"Feedback enviado: user={feedback.get('user_id')}, "
                f"action={feedback.get('action')}, car={feedback.get('car_id')}"
            )
            
            # Invalidar cache de recomendações do usuário
            user_id = feedback.get("user_id")
            if user_id:
                await self._invalidate_cache(f"recommendations:*")
            
            return response
        
        except Exception as e:
            logger.error(f"Erro ao enviar feedback: {e}")
            raise
    
    async def refine_recommendations(
        self,
        request: Dict,
        use_cache: bool = False  # Não cachear refinamentos por padrão
    ) -> Dict:
        """
        Refinar recomendações baseado em feedback
        
        Endpoint: POST /refine-recommendations
        
        Args:
            request: Requisição de refinamento (formato RefinementRequest)
            use_cache: Se deve usar cache (padrão: False)
            
        Returns:
            Resposta com recomendações refinadas
            
        Requirements: 5.4
        """
        try:
            response = await self._make_request(
                "POST",
                "/refine-recommendations",
                json=request
            )
            
            logger.info(
                f"Recomendações refinadas: user={request.get('user_id')}, "
                f"iteration={len(request.get('feedbacks', []))}, "
                f"converged={response.get('converged')}"
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Erro ao refinar recomendações: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Verificar saúde do backend
        
        Endpoint: GET /health
        
        Returns:
            True se backend está saudável
        """
        try:
            response = await self._make_request("GET", "/health")
            return response.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Health check falhou: {e}")
            return False


# Singleton instance (opcional)
_backend_client: Optional[BackendClient] = None


def get_backend_client(
    base_url: str = "http://localhost:8000",
    redis_client = None
) -> BackendClient:
    """
    Obter instância singleton do BackendClient
    
    Args:
        base_url: URL base da API
        redis_client: Cliente Redis
        
    Returns:
        Instância do BackendClient
    """
    global _backend_client
    
    if _backend_client is None:
        _backend_client = BackendClient(
            base_url=base_url,
            redis_client=redis_client
        )
    
    return _backend_client
