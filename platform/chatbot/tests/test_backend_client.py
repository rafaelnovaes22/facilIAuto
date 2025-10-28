"""
Testes para Backend Client

Valida:
- Requisições HTTP com retry
- Circuit breaker
- Cache de recomendações
- Fallback para cache
- Invalidação de cache
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import json

from src.services.backend_client import BackendClient, CircuitBreaker, CircuitState


class TestCircuitBreaker:
    """Testes do Circuit Breaker"""
    
    def test_circuit_breaker_initial_state(self):
        """Circuit breaker deve iniciar no estado CLOSED"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
    
    def test_circuit_breaker_opens_after_threshold(self):
        """Circuit breaker deve abrir após atingir threshold de falhas"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        
        # Simular falhas
        for _ in range(3):
            cb._on_failure()
        
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3
    
    def test_circuit_breaker_resets_on_success(self):
        """Circuit breaker deve resetar contador em caso de sucesso"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        
        # Simular falhas
        cb._on_failure()
        cb._on_failure()
        assert cb.failure_count == 2
        
        # Sucesso deve resetar
        cb._on_success()
        assert cb.failure_count == 0
        assert cb.state == CircuitState.CLOSED


class TestBackendClient:
    """Testes do Backend Client"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis client"""
        redis = AsyncMock()
        redis.get = AsyncMock(return_value=None)
        redis.setex = AsyncMock()
        redis.delete = AsyncMock()
        redis.scan_iter = AsyncMock(return_value=iter([]))
        return redis
    
    @pytest.fixture
    def backend_client(self, mock_redis):
        """Instância do BackendClient com Redis mockado"""
        return BackendClient(
            base_url="http://localhost:8000",
            redis_client=mock_redis,
            timeout=10,
            cache_ttl=3600
        )
    
    @pytest.mark.asyncio
    async def test_generate_cache_key(self, backend_client):
        """Deve gerar chave de cache consistente"""
        data1 = {"orcamento_min": 50000, "orcamento_max": 80000}
        data2 = {"orcamento_max": 80000, "orcamento_min": 50000}  # Ordem diferente
        
        key1 = backend_client._generate_cache_key("test", data1)
        key2 = backend_client._generate_cache_key("test", data2)
        
        # Deve gerar mesma chave independente da ordem
        assert key1 == key2
        assert key1.startswith("test:")
    
    @pytest.mark.asyncio
    async def test_get_from_cache_hit(self, backend_client, mock_redis):
        """Deve retornar dados do cache quando disponível"""
        cached_data = {"recommendations": [{"car_id": "123"}]}
        mock_redis.get.return_value = json.dumps(cached_data)
        
        result = await backend_client._get_from_cache("test_key")
        
        assert result == cached_data
        mock_redis.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_get_from_cache_miss(self, backend_client, mock_redis):
        """Deve retornar None quando cache não existe"""
        mock_redis.get.return_value = None
        
        result = await backend_client._get_from_cache("test_key")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_save_to_cache(self, backend_client, mock_redis):
        """Deve salvar dados no cache com TTL"""
        data = {"recommendations": [{"car_id": "123"}]}
        
        await backend_client._save_to_cache("test_key", data)
        
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == "test_key"
        assert args[1] == 3600  # TTL
        assert json.loads(args[2]) == data
    
    @pytest.mark.asyncio
    async def test_get_recommendations_with_cache_hit(self, backend_client, mock_redis):
        """Deve retornar recomendações do cache quando disponível"""
        cached_recommendations = [
            {"car": {"id": "123", "marca": "Toyota"}, "match_score": 0.95}
        ]
        mock_redis.get.return_value = json.dumps(cached_recommendations)
        
        user_profile = {
            "orcamento_min": 50000,
            "orcamento_max": 80000,
            "uso_principal": "trabalho"
        }
        
        result = await backend_client.get_recommendations(user_profile, use_cache=True)
        
        assert result == cached_recommendations
        # Não deve fazer requisição HTTP
        assert mock_redis.get.called
    
    @pytest.mark.asyncio
    async def test_get_recommendations_cache_miss_and_save(self, backend_client, mock_redis):
        """Deve fazer requisição e salvar no cache quando cache miss"""
        mock_redis.get.return_value = None
        
        user_profile = {
            "orcamento_min": 50000,
            "orcamento_max": 80000,
            "uso_principal": "trabalho"
        }
        
        recommendations = [
            {"car": {"id": "123", "marca": "Toyota"}, "match_score": 0.95}
        ]
        
        # Mock da requisição HTTP
        with patch.object(backend_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"recommendations": recommendations}
            
            result = await backend_client.get_recommendations(user_profile, use_cache=True)
            
            assert result == recommendations
            mock_request.assert_called_once()
            mock_redis.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_recommendations_fallback_to_cache(self, backend_client, mock_redis):
        """Deve usar cache como fallback quando backend falha"""
        cached_recommendations = [
            {"car": {"id": "123", "marca": "Toyota"}, "match_score": 0.95}
        ]
        
        # Primeira chamada retorna None (cache miss)
        # Segunda chamada retorna cache (fallback)
        mock_redis.get.side_effect = [None, json.dumps(cached_recommendations)]
        
        user_profile = {
            "orcamento_min": 50000,
            "orcamento_max": 80000,
            "uso_principal": "trabalho"
        }
        
        # Mock da requisição HTTP para falhar
        with patch.object(backend_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.HTTPError("Backend unavailable")
            
            result = await backend_client.get_recommendations(user_profile, use_cache=True)
            
            assert result == cached_recommendations
            assert mock_redis.get.call_count == 2  # Cache miss + fallback
    
    @pytest.mark.asyncio
    async def test_submit_feedback_invalidates_cache(self, backend_client, mock_redis):
        """Deve invalidar cache após enviar feedback"""
        feedback = {
            "user_id": "user123",
            "car_id": "car456",
            "action": "liked"
        }
        
        # Mock da requisição HTTP
        with patch.object(backend_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "success"}
            
            await backend_client.submit_feedback(feedback)
            
            # Deve invalidar cache
            mock_redis.scan_iter.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_car_details(self, backend_client):
        """Deve obter detalhes de um carro"""
        car_data = {
            "id": "car123",
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "preco": 120000
        }
        
        with patch.object(backend_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = car_data
            
            result = await backend_client.get_car_details("car123")
            
            assert result == car_data
            mock_request.assert_called_once_with("GET", "/cars/car123")
    
    @pytest.mark.asyncio
    async def test_get_car_details_not_found(self, backend_client):
        """Deve lançar ValueError quando carro não encontrado"""
        with patch.object(backend_client, '_make_request', new_callable=AsyncMock) as mock_request:
            error_response = MagicMock()
            error_response.status_code = 404
            mock_request.side_effect = httpx.HTTPStatusError(
                "Not found",
                request=MagicMock(),
                response=error_response
            )
            
            with pytest.raises(ValueError, match="não encontrado"):
                await backend_client.get_car_details("invalid_id")
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, backend_client):
        """Deve retornar True quando backend está saudável"""
        with patch.object(backend_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "healthy"}
            
            result = await backend_client.health_check()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, backend_client):
        """Deve retornar False quando backend não está saudável"""
        with patch.object(backend_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.HTTPError("Connection failed")
            
            result = await backend_client.health_check()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_refine_recommendations(self, backend_client):
        """Deve refinar recomendações baseado em feedback"""
        request_data = {
            "user_id": "user123",
            "current_profile": {"orcamento_min": 50000},
            "feedbacks": [{"car_id": "car1", "action": "liked"}]
        }
        
        response_data = {
            "converged": True,
            "recommendations": []
        }
        
        with patch.object(backend_client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = response_data
            
            result = await backend_client.refine_recommendations(request_data)
            
            assert result == response_data
            mock_request.assert_called_once_with(
                "POST",
                "/refine-recommendations",
                json=request_data
            )
    
    @pytest.mark.asyncio
    async def test_close_client(self, backend_client):
        """Deve fechar conexões HTTP"""
        with patch.object(backend_client.client, 'aclose', new_callable=AsyncMock) as mock_close:
            await backend_client.close()
            mock_close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
