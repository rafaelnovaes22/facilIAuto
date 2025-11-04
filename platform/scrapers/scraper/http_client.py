"""
HTTP Client Layer with resilience features.

This module provides HTTP client functionality with rate limiting,
retry logic, caching, and connection pooling.

Requirements: 2.1, 2.3, 2.4, 3.1, 3.2, 3.4, 3.5, 6.1, 6.2
"""

import time
import hashlib
import pickle
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from collections import deque
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry as Urllib3Retry

from .models import Config


logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter with business hours throttling.
    
    Requirements: 3.1, 3.2, 3.5
    """
    
    def __init__(self, config: Config):
        """
        Initialize rate limiter.
        
        Args:
            config: Scraper configuration
        """
        self.config = config
        self.requests_per_minute = config.rate_limit_requests_per_minute
        self.delay_between_requests = config.rate_limit_delay_between_requests
        self.business_hours_throttle = config.rate_limit_business_hours_throttle
        
        # Token bucket implementation
        self.tokens = float(self.requests_per_minute)
        self.max_tokens = float(self.requests_per_minute)
        self.last_update = time.time()
        self.token_rate = self.requests_per_minute / 60.0  # tokens per second
        
        # Request history for tracking
        self.request_times: deque = deque(maxlen=self.requests_per_minute)
        
        logger.info(
            f"RateLimiter initialized: {self.requests_per_minute} req/min, "
            f"{self.delay_between_requests}s delay"
        )
    
    def _refill_tokens(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.max_tokens,
            self.tokens + elapsed * self.token_rate
        )
        self.last_update = now
    
    def _is_business_hours(self) -> bool:
        """
        Check if current time is during business hours (8h-18h).
        
        Returns:
            True if during business hours
        """
        now = datetime.now()
        return 8 <= now.hour < 18
    
    def acquire(self):
        """
        Acquire permission to make a request.
        
        Blocks until permission is granted, respecting rate limits
        and business hours throttling.
        """
        # Apply business hours throttling
        effective_delay = self.delay_between_requests
        if self._is_business_hours():
            effective_delay = self.delay_between_requests / self.business_hours_throttle
            logger.debug(f"Business hours throttling: {effective_delay}s delay")
        
        # Wait for minimum delay between requests
        if self.request_times:
            time_since_last = time.time() - self.request_times[-1]
            if time_since_last < effective_delay:
                sleep_time = effective_delay - time_since_last
                logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        # Token bucket algorithm
        while True:
            self._refill_tokens()
            
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                self.request_times.append(time.time())
                break
            else:
                # Wait until we have at least one token
                wait_time = (1.0 - self.tokens) / self.token_rate
                logger.debug(f"Token bucket: waiting {wait_time:.2f}s for token")
                time.sleep(wait_time)
    
    def handle_429(self):
        """
        Handle 429 Too Many Requests response.
        
        Requirement: 3.2
        """
        logger.warning("Received 429 Too Many Requests, waiting 60 seconds")
        time.sleep(60)
        # Reset tokens to be conservative
        self.tokens = 0.0


class CacheManager:
    """
    LRU cache with TTL and disk persistence.
    
    Requirement: 2.3
    """
    
    def __init__(self, config: Config):
        """
        Initialize cache manager.
        
        Args:
            config: Scraper configuration
        """
        self.config = config
        self.enabled = config.cache_enabled
        self.ttl_hours = config.cache_ttl_hours
        self.max_size_mb = config.cache_max_size_mb
        
        # Cache directory
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # In-memory cache: url -> (response, timestamp)
        self.cache: Dict[str, tuple] = {}
        
        # LRU tracking: url -> last_access_time
        self.access_times: Dict[str, float] = {}
        
        logger.info(
            f"CacheManager initialized: TTL={self.ttl_hours}h, "
            f"max_size={self.max_size_mb}MB"
        )
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cached response"""
        return self.cache_dir / f"{cache_key}.cache"
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry is expired"""
        age_hours = (time.time() - timestamp) / 3600
        return age_hours > self.ttl_hours
    
    def _cleanup_old_entries(self):
        """Remove expired entries and enforce size limit"""
        # Remove expired entries
        expired_keys = [
            url for url, (_, timestamp) in self.cache.items()
            if self._is_expired(timestamp)
        ]
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
        
        # Enforce size limit using LRU
        try:
            cache_size_mb = len(pickle.dumps(self.cache)) / (1024 * 1024)
        except (pickle.PicklingError, AttributeError, TypeError) as e:
            # If we can't pickle the cache, estimate size by entry count
            logger.warning(f"Cannot calculate cache size: {e}, using entry count")
            cache_size_mb = len(self.cache) * 0.1  # Rough estimate: 100KB per entry
        
        if cache_size_mb > self.max_size_mb:
            # Remove least recently used entries
            sorted_urls = sorted(
                self.access_times.items(),
                key=lambda x: x[1]
            )
            # Remove oldest 20% of entries
            remove_count = max(1, len(sorted_urls) // 5)
            for url, _ in sorted_urls[:remove_count]:
                if url in self.cache:
                    del self.cache[url]
                del self.access_times[url]
            
            logger.info(f"Cache cleanup: removed {remove_count} LRU entries")
    
    def get(self, url: str) -> Optional[requests.Response]:
        """
        Get cached response for URL.
        
        Args:
            url: Request URL
            
        Returns:
            Cached response or None if not found/expired
        """
        if not self.enabled:
            return None
        
        cache_key = self._get_cache_key(url)
        
        # Check in-memory cache first
        if url in self.cache:
            response, timestamp = self.cache[url]
            if not self._is_expired(timestamp):
                self.access_times[url] = time.time()
                logger.debug(f"Cache hit (memory): {url}")
                return response
            else:
                # Expired, remove it
                del self.cache[url]
                if url in self.access_times:
                    del self.access_times[url]
        
        # Check disk cache
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    response, timestamp = pickle.load(f)
                
                if not self._is_expired(timestamp):
                    # Load into memory cache
                    self.cache[url] = (response, timestamp)
                    self.access_times[url] = time.time()
                    logger.debug(f"Cache hit (disk): {url}")
                    return response
                else:
                    # Expired, remove file
                    cache_path.unlink()
            except Exception as e:
                logger.warning(f"Error loading cache for {url}: {e}")
                cache_path.unlink(missing_ok=True)
        
        logger.debug(f"Cache miss: {url}")
        return None
    
    def set(self, url: str, response: requests.Response):
        """
        Cache response for URL.
        
        Args:
            url: Request URL
            response: Response to cache
        """
        if not self.enabled:
            return
        
        timestamp = time.time()
        cache_key = self._get_cache_key(url)
        
        # Store in memory
        self.cache[url] = (response, timestamp)
        self.access_times[url] = timestamp
        
        # Persist to disk
        cache_path = self._get_cache_path(cache_key)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump((response, timestamp), f)
            logger.debug(f"Cached response: {url}")
        except Exception as e:
            logger.warning(f"Error caching response for {url}: {e}")
        
        # Cleanup if needed
        self._cleanup_old_entries()
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.access_times.clear()
        
        # Remove cache files
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
        
        logger.info("Cache cleared")


class RetryHandler:
    """
    Exponential backoff retry handler.
    
    Requirements: 2.4, 6.1, 6.2, 3.2
    """
    
    def __init__(self, config: Config):
        """
        Initialize retry handler.
        
        Args:
            config: Scraper configuration
        """
        self.config = config
        self.max_retries = config.http_max_retries
        self.backoff_factor = config.http_retry_backoff
        
        logger.info(
            f"RetryHandler initialized: max_retries={self.max_retries}, "
            f"backoff={self.backoff_factor}"
        )
    
    def calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.
        
        Args:
            attempt: Retry attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        return self.backoff_factor ** attempt
    
    def should_retry(self, response: Optional[requests.Response], 
                    exception: Optional[Exception]) -> bool:
        """
        Determine if request should be retried.
        
        Args:
            response: HTTP response (if any)
            exception: Exception raised (if any)
            
        Returns:
            True if should retry
        """
        # Retry on network errors
        if exception:
            if isinstance(exception, (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ChunkedEncodingError
            )):
                return True
        
        # Retry on 5xx server errors
        if response and 500 <= response.status_code < 600:
            return True
        
        # Don't retry on 429 (handled separately)
        if response and response.status_code == 429:
            return False
        
        # Don't retry on 4xx client errors (except 429)
        if response and 400 <= response.status_code < 500:
            return False
        
        return False


class HTTPClient:
    """
    HTTP client with connection pooling, rate limiting, retry logic, and caching.
    
    Requirements: 2.1, 3.4
    """
    
    def __init__(self, config: Config):
        """
        Initialize HTTP client.
        
        Args:
            config: Scraper configuration
        """
        self.config = config
        
        # Initialize components
        self.rate_limiter = RateLimiter(config)
        self.cache_manager = CacheManager(config)
        self.retry_handler = RetryHandler(config)
        
        # Create session with connection pooling
        self.session = requests.Session()
        
        # Configure retry strategy for urllib3
        retry_strategy = Urllib3Retry(
            total=0,  # We handle retries manually
            connect=0,
            read=0,
            redirect=3,
            status_forcelist=[]
        )
        
        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry_strategy,
            pool_block=False
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': config.http_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        logger.info(
            f"HTTPClient initialized: timeout={config.http_timeout}s, "
            f"user_agent={config.http_user_agent}"
        )
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Perform GET request with rate limiting, retry logic, and caching.
        
        Args:
            url: Request URL
            **kwargs: Additional arguments for requests.get()
            
        Returns:
            Response object
            
        Raises:
            requests.exceptions.RequestException: On request failure
        """
        # Check cache first
        cached_response = self.cache_manager.get(url)
        if cached_response:
            return cached_response
        
        # Acquire rate limit permission
        self.rate_limiter.acquire()
        
        # Set default timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.config.http_timeout
        
        # Retry loop
        last_exception = None
        for attempt in range(self.config.http_max_retries + 1):
            try:
                logger.debug(f"GET {url} (attempt {attempt + 1}/{self.config.http_max_retries + 1})")
                
                response = self.session.get(url, **kwargs)
                
                # Handle 429 Too Many Requests
                if response.status_code == 429:
                    if self.config.rate_limit_respect_429:
                        self.rate_limiter.handle_429()
                        continue
                
                # Check if we should retry
                if self.retry_handler.should_retry(response, None):
                    if attempt < self.config.http_max_retries:
                        backoff = self.retry_handler.calculate_backoff(attempt)
                        logger.warning(
                            f"Request failed with status {response.status_code}, "
                            f"retrying in {backoff}s"
                        )
                        time.sleep(backoff)
                        continue
                
                # Raise for bad status codes
                response.raise_for_status()
                
                # Cache successful response
                if response.status_code == 200:
                    self.cache_manager.set(url, response)
                
                logger.debug(f"GET {url} succeeded: {response.status_code}")
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                
                # Check if we should retry
                if self.retry_handler.should_retry(None, e):
                    if attempt < self.config.http_max_retries:
                        backoff = self.retry_handler.calculate_backoff(attempt)
                        logger.warning(
                            f"Request failed with {type(e).__name__}: {e}, "
                            f"retrying in {backoff}s"
                        )
                        time.sleep(backoff)
                        continue
                
                # No more retries, raise
                logger.error(f"GET {url} failed after {attempt + 1} attempts: {e}")
                raise
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        else:
            raise requests.exceptions.RequestException(
                f"Request failed after {self.config.http_max_retries + 1} attempts"
            )
    
    def get_cached(self, url: str) -> Optional[requests.Response]:
        """
        Get cached response without making a request.
        
        Args:
            url: Request URL
            
        Returns:
            Cached response or None
        """
        return self.cache_manager.get(url)
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()
        logger.info("HTTPClient closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
