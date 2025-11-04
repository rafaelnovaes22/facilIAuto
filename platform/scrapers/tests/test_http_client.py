"""
Tests for HTTP Client Layer.

Tests cover HTTPClient, RateLimiter, CacheManager, and RetryHandler.
"""

import time
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import requests
from requests.exceptions import Timeout, ConnectionError

from scraper.http_client import (
    HTTPClient,
    RateLimiter,
    CacheManager,
    RetryHandler
)
from scraper.models import Config


@pytest.fixture
def test_config():
    """Create test configuration"""
    return Config(
        http_timeout=5,
        http_max_retries=2,
        http_retry_backoff=2.0,
        rate_limit_requests_per_minute=60,
        rate_limit_delay_between_requests=0.1,  # Faster for tests
        cache_enabled=True,
        cache_ttl_hours=1,
        cache_max_size_mb=10
    )


class TestRateLimiter:
    """Test RateLimiter functionality"""
    
    def test_initialization(self, test_config):
        """Test rate limiter initialization"""
        limiter = RateLimiter(test_config)
        
        assert limiter.requests_per_minute == 60
        assert limiter.delay_between_requests == 0.1
        assert limiter.tokens > 0
    
    def test_acquire_allows_request(self, test_config):
        """Test that acquire allows requests"""
        limiter = RateLimiter(test_config)
        
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start
        
        # Should be nearly instant for first request
        assert elapsed < 0.5
    
    def test_acquire_enforces_delay(self, test_config):
        """Test that acquire enforces delay between requests"""
        limiter = RateLimiter(test_config)
        
        # First request
        limiter.acquire()
        
        # Second request should be delayed
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start
        
        # Should wait at least the configured delay
        assert elapsed >= test_config.rate_limit_delay_between_requests * 0.9
    
    def test_business_hours_throttling(self, test_config):
        """Test business hours throttling"""
        limiter = RateLimiter(test_config)
        
        # Mock business hours
        with patch.object(limiter, '_is_business_hours', return_value=True):
            limiter.acquire()
            
            start = time.time()
            limiter.acquire()
            elapsed = time.time() - start
            
            # Should wait longer during business hours
            expected_delay = test_config.rate_limit_delay_between_requests / test_config.rate_limit_business_hours_throttle
            assert elapsed >= expected_delay * 0.9
    
    def test_handle_429(self, test_config):
        """Test 429 handling"""
        limiter = RateLimiter(test_config)
        
        # Mock sleep to avoid actual waiting
        with patch('time.sleep') as mock_sleep:
            limiter.handle_429()
            
            # Should sleep for 60 seconds
            mock_sleep.assert_called_once_with(60)
            
            # Tokens should be reset
            assert limiter.tokens == 0.0


class TestCacheManager:
    """Test CacheManager functionality"""
    
    def test_initialization(self, test_config, tmp_path):
        """Test cache manager initialization"""
        # Use temporary directory for cache
        with patch('scraper.http_client.Path', return_value=tmp_path):
            cache = CacheManager(test_config)
            
            assert cache.enabled is True
            assert cache.ttl_hours == 1
            assert len(cache.cache) == 0
    
    def test_cache_miss(self, test_config):
        """Test cache miss returns None"""
        cache = CacheManager(test_config)
        
        result = cache.get("http://example.com")
        assert result is None
    
    def test_cache_hit(self, test_config):
        """Test cache hit returns cached response"""
        cache = CacheManager(test_config)
        
        # Create mock response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = "test content"
        
        # Cache the response
        url = "http://example.com"
        cache.set(url, mock_response)
        
        # Retrieve from cache
        cached = cache.get(url)
        assert cached is not None
        assert cached.status_code == 200
        assert cached.text == "test content"
    
    def test_cache_expiration(self, test_config):
        """Test that expired cache entries are not returned"""
        cache = CacheManager(test_config)
        cache.ttl_hours = 0.0001  # Very short TTL
        
        # Create and cache response
        mock_response = Mock(spec=requests.Response)
        url = "http://example.com"
        cache.set(url, mock_response)
        
        # Wait for expiration
        time.sleep(0.5)
        
        # Should return None (expired)
        cached = cache.get(url)
        assert cached is None
    
    def test_cache_disabled(self, test_config):
        """Test that caching can be disabled"""
        test_config.cache_enabled = False
        cache = CacheManager(test_config)
        
        mock_response = Mock(spec=requests.Response)
        url = "http://example.com"
        
        # Set should do nothing
        cache.set(url, mock_response)
        
        # Get should return None
        cached = cache.get(url)
        assert cached is None
    
    def test_cache_clear(self, test_config):
        """Test cache clearing"""
        cache = CacheManager(test_config)
        
        # Add some entries
        for i in range(5):
            mock_response = Mock(spec=requests.Response)
            cache.set(f"http://example.com/{i}", mock_response)
        
        assert len(cache.cache) == 5
        
        # Clear cache
        cache.clear()
        
        assert len(cache.cache) == 0
        assert len(cache.access_times) == 0


