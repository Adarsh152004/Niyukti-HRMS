"""
API Rate Limiter — Sliding window rate limiting per tenant, actor, and tier.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import NamedTuple

logger = logging.getLogger(__name__)


class RateLimitPolicy(NamedTuple):
    max_requests: int
    window_seconds: int


class RateLimitExceededError(Exception):
    """Raised when an actor or tenant exceeds rate limit."""

    def __init__(self, message: str, retry_after_seconds: int = 60) -> None:
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter."""

    _instance: SlidingWindowRateLimiter | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._request_timestamps: dict[str, list[datetime]] = {}
        self._default_policy = RateLimitPolicy(max_requests=120, window_seconds=60)
        self._endpoint_policies: dict[str, RateLimitPolicy] = {}

    @classmethod
    def get_instance(cls) -> SlidingWindowRateLimiter:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_policy(self, endpoint_key: str, max_requests: int, window_seconds: int) -> None:
        """Register specific rate limit policy for an endpoint."""
        self._endpoint_policies[endpoint_key] = RateLimitPolicy(max_requests, window_seconds)

    async def check_rate_limit(
        self,
        organization_id: str,
        actor_id: str,
        endpoint_key: str = "default",
    ) -> bool:
        """
        Check and record request.
        Raises RateLimitExceededError if limit is reached.
        """
        policy = self._endpoint_policies.get(endpoint_key, self._default_policy)
        now = datetime.now(tz=UTC)
        window_start = now - timedelta(seconds=policy.window_seconds)
        bucket_key = f"{organization_id}:{actor_id}:{endpoint_key}"

        async with self._lock:
            timestamps = self._request_timestamps.get(bucket_key, [])
            # Evict expired entries
            valid_timestamps = [ts for ts in timestamps if ts > window_start]

            if len(valid_timestamps) >= policy.max_requests:
                oldest = valid_timestamps[0]
                retry_after = int((oldest + timedelta(seconds=policy.window_seconds) - now).total_seconds())
                retry_after = max(1, retry_after)
                logger.warning(f"Rate limit exceeded for {bucket_key}. Retry after {retry_after}s")
                raise RateLimitExceededError(
                    f"Rate limit exceeded for endpoint '{endpoint_key}'. Allowed: {policy.max_requests} req / {policy.window_seconds}s.",
                    retry_after_seconds=retry_after,
                )

            valid_timestamps.append(now)
            self._request_timestamps[bucket_key] = valid_timestamps
            return True

    async def reset(self) -> None:
        """Reset all rate limit buckets (useful for tests)."""
        async with self._lock:
            self._request_timestamps.clear()
