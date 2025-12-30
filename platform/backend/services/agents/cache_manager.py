"""
Cache Manager - Sistema de cache em múltiplas camadas

Implementa cache hierárquico:
1. Memória local (LRU) - rápido mas limitado
2. Redis (opcional) - compartilhado entre workers
3. Fallback para cálculo direto
"""

import json
import time
import logging
from typing import Any, Optional, Dict
from datetime import datetime


logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gerenciador de cache em múltiplas camadas

    Camada 1: Cache em memória local (LRU)
    Camada 2: Redis (opcional, compartilhado)
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        local_cache_max_size: int = 1000,
        enable_redis: bool = True
    ):
        """
        Inicializa o gerenciador de cache

        Args:
            redis_url: URL do Redis (ex: redis://localhost:6379)
            local_cache_max_size: Tamanho máximo do cache local
            enable_redis: Se deve tentar conectar ao Redis
        """
        # Camada 1: Cache local em memória
        self.local_cache: Dict[str, tuple] = {}
        self.local_cache_max_size = local_cache_max_size

        # Camada 2: Redis (opcional)
        self.redis_client = None
        self.redis_available = False

        if enable_redis and redis_url:
            try:
                import redis.asyncio as redis
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    encoding="utf-8"
                )
                self.redis_available = True
                logger.info(f"[CacheManager] Redis conectado: {redis_url}")
            except ImportError:
                logger.warning(
                    "[CacheManager] redis.asyncio não disponível, "
                    "usando apenas cache local"
                )
            except Exception as e:
                logger.warning(
                    f"[CacheManager] Erro ao conectar Redis: {e}, "
                    f"usando apenas cache local"
                )

        # Métricas
        self.stats = {
            'local_hits': 0,
            'local_misses': 0,
            'redis_hits': 0,
            'redis_misses': 0,
            'total_gets': 0,
            'total_sets': 0
        }

    async def get(self, key: str) -> Optional[Any]:
        """
        Busca valor no cache (local -> redis -> None)

        Args:
            key: Chave de cache

        Returns:
            Valor armazenado ou None se não encontrado
        """
        self.stats['total_gets'] += 1

        # 1. Tentar cache local
        local_value = self._get_from_local(key)
        if local_value is not None:
            self.stats['local_hits'] += 1
            return local_value

        self.stats['local_misses'] += 1

        # 2. Tentar Redis
        if self.redis_available and self.redis_client:
            try:
                redis_value = await self._get_from_redis(key)
                if redis_value is not None:
                    self.stats['redis_hits'] += 1

                    # Promover para cache local
                    self._set_in_local(key, redis_value, ttl=3600)

                    return redis_value

                self.stats['redis_misses'] += 1

            except Exception as e:
                logger.warning(f"[CacheManager] Erro ao ler do Redis: {e}")

        # 3. Cache miss completo
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Salva valor no cache (local + redis)

        Args:
            key: Chave de cache
            value: Valor a armazenar
            ttl: Time-to-live em segundos (padrão: 1 hora)
        """
        self.stats['total_sets'] += 1

        # 1. Salvar localmente
        self._set_in_local(key, value, ttl)

        # 2. Salvar no Redis
        if self.redis_available and self.redis_client:
            try:
                await self._set_in_redis(key, value, ttl)
            except Exception as e:
                logger.warning(f"[CacheManager] Erro ao salvar no Redis: {e}")

    async def delete(self, key: str):
        """
        Remove valor do cache (local + redis)

        Args:
            key: Chave de cache a remover
        """
        # 1. Remover localmente
        if key in self.local_cache:
            del self.local_cache[key]

        # 2. Remover do Redis
        if self.redis_available and self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception as e:
                logger.warning(f"[CacheManager] Erro ao deletar do Redis: {e}")

    async def clear(self):
        """
        Limpa todo o cache (local + redis)
        """
        # 1. Limpar local
        self.local_cache.clear()

        # 2. Limpar Redis (flush all - CUIDADO!)
        # Comentado por segurança - implementar com prefixo se necessário
        # if self.redis_available and self.redis_client:
        #     await self.redis_client.flushdb()

    def _get_from_local(self, key: str) -> Optional[Any]:
        """
        Busca valor no cache local

        Args:
            key: Chave de cache

        Returns:
            Valor armazenado ou None se não encontrado/expirado
        """
        if key not in self.local_cache:
            return None

        value, expiry = self.local_cache[key]

        # Verificar expiração
        if expiry is not None and time.time() > expiry:
            del self.local_cache[key]
            return None

        return value

    def _set_in_local(self, key: str, value: Any, ttl: int):
        """
        Salva valor no cache local com LRU

        Args:
            key: Chave de cache
            value: Valor a armazenar
            ttl: Time-to-live em segundos
        """
        expiry = time.time() + ttl if ttl else None
        self.local_cache[key] = (value, expiry)

        # Limpar cache se muito grande (LRU simples)
        if len(self.local_cache) > self.local_cache_max_size:
            self._evict_lru()

    def _evict_lru(self):
        """
        Remove 10% dos itens mais antigos (LRU)
        """
        # Ordenar por tempo de expiração (mais antigos primeiro)
        sorted_keys = sorted(
            self.local_cache.keys(),
            key=lambda k: self.local_cache[k][1] or float('inf')
        )

        # Remover 10% dos mais antigos
        num_to_remove = max(1, len(sorted_keys) // 10)
        for key_to_remove in sorted_keys[:num_to_remove]:
            del self.local_cache[key_to_remove]

        logger.debug(
            f"[CacheManager] LRU eviction: removidos {num_to_remove} itens"
        )

    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """
        Busca valor no Redis

        Args:
            key: Chave de cache

        Returns:
            Valor armazenado ou None se não encontrado
        """
        value_str = await self.redis_client.get(key)

        if value_str is None:
            return None

        # Deserializar JSON
        try:
            return json.loads(value_str)
        except json.JSONDecodeError:
            # Se não for JSON, retornar string direta
            return value_str

    async def _set_in_redis(self, key: str, value: Any, ttl: int):
        """
        Salva valor no Redis

        Args:
            key: Chave de cache
            value: Valor a armazenar
            ttl: Time-to-live em segundos
        """
        # Serializar para JSON
        try:
            value_str = json.dumps(value)
        except (TypeError, ValueError):
            # Se não for serializável, converter para string
            value_str = str(value)

        # Salvar com TTL
        await self.redis_client.setex(key, ttl, value_str)

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache

        Returns:
            dict: Estatísticas incluindo:
                - local_hit_rate: Taxa de hit do cache local
                - redis_hit_rate: Taxa de hit do Redis
                - total_hit_rate: Taxa de hit geral
                - local_size: Tamanho do cache local
                - total_gets: Total de leituras
                - total_sets: Total de escritas
        """
        total_gets = self.stats['total_gets']

        if total_gets == 0:
            return {
                'local_hits': 0,
                'local_misses': 0,
                'local_hit_rate': 0.0,
                'redis_hits': 0,
                'redis_misses': 0,
                'redis_hit_rate': 0.0,
                'total_hit_rate': 0.0,
                'local_size': len(self.local_cache),
                'total_gets': 0,
                'total_sets': self.stats['total_sets']
            }

        local_attempts = self.stats['local_hits'] + self.stats['local_misses']
        redis_attempts = self.stats['redis_hits'] + self.stats['redis_misses']

        local_hit_rate = (
            self.stats['local_hits'] / local_attempts
            if local_attempts > 0 else 0.0
        )

        redis_hit_rate = (
            self.stats['redis_hits'] / redis_attempts
            if redis_attempts > 0 else 0.0
        )

        total_hits = self.stats['local_hits'] + self.stats['redis_hits']
        total_hit_rate = total_hits / total_gets

        return {
            'local_hits': self.stats['local_hits'],
            'local_misses': self.stats['local_misses'],
            'local_hit_rate': local_hit_rate,
            'redis_hits': self.stats['redis_hits'],
            'redis_misses': self.stats['redis_misses'],
            'redis_hit_rate': redis_hit_rate,
            'total_hit_rate': total_hit_rate,
            'local_size': len(self.local_cache),
            'total_gets': total_gets,
            'total_sets': self.stats['total_sets']
        }

    def reset_stats(self):
        """Reseta as estatísticas"""
        self.stats = {
            'local_hits': 0,
            'local_misses': 0,
            'redis_hits': 0,
            'redis_misses': 0,
            'total_gets': 0,
            'total_sets': 0
        }


# Singleton global (opcional)
_cache_manager_instance = None


def get_cache_manager(
    redis_url: Optional[str] = None,
    enable_redis: bool = True
) -> CacheManager:
    """
    Retorna instância singleton do CacheManager

    Args:
        redis_url: URL do Redis
        enable_redis: Se deve habilitar Redis

    Returns:
        CacheManager: Instância singleton
    """
    global _cache_manager_instance

    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager(
            redis_url=redis_url,
            enable_redis=enable_redis
        )

    return _cache_manager_instance
