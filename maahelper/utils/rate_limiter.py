#!/usr/bin/env python3
"""
Rate Limiting and Retry Logic
Implements rate limiting, retry mechanisms, and request throttling for API calls
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from functools import wraps

from rich.console import Console

console = Console()


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    burst_limit: int = 10
    retry_attempts: int = 3
    retry_delay: float = 1.0
    backoff_multiplier: float = 2.0
    max_retry_delay: float = 60.0


@dataclass
class RequestRecord:
    """Record of a request for rate limiting"""
    timestamp: float
    provider: str
    model: str
    tokens: int = 0


class RateLimiter:
    """Rate limiter with sliding window and burst protection"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.burst_counts: Dict[str, int] = defaultdict(int)
        self.last_reset: Dict[str, float] = defaultdict(float)
    
    def _get_key(self, provider: str, model: str = "") -> str:
        """Get rate limiting key for provider/model combination"""
        return f"{provider}:{model}" if model else provider
    
    def _cleanup_old_requests(self, key: str, window_seconds: int) -> None:
        """Remove requests older than the window"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        while self.requests[key] and self.requests[key][0].timestamp < cutoff_time:
            self.requests[key].popleft()
    
    def _reset_burst_if_needed(self, key: str) -> None:
        """Reset burst counter if enough time has passed"""
        current_time = time.time()
        if current_time - self.last_reset[key] >= 60:  # Reset every minute
            self.burst_counts[key] = 0
            self.last_reset[key] = current_time
    
    def can_make_request(self, provider: str, model: str = "") -> bool:
        """Check if a request can be made without hitting rate limits"""
        key = self._get_key(provider, model)
        current_time = time.time()
        
        # Cleanup old requests
        self._cleanup_old_requests(key, 60)  # 1 minute window
        self._cleanup_old_requests(key, 3600)  # 1 hour window
        
        # Reset burst counter if needed
        self._reset_burst_if_needed(key)
        
        # Check rate limits
        minute_requests = len([r for r in self.requests[key] if current_time - r.timestamp <= 60])
        hour_requests = len([r for r in self.requests[key] if current_time - r.timestamp <= 3600])
        
        # Check limits
        if minute_requests >= self.config.requests_per_minute:
            return False
        
        if hour_requests >= self.config.requests_per_hour:
            return False
        
        if self.burst_counts[key] >= self.config.burst_limit:
            return False
        
        return True
    
    def record_request(self, provider: str, model: str = "", tokens: int = 0) -> None:
        """Record a request for rate limiting"""
        key = self._get_key(provider, model)
        current_time = time.time()
        
        # Record the request
        record = RequestRecord(
            timestamp=current_time,
            provider=provider,
            model=model,
            tokens=tokens
        )
        self.requests[key].append(record)
        
        # Increment burst counter
        self.burst_counts[key] += 1
    
    def get_wait_time(self, provider: str, model: str = "") -> float:
        """Get the time to wait before the next request can be made"""
        if self.can_make_request(provider, model):
            return 0.0
        
        key = self._get_key(provider, model)
        current_time = time.time()
        
        # Find the oldest request in the minute window
        minute_requests = [r for r in self.requests[key] if current_time - r.timestamp <= 60]
        if len(minute_requests) >= self.config.requests_per_minute:
            oldest_in_minute = min(minute_requests, key=lambda r: r.timestamp)
            wait_time = 60 - (current_time - oldest_in_minute.timestamp)
            return max(0, wait_time)
        
        # Check burst limit
        if self.burst_counts[key] >= self.config.burst_limit:
            time_since_reset = current_time - self.last_reset[key]
            return max(0, 60 - time_since_reset)
        
        return 0.0
    
    async def wait_if_needed(self, provider: str, model: str = "") -> None:
        """Wait if rate limit would be exceeded"""
        wait_time = self.get_wait_time(provider, model)
        if wait_time > 0:
            console.print(f"[yellow]⏳ Rate limit reached. Waiting {wait_time:.1f}s for {provider}[/yellow]")
            await asyncio.sleep(wait_time)


class RetryHandler:
    """Handles retry logic with exponential backoff"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Determine if an error should be retried"""
        if attempt >= self.config.retry_attempts:
            return False
        
        # Check error type
        error_str = str(error).lower()
        
        # Retry on rate limits, timeouts, and connection errors
        retry_conditions = [
            "rate limit" in error_str,
            "timeout" in error_str,
            "connection" in error_str,
            "503" in error_str,  # Service unavailable
            "502" in error_str,  # Bad gateway
            "500" in error_str,  # Internal server error
        ]
        
        return any(retry_conditions)
    
    def get_delay(self, attempt: int) -> float:
        """Get delay for retry attempt with exponential backoff"""
        delay = self.config.retry_delay * (self.config.backoff_multiplier ** attempt)
        return min(delay, self.config.max_retry_delay)
    
    async def wait_for_retry(self, attempt: int) -> None:
        """Wait for retry with exponential backoff"""
        delay = self.get_delay(attempt)
        console.print(f"[yellow]🔄 Retrying in {delay:.1f}s (attempt {attempt + 1}/{self.config.retry_attempts})[/yellow]")
        await asyncio.sleep(delay)


class RateLimitedClient:
    """Wrapper that adds rate limiting and retry logic to any client"""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.rate_limiter = RateLimiter(self.config)
        self.retry_handler = RetryHandler(self.config)
    
    async def execute_with_limits(
        self,
        func: Callable,
        provider: str,
        model: str = "",
        *args,
        **kwargs
    ) -> Any:
        """Execute a function with rate limiting and retry logic"""
        
        for attempt in range(self.config.retry_attempts + 1):
            try:
                # Wait for rate limit if needed
                await self.rate_limiter.wait_if_needed(provider, model)
                
                # Record the request
                self.rate_limiter.record_request(provider, model)
                
                # Execute the function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                return result
                
            except Exception as e:
                if not self.retry_handler.should_retry(attempt, e):
                    raise e
                
                if attempt < self.config.retry_attempts:
                    await self.retry_handler.wait_for_retry(attempt)
                else:
                    raise e
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        stats = {}
        current_time = time.time()
        
        for key, requests in self.rate_limiter.requests.items():
            # Count requests in different windows
            minute_count = len([r for r in requests if current_time - r.timestamp <= 60])
            hour_count = len([r for r in requests if current_time - r.timestamp <= 3600])
            
            stats[key] = {
                "requests_last_minute": minute_count,
                "requests_last_hour": hour_count,
                "burst_count": self.rate_limiter.burst_counts[key],
                "can_make_request": self.rate_limiter.can_make_request(*key.split(":")),
                "wait_time": self.rate_limiter.get_wait_time(*key.split(":"))
            }
        
        return stats


def rate_limited(provider: str, model: str = "", config: Optional[RateLimitConfig] = None):
    """Decorator to add rate limiting to functions"""
    def decorator(func):
        client = RateLimitedClient(config)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await client.execute_with_limits(func, provider, model, *args, **kwargs)
        
        return wrapper
    return decorator


# Global rate limiter instance
global_rate_limiter = RateLimitedClient()
