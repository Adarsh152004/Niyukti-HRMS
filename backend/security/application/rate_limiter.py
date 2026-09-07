"""
Rate Limiting & Brute Force Protection — Interface & In-Memory Implementation.

Provides rate limiting for authentication attempts, token refresh, and API key requests.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod


class RateLimiter(ABC):
    """Abstract interface for rate limiting."""

    @abstractmethod
    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if an action is allowed within rate limits.
        Returns True if allowed, False if rate limit exceeded.
        """
        pass

    @abstractmethod
    def record_attempt(self, key: str) -> None:
        """Record an attempt for rate limiting."""
        pass


class InMemoryRateLimiter(RateLimiter):
    """
    In-memory rate limiter using sliding window counters.
    """

    def __init__(self) -> None:
        # Maps key -> list of timestamps
        self._requests: dict[str, list[float]] = {}

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        cutoff = now - window_seconds

        timestamps = self._requests.get(key, [])
        # Prune old timestamps
        valid_timestamps = [ts for ts in timestamps if ts > cutoff]
        self._requests[key] = valid_timestamps

        return len(valid_timestamps) < max_requests

    def record_attempt(self, key: str) -> None:
        now = time.time()
        if key not in self._requests:
            self._requests[key] = []
        self._requests[key].append(now)

    def reset(self, key: str) -> None:
        """Reset rate limit history for a key."""
        if key in self._requests:
            del self._requests[key]