class TestRetryHandler:
    """Test RetryHandler functionality"""
    
    def test_initialization(self, test_config):
        """Test retry handler initialization"""
        handler = RetryHandler(test_config)
        
        assert handler.max_retries == 2
        assert handler.backoff_factor == 2.0
    
    def test_calculate_backoff(self, test_config):
        """Test exponential backoff calculation"""
        handler = RetryHandler(test_config)
        
        assert handler.calculate_backoff(0) == 1.0  # 2^0
        assert handler.calculate_backoff(1) == 2.0  # 2^1
        assert handler.calculate_backoff(2) == 4.0  # 2^2
        assert handler.calculate_backoff(3) == 8.0  # 2^3
    
    def test_should_retry_on_timeout(self, test_config):
        """Test retry on timeout exception"""
        handler = RetryHandler(test_config)
        
        exception = Timeout("Connection timeout")
        assert handler.should_retry(None, exception) is True
    
    def test_should_retry_on_connection_error(self, test_config):
        """Test retry on connection error"""
        handler = RetryHandler(test_config)
        
        exception = ConnectionError("Connection failed")
        assert handler.should_retry(None, exception) is True
    
    def test_should_retry_on_5xx(self, test_config):
        """Test retry on 5xx server errors"""
        handler = RetryHandler(test_config)
        
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        
        assert handler.should_retry(mock_response, None) is True
        
        mock_response.status_code = 503
        assert handler.should_retry(mock_response, None) is True
    
    def test_should_not_retry_on_4xx(self, test_config):
        """Test no retry on 4xx client errors"""
        handler = RetryHandler(test_config)
        
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 404
        
        assert handler.should_retry(mock_response, None) is False
        
        mock_response.status_code = 400
        assert handler.should_retry(mock_response, None) is False
    
    def test_should_not_retry_on_429(self, test_config):
        """Test no retry on 429 (handled separately)"""
        handler = RetryHandler(test_config)
        
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 429
        
        assert handler.should_retry(mock_response, None) is False


class TestHTTPClient:
    """Test HTTPClient functionality"""
    
    def test_initialization(self, test_config):
        """Test HTTP client initialization"""
        client = HTTPClient(test_config)
        
        assert client.config == test_config
        assert client.rate_limiter is not None
        assert client.cache_manager is not None
        assert client.retry_handler is not None
        assert client.session is not None
        
        # Check headers
        assert 'User-Agent' in client.session.headers
        assert client.session.headers['User-Agent'] == test_config.http_user_agent
    
    @patch('scraper.http_client.requests.Session.get')
    def test_successful_get(self, mock_get, test_config):
        """Test successful GET request"""
        # Mock successful response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = "success"
        mock_get.return_value = mock_response
        
        client = HTTPClient(test_config)
        response = client.get("http://example.com")
        
        assert response.status_code == 200
        assert response.text == "success"
        mock_get.assert_called_once()
    
    @patch('scraper.http_client.requests.Session.get')
    def test_get_with_cache(self, mock_get, test_config):
        """Test GET request uses cache"""
        # Mock successful response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = "cached content"
        mock_get.return_value = mock_response
        
        client = HTTPClient(test_config)
        url = "http://example.com"
        
        # First request - should hit network
        response1 = client.get(url)
        assert mock_get.call_count == 1
        
        # Second request - should use cache
        response2 = client.get(url)
        assert mock_get.call_count == 1  # No additional call
        assert response2.text == "cached content"
    
    @patch('scraper.http_client.requests.Session.get')
    @patch('time.sleep')
    def test_retry_on_timeout(self, mock_sleep, mock_get, test_config):
        """Test retry on timeout"""
        # First call raises timeout, second succeeds
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_get.side_effect = [Timeout("timeout"), mock_response]
        
        client = HTTPClient(test_config)
        response = client.get("http://example.com")
        
        assert response.status_code == 200
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once()  # Should have backed off
    
    @patch('scraper.http_client.requests.Session.get')
    @patch('time.sleep')
    def test_retry_exhaustion(self, mock_sleep, mock_get, test_config):
        """Test that retries are exhausted"""
        # All calls raise timeout
        mock_get.side_effect = Timeout("timeout")
        
        client = HTTPClient(test_config)
        
        with pytest.raises(Timeout):
            client.get("http://example.com")
        
        # Should try max_retries + 1 times
        assert mock_get.call_count == test_config.http_max_retries + 1
    
    @patch('scraper.http_client.requests.Session.get')
    @patch('time.sleep')
    def test_handle_429(self, mock_sleep, mock_get, test_config):
        """Test 429 handling"""
        # First call returns 429, second succeeds
        mock_429 = Mock(spec=requests.Response)
        mock_429.status_code = 429
        
        mock_success = Mock(spec=requests.Response)
        mock_success.status_code = 200
        
        mock_get.side_effect = [mock_429, mock_success]
        
        client = HTTPClient(test_config)
        response = client.get("http://example.com")
        
        assert response.status_code == 200
        assert mock_get.call_count == 2
        
        # Should have slept for 60 seconds (429 handling)
        assert any(call[0][0] == 60 for call in mock_sleep.call_args_list)
    
    def test_context_manager(self, test_config):
        """Test HTTP client as context manager"""
        with HTTPClient(test_config) as client:
            assert client.session is not None
        
        # Session should be closed after context
        # (We can't easily test this without mocking)
    
    def test_get_cached_method(self, test_config):
        """Test get_cached method"""
        client = HTTPClient(test_config)
        
        # Should return None for uncached URL
        cached = client.get_cached("http://example.com")
        assert cached is None
        
        # Cache a response
        mock_response = Mock(spec=requests.Response)
        client.cache_manager.set("http://example.com", mock_response)
        
        # Should return cached response
        cached = client.get_cached("http://example.com")
        assert cached is not None
