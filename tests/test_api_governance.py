"""
Tests for API Governance (Pagination, Idempotency, Rate Limiting).
"""

from __future__ import annotations

import pytest

from backend.api.governance.idempotency import IdempotencyConflictError, IdempotencyEngine
from backend.api.governance.models import (
    PaginatedResponse,
    PaginationParams,
    StandardErrorDetail,
    StandardErrorEnvelope,
)
from backend.api.governance.rate_limiter import (
    RateLimitExceededError,
    SlidingWindowRateLimiter,
)


def test_pagination_models():
    params = PaginationParams(page=2, page_size=25)
    assert params.page == 2
    assert params.page_size == 25

    response = PaginatedResponse[str](
        items=["item1", "item2"],
        total_count=50,
        page=2,
        page_size=25,
        total_pages=2,
        has_next=False,
        has_previous=True,
    )
    assert response.total_pages == 2
    assert response.has_previous is True


def test_error_envelope():
    err = StandardErrorEnvelope(
        error=StandardErrorDetail(code="RESOURCE_NOT_FOUND", message="Employee not found"),
        request_id="req-12345",
        status_code=404,
    )
    assert err.error.code == "RESOURCE_NOT_FOUND"
    assert err.status_code == 404


@pytest.mark.asyncio
async def test_idempotency_engine():
    engine = IdempotencyEngine.get_instance()
    await engine.clear()

    key = "idem-abc-123"
    org_id = "org-1"
    actor_id = "user-1"
    path = "/api/v1/leave/apply"
    payload = {"leave_type": "ANNUAL", "days": 3}

    # Initial check -> should be None
    record = await engine.get_or_lock(key, org_id, actor_id, path, payload)
    assert record is None

    # Store response
    await engine.store_response(
        idempotency_key=key,
        organization_id=org_id,
        actor_id=actor_id,
        request_path=path,
        payload=payload,
        status_code=201,
        response_body={"leave_id": "lev-999", "status": "PENDING"},
    )

    # Subsequent retrieval with same payload -> cache hit
    hit = await engine.get_or_lock(key, org_id, actor_id, path, payload)
    assert hit is not None
    assert hit.status_code == 201
    assert hit.response_body["leave_id"] == "lev-999"

    # Reuse key with DIFFERENT payload -> raises IdempotencyConflictError
    diff_payload = {"leave_type": "SICK", "days": 10}
    with pytest.raises(IdempotencyConflictError):
        await engine.get_or_lock(key, org_id, actor_id, path, diff_payload)


@pytest.mark.asyncio
async def test_rate_limiter():
    limiter = SlidingWindowRateLimiter.get_instance()
    await limiter.reset()

    org_id = "org-1"
    actor_id = "actor-1"
    endpoint = "auth.login"

    limiter.set_policy(endpoint, max_requests=3, window_seconds=60)

    # 3 allowed requests
    assert await limiter.check_rate_limit(org_id, actor_id, endpoint) is True
    assert await limiter.check_rate_limit(org_id, actor_id, endpoint) is True
    assert await limiter.check_rate_limit(org_id, actor_id, endpoint) is True

    # 4th request -> RateLimitExceededError
    with pytest.raises(RateLimitExceededError) as exc_info:
        await limiter.check_rate_limit(org_id, actor_id, endpoint)
    assert exc_info.value.retry_after_seconds > 0
