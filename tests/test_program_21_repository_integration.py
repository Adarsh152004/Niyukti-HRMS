"""
AI-Powered Intelligent HRMS — Program 21 Repository Integration Test Suite.

Verifies:
1. Health & dependency probe responses (/health/dependencies, /health/live, /health/ready)
2. Redis distributed lock, rate limiting & cache operations
3. Object storage upload, signed URLs & HMAC validation
4. Dynamic KPI calculations and real aggregation summaries
5. Predictive ML calibration and continuous evaluation
"""

import pytest
from fastapi.testclient import TestClient

from backend.analytics.service import KPIService
from backend.app import app
from backend.infrastructure.redis.cache import DistributedLock, RedisRateLimiter
from backend.infrastructure.redis.client import RedisClient
from backend.ml.calibration.runner import ContinuousEvaluationRunner
from backend.storage.local import LocalStorage

client = TestClient(app)


def test_system_health_and_dependency_probes():
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
    await redis.set("p21_key", "active_val", ex=10)
    assert await redis.get("p21_key") == "active_val"

    lock = DistributedLock("p21_test_lock", ttl_seconds=5)
    assert await lock.acquire() is True
    await lock.release()

    limiter = RedisRateLimiter()
    allowed, _, _ = await limiter.is_allowed("p21_actor", max_requests=10, window_seconds=60)
    assert allowed is True


@pytest.mark.asyncio
async def test_object_storage_signed_urls():
    """Verify object storage file upload and HMAC signed URL generation."""
    storage = LocalStorage()
    stored = await storage.upload("org-apex-01", "report_p21.txt", "text/plain", b"PROGRAM 21 VERIFICATION")
    assert stored.size_bytes == 23

    signed_url = await storage.generate_signed_url("org-apex-01", stored.object_key)
    assert "sig=" in signed_url
    assert await storage.delete("org-apex-01", stored.object_key) is True


def test_dynamic_kpi_engine_aggregations():
    """Verify KPI service calculates real aggregations."""
    kpi_svc = KPIService()
    summary = kpi_svc.get_executive_summary()
    assert summary.total_headcount == 128
    assert summary.overall_attendance_rate == 94.6
    assert summary.monthly_payroll_spend_usd == 1240500.00
    assert len(kpi_svc.get_department_breakdown()) >= 5


def test_predictive_ml_calibration_runner():
    """Verify ML model continuous evaluation runner."""
    eval_runner = ContinuousEvaluationRunner()
    report = eval_runner.run_full_suite()
    assert report.overall_status == "PASSED"
    assert report.ml_calibration.expected_calibration_error <= 0.15
