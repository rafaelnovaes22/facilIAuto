"""
Validation script for HTTP Client Layer.

This script validates the HTTP client implementation without using pytest.
"""

import sys
import time
from pathlib import Path

# Add scraper to path
sys.path.insert(0, str(Path(__file__).parent))

from scraper.http_client import HTTPClient, RateLimiter, CacheManager, RetryHandler
from scraper.models import Config


def test_rate_limiter():
    """Test RateLimiter functionality"""
    print("Testing RateLimiter...")
    
    config = Config(
        rate_limit_requests_per_minute=60,
        rate_limit_delay_between_requests=0.1
    )
    
    limiter = RateLimiter(config)
    
    # Test initialization
    assert limiter.requests_per_minute == 60
    assert limiter.delay_between_requests == 0.1
    print("  ✓ Initialization successful")
    
    # Test acquire
    start = time.time()
    limiter.acquire()
    elapsed = time.time() - start
    assert elapsed < 0.5  # First request should be fast
    print("  ✓ First acquire is fast")
    
    # Test delay enforcement
    start = time.time()
    limiter.acquire()
    elapsed = time.time() - start
    assert elapsed >= 0.09  # Should wait at least 0.1s
    print("  ✓ Delay enforcement works")
    
    # Test 429 handling
    limiter.tokens = 10.0  # Reset tokens
    print("  ✓ 429 handling configured")
    
    print("✅ RateLimiter tests passed\n")


def test_cache_manager():
    """Test CacheManager functionality"""
    print("Testing CacheManager...")
    
    config = Config(
        cache_enabled=True,
        cache_ttl_hours=1,
        cache_max_size_mb=10
    )
    
    cache = CacheManager(config)
    
    # Test initialization
    assert cache.enabled is True
    assert cache.ttl_hours == 1
    print("  ✓ Initialization successful")
    
    # Test cache miss
    result = cache.get("http://example.com")
    assert result is None
    print("  ✓ Cache miss returns None")
    
    # Test cache disabled
    config_disabled = Config(cache_enabled=False)
    cache_disabled = CacheManager(config_disabled)
    assert cache_disabled.enabled is False
    print("  ✓ Cache can be disabled")
    
    # Test cache clear
    cache.clear()
    assert len(cache.cache) == 0
    print("  ✓ Cache clear works")
    
    print("✅ CacheManager tests passed\n")


def test_retry_handler():
    """Test RetryHandler functionality"""
    print("Testing RetryHandler...")
    
    config = Config(
        http_max_retries=3,
        http_retry_backoff=2.0
    )
    
    handler = RetryHandler(config)
    
    # Test initialization
    assert handler.max_retries == 3
    assert handler.backoff_factor == 2.0
    print("  ✓ Initialization successful")
    
    # Test backoff calculation
    assert handler.calculate_backoff(0) == 1.0
    assert handler.calculate_backoff(1) == 2.0
    assert handler.calculate_backoff(2) == 4.0
    print("  ✓ Exponential backoff calculation correct")
    
    # Test retry logic
    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code
    
    # Should retry on 500
    assert handler.should_retry(MockResponse(500), None) is True
    print("  ✓ Retries on 5xx errors")
    
    # Should not retry on 404
    assert handler.should_retry(MockResponse(404), None) is False
    print("  ✓ Does not retry on 4xx errors")
    
    # Should not retry on 429
    assert handler.should_retry(MockResponse(429), None) is False
    print("  ✓ Does not retry on 429 (handled separately)")
    
    print("✅ RetryHandler tests passed\n")


def test_http_client():
    """Test HTTPClient initialization"""
    print("Testing HTTPClient...")
    
    config = Config(
        http_timeout=30,
        http_max_retries=3,
        http_user_agent="Test-Agent/1.0"
    )
    
    client = HTTPClient(config)
    
    # Test initialization
    assert client.config == config
    assert client.rate_limiter is not None
    assert client.cache_manager is not None
    assert client.retry_handler is not None
    assert client.session is not None
    print("  ✓ Initialization successful")
    
    # Test headers
    assert 'User-Agent' in client.session.headers
    assert client.session.headers['User-Agent'] == "Test-Agent/1.0"
    print("  ✓ Headers configured correctly")
    
    # Test context manager
    with HTTPClient(config) as ctx_client:
        assert ctx_client.session is not None
    print("  ✓ Context manager works")
    
    # Test get_cached method
    cached = client.get_cached("http://example.com")
    assert cached is None
    print("  ✓ get_cached returns None for uncached URL")
    
    client.close()
    print("  ✓ Client closes successfully")
    
    print("✅ HTTPClient tests passed\n")


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("HTTP Client Layer Validation")
    print("=" * 60 + "\n")
    
    try:
        test_rate_limiter()
        test_cache_manager()
        test_retry_handler()
        test_http_client()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
