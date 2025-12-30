"""
Testes para CacheManager
"""

import pytest
import asyncio
import time

from services.agents.cache_manager import CacheManager


class TestCacheManager:
    """Testes do CacheManager"""

    @pytest.fixture
    def cache_manager(self):
        """Cache manager sem Redis para testes"""
        return CacheManager(redis_url=None, enable_redis=False)

    @pytest.mark.asyncio
    async def test_set_and_get_local(self, cache_manager):
        """Testa set e get básicos no cache local"""
        await cache_manager.set("test_key", "test_value", ttl=3600)

        value = await cache_manager.get("test_key")

        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache_manager):
        """Testa get de chave inexistente"""
        value = await cache_manager.get("nonexistent")

        assert value is None

    @pytest.mark.asyncio
    async def test_set_with_expiration(self, cache_manager):
        """Testa que valores expiram após TTL"""
        await cache_manager.set("expiring_key", "value", ttl=1)  # 1 segundo

        # Imediatamente deve existir
        value1 = await cache_manager.get("expiring_key")
        assert value1 == "value"

        # Aguardar expiração
        await asyncio.sleep(1.5)

        # Deve ter expirado
        value2 = await cache_manager.get("expiring_key")
        assert value2 is None

    @pytest.mark.asyncio
    async def test_set_multiple_values(self, cache_manager):
        """Testa múltiplos valores no cache"""
        await cache_manager.set("key1", "value1", ttl=3600)
        await cache_manager.set("key2", "value2", ttl=3600)
        await cache_manager.set("key3", "value3", ttl=3600)

        assert await cache_manager.get("key1") == "value1"
        assert await cache_manager.get("key2") == "value2"
        assert await cache_manager.get("key3") == "value3"

    @pytest.mark.asyncio
    async def test_overwrite_value(self, cache_manager):
        """Testa sobrescrita de valor"""
        await cache_manager.set("key", "old_value", ttl=3600)
        await cache_manager.set("key", "new_value", ttl=3600)

        value = await cache_manager.get("key")

        assert value == "new_value"

    @pytest.mark.asyncio
    async def test_delete_value(self, cache_manager):
        """Testa deleção de valor"""
        await cache_manager.set("key", "value", ttl=3600)

        # Verificar que existe
        assert await cache_manager.get("key") == "value"

        # Deletar
        await cache_manager.delete("key")

        # Verificar que foi removido
        assert await cache_manager.get("key") is None

    @pytest.mark.asyncio
    async def test_clear_cache(self, cache_manager):
        """Testa limpeza do cache"""
        await cache_manager.set("key1", "value1", ttl=3600)
        await cache_manager.set("key2", "value2", ttl=3600)

        # Limpar
        await cache_manager.clear()

        # Verificar que cache local está vazio
        assert len(cache_manager.local_cache) == 0

    @pytest.mark.asyncio
    async def test_lru_eviction(self):
        """Testa evicção LRU quando cache enche"""
        # Cache pequeno (max 10 itens)
        cache = CacheManager(
            redis_url=None,
            enable_redis=False,
            local_cache_max_size=10
        )

        # Adicionar 15 itens (vai exceder o limite)
        for i in range(15):
            await cache.set(f"key{i}", f"value{i}", ttl=3600)

        # Cache deve ter no máximo 10 itens (ou um pouco mais antes da evicção)
        assert len(cache.local_cache) <= 11  # 10 + margem de 1

    @pytest.mark.asyncio
    async def test_stats_tracking(self, cache_manager):
        """Testa rastreamento de estatísticas"""
        # Gerar algumas operações
        await cache_manager.set("key1", "value1", ttl=3600)
        await cache_manager.get("key1")  # Cache hit
        await cache_manager.get("key2")  # Cache miss

        stats = cache_manager.get_stats()

        assert stats['total_gets'] == 2
        assert stats['total_sets'] == 1
        assert stats['local_hits'] == 1
        assert stats['local_misses'] == 1
        assert stats['local_hit_rate'] == 0.5

    @pytest.mark.asyncio
    async def test_reset_stats(self, cache_manager):
        """Testa reset de estatísticas"""
        # Gerar operações
        await cache_manager.set("key", "value", ttl=3600)
        await cache_manager.get("key")

        stats_before = cache_manager.get_stats()
        assert stats_before['total_gets'] > 0

        # Resetar
        cache_manager.reset_stats()

        stats_after = cache_manager.get_stats()
        assert stats_after['total_gets'] == 0
        assert stats_after['total_sets'] == 0

    @pytest.mark.asyncio
    async def test_cache_with_dict_value(self, cache_manager):
        """Testa cache com dicionário como valor"""
        data = {
            'score': 0.85,
            'metadata': {'source': 'test'}
        }

        await cache_manager.set("dict_key", data, ttl=3600)
        value = await cache_manager.get("dict_key")

        assert value == data
        assert value['score'] == 0.85

    @pytest.mark.asyncio
    async def test_cache_with_list_value(self, cache_manager):
        """Testa cache com lista como valor"""
        data = [1, 2, 3, 4, 5]

        await cache_manager.set("list_key", data, ttl=3600)
        value = await cache_manager.get("list_key")

        assert value == data

    @pytest.mark.asyncio
    async def test_cache_with_numeric_value(self, cache_manager):
        """Testa cache com valores numéricos"""
        await cache_manager.set("int_key", 42, ttl=3600)
        await cache_manager.set("float_key", 3.14, ttl=3600)

        assert await cache_manager.get("int_key") == 42
        assert await cache_manager.get("float_key") == 3.14

    def test_local_cache_only_when_redis_disabled(self):
        """Testa que Redis não é usado quando desabilitado"""
        cache = CacheManager(
            redis_url="redis://localhost:6379",
            enable_redis=False
        )

        # Redis não deve estar disponível
        assert cache.redis_available is False
        assert cache.redis_client is None
