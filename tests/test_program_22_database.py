"""
AI-Powered Intelligent HRMS — Program 22 Database & Persistence Test Suite.

Verifies:
1. Health & Dependency Probes
2. Redis Distributed Locks & Rate Limiting
3. Object Storage HMAC Signed URLs & File Deletion
"""

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.infrastructure.redis.cache import DistributedLock, RedisRateLimiter
from backend.infrastructure.redis.client import RedisClient
from backend.storage.local import LocalStorage

client = TestClient(app)


def test_database_and_dependency_health_probes():
    """Verify live, ready, and dependency probes return nominal status."""
    live_res = client.get("/health/live")
    assert live_res.status_code == 200
    assert live_res.json()["status"] == "live"

    ready_res = client.get("/health/ready")
    assert ready_res.status_code == 200

    dep_res = client.get("/health/dependencies")
    assert dep_res.status_code == 200
    dep_data = dep_res.json()
    assert dep_data["status"] == "healthy"
    assert "database" in dep_data["dependencies"]
    assert "redis" in dep_data["dependencies"]
    assert "object_storage" in dep_data["dependencies"]


@pytest.mark.asyncio
async def test_redis_cache_and_distributed_locks():
    """Verify Redis client caching and distributed lock acquisition."""
    redis = RedisClient.get_instance()
    await redis.set("p22_key", "active_val", ex=10)
    assert await redis.get("p22_key") == "active_val"

    lock = DistributedLock("p22_test_lock", ttl_seconds=5)
    assert await lock.acquire() is True
    await lock.release()

    limiter = RedisRateLimiter()
    allowed, _, _ = await limiter.is_allowed("p22_actor", max_requests=10, window_seconds=60)
    assert allowed is True


@pytest.mark.asyncio
async def test_object_storage_signed_urls():
    """Verify object storage file upload and HMAC signed URL generation."""
    storage = LocalStorage()
    content = b"PROGRAM 22 STORAGE VERIFICATION"
    stored = await storage.upload("org-apex-01", "report_p22.txt", "text/plain", content)
    assert stored.size_bytes == len(content)

    signed_url = await storage.generate_signed_url("org-apex-01", stored.object_key)
    assert "sig=" in signed_url
    assert await storage.delete("org-apex-01", stored.object_key) is True
