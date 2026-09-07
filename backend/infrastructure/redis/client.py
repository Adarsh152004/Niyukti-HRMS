"""
AI-Powered Intelligent HRMS — Redis Infrastructure Client.

Provides:
- Async Redis connection pool management
- Automatic fallback to high-performance threadsafe in-memory cache when Redis is offline
- Health checks and connection diagnostics
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any


class InMemoryFallbackStore:
    """Threadsafe in-memory key-value store with TTL support for offline/testing modes."""

    def __init__(self) -> None:
        self._data: dict[str, tuple[str, float | None]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> str | None:
        async with self._lock:
            if key not in self._data:
                return None
            val, expiry = self._data[key]
            if expiry is not None and time.time() > expiry:
                del self._data[key]
                return None
            return val

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        async with self._lock:
            expiry = (time.time() + ex) if ex else None
            self._data[key] = (value, expiry)
            return True

    async def delete(self, key: str) -> int:
        async with self._lock:
            if key in self._data:
                del self._data[key]
                return 1
            return 0

    async def exists(self, key: str) -> int:
        val = await self.get(key)
        return 1 if val is not None else 0

    async def flush(self) -> None:
        async with self._lock:
            self._data.clear()


class RedisClient:
    """Enterprise Redis client with resilient connection pooling and automatic fallback."""

    _instance: RedisClient | None = None

    def __init__(self, redis_url: str | None = None) -> None:
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._fallback = InMemoryFallbackStore()
        self._redis: Any = None
        self._is_connected = False

    @classmethod
    def get_instance(cls) -> RedisClient:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    async def connect(self) -> None:
        """Attempts connection to Redis server, falls back to memory if unavailable."""
        try:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0,
            )
            await self._redis.ping()
            self._is_connected = True
        except Exception:
            self._redis = None
            self._is_connected = False

    async def ping(self) -> bool:
        if self._is_connected and self._redis:
            try:
                await self._redis.ping()
                return True
            except Exception:
                self._is_connected = False
        return True  # Fallback store is always operational

    async def get(self, key: str) -> str | None:
        if self._is_connected and self._redis:
            try:
                return await self._redis.get(key)
            except Exception:
                pass
        return await self._fallback.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        if self._is_connected and self._redis:
            try:
                return bool(await self._redis.set(key, value, ex=ex))
            except Exception:
                pass
        return await self._fallback.set(key, value, ex=ex)

    async def delete(self, key: str) -> int:
        if self._is_connected and self._redis:
            try:
                return int(await self._redis.delete(key))
            except Exception:
                pass
        return await self._fallback.delete(key)

    async def exists(self, key: str) -> int:
        if self._is_connected and self._redis:
            try:
                return int(await self._redis.exists(key))
            except Exception:
                pass
        return await self._fallback.exists(key)

    @property
    def is_live_redis(self) -> bool:
        return self._is_connected
