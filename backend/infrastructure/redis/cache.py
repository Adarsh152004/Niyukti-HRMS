"""
AI-Powered Intelligent HRMS — Redis Infrastructure Services.

Implements:
- Cache Manager with tenant namespace partitioning and TTL
- Distributed async Lock Manager with automatic release
- Redis-backed Sliding Window Rate Limiter
- Idempotency Cache for deduplicating mutation commands
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Any, Callable

from backend.infrastructure.redis.client import RedisClient


class CacheManager:
    """Tenant-isolated cache manager."""

    def __init__(self, client: RedisClient | None = None) -> None:
        self.client = client or RedisClient.get_instance()

    def _make_key(self, tenant_id: str, namespace: str, key: str) -> str:
        return f"hrms:{tenant_id}:{namespace}:{key}"

    async def get_json(self, tenant_id: str, namespace: str, key: str) -> Any | None:
        full_key = self._make_key(tenant_id, namespace, key)
        raw = await self.client.get(full_key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    async def set_json(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        value: Any,
        ttl_seconds: int = 300,
    ) -> bool:
        full_key = self._make_key(tenant_id, namespace, key)
        encoded = json.dumps(value)
        return await self.client.set(full_key, encoded, ex=ttl_seconds)

    async def invalidate(self, tenant_id: str, namespace: str, key: str) -> bool:
        full_key = self._make_key(tenant_id, namespace, key)
        return bool(await self.client.delete(full_key))


class DistributedLock:
    """Distributed lock implementation."""

    def __init__(
        self,
        lock_name: str,
        ttl_seconds: int = 30,
        client: RedisClient | None = None,
    ) -> None:
        self.lock_name = f"hrms:lock:{lock_name}"
        self.ttl = ttl_seconds
        self.client = client or RedisClient.get_instance()
        self.lock_token = str(uuid.uuid4())
        self._acquired = False

    async def acquire(self) -> bool:
        current = await self.client.get(self.lock_name)
        if current is None:
            await self.client.set(self.lock_name, self.lock_token, ex=self.ttl)
            self._acquired = True
            return True
        return False

    async def release(self) -> bool:
        if not self._acquired:
            return False
        current = await self.client.get(self.lock_name)
        if current == self.lock_token:
            await self.client.delete(self.lock_name)
            self._acquired = False
            return True
        return False

    async def __aenter__(self) -> bool:
        return await self.acquire()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.release()


class RedisRateLimiter:
    """Sliding-window rate limiter using Redis key expiration."""

    def __init__(self, client: RedisClient | None = None) -> None:
        self.client = client or RedisClient.get_instance()

    async def is_allowed(
        self,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60,
    ) -> tuple[bool, int, int]:
        """
        Returns (is_allowed, remaining_quota, reset_seconds).
        """
        key = f"hrms:rl:{identifier}"
        raw = await self.client.get(key)
        count = int(raw) if raw else 0

        if count >= max_requests:
            return False, 0, window_seconds

        await self.client.set(key, str(count + 1), ex=window_seconds)
        remaining = max(0, max_requests - (count + 1))
        return True, remaining, window_seconds


class IdempotencyManager:
    """Caches command results by idempotency key to prevent double execution."""

    def __init__(self, client: RedisClient | None = None) -> None:
        self.client = client or RedisClient.get_instance()

    def _make_key(self, tenant_id: str, idempotency_key: str) -> str:
        return f"hrms:idempotency:{tenant_id}:{idempotency_key}"

    async def get_result(self, tenant_id: str, idempotency_key: str) -> dict[str, Any] | None:
        key = self._make_key(tenant_id, idempotency_key)
        raw = await self.client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    async def record_result(
        self,
        tenant_id: str,
        idempotency_key: str,
        result: dict[str, Any],
        ttl_seconds: int = 86400,
    ) -> bool:
        key = self._make_key(tenant_id, idempotency_key)
        return await self.client.set(key, json.dumps(result), ex=ttl_seconds)
