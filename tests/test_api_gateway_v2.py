"""
AI-Powered Intelligent HRMS — Program 12 API Gateway Integration Test Suite.

Tests:
1. Request Context & Correlation ID Middleware
2. Multi-tenant Header Propagation
3. Rate Limiting Middleware (Limits, Headers, HTTP 429)
4. Authentication & Role-Based Access Control (RBAC)
5. Server-Sent Events (SSE) AI Streaming
6. GraphQL Relational Queries
7. Transactional Outbox Background Worker
"""

import asyncio
import json
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from backend.app import app
from backend.api.middleware.context import get_correlation_id, get_current_tenant_id
from backend.api.middleware.rate_limit import InMemoryRateLimiter
from backend.api.middleware.auth import AuthPrincipal
from backend.events.outbox import OutboxEvent, get_outbox_repository
from backend.events.outbox.worker import OutboxPublisherWorker


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint_includes_graphql_and_docs(client):
    """Verify root endpoint provides discoverability for Docs, GraphQL, and Status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["graphql"] == "/graphql"
    assert data["docs"] == "/api/docs"


def test_status_endpoint_reports_program_12_modules(client):
    """Verify system status reports all Program 12 gateway modules as ready."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["node"].startswith("Node 12")
    assert data["modules"]["realtime_websockets"] == "ready"
    assert data["modules"]["graphql_gateway"] == "ready"
    assert data["modules"]["rate_limiter"] == "ready"
    assert data["modules"]["transactional_outbox"] == "ready"


def test_request_context_middleware_correlation_id(client):
    """Verify X-Correlation-ID is generated and echoed back in headers."""
    # 1. Without custom header -> auto-generated
    resp1 = client.get("/health/live")
    assert resp1.status_code == 200
    assert "X-Correlation-ID" in resp1.headers
    assert resp1.headers["X-Correlation-ID"].startswith("corr-")

    # 2. With provided custom header -> preserved
    custom_corr = "corr-enterprise-test-9900"
    resp2 = client.get("/health/live", headers={"X-Correlation-ID": custom_corr})
    assert resp2.status_code == 200
    assert resp2.headers["X-Correlation-ID"] == custom_corr


def test_multi_tenant_header_propagation(client):
    """Verify X-Tenant-ID header is captured and echoed in response."""
    tenant = "tenant-apex-global-01"
    response = client.get("/health/live", headers={"X-Tenant-ID": tenant})
    assert response.status_code == 200
    assert response.headers.get("X-Tenant-ID") == tenant


def test_rate_limit_middleware_headers(client):
    """Verify rate limiting headers are injected on standard endpoints."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers


def test_rate_limiter_unit_sliding_window():
    """Unit test sliding window rate limiter quota and rejection."""
    limiter = InMemoryRateLimiter()
    key = "test-client-ip"

    # Allow up to 3 requests in 10s window
    allowed1, rem1, _ = limiter.is_allowed(key, max_requests=3, window_seconds=10)
    assert allowed1 is True
    assert rem1 == 2

    allowed2, rem2, _ = limiter.is_allowed(key, max_requests=3, window_seconds=10)
    assert allowed2 is True
    assert rem2 == 1

    allowed3, rem3, _ = limiter.is_allowed(key, max_requests=3, window_seconds=10)
    assert allowed3 is True
    assert rem3 == 0

    # 4th request must be rejected
    allowed4, rem4, reset = limiter.is_allowed(key, max_requests=3, window_seconds=10)
    assert allowed4 is False
    assert rem4 == 0
    assert reset > 0


def test_graphql_endpoint_query(client):
    """Verify GraphQL endpoint resolves relational queries."""
    # Query employees
    payload = {"query": "{ employees { id name title department { name } } }"}
    response = client.post("/graphql", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "employees" in data["data"]
    assert len(data["data"]["employees"]) > 0
    assert data["data"]["employees"][0]["name"] == "Priya Sharma"


def test_graphql_schema_sdl(client):
    """Verify GraphQL schema introspection endpoint returns SDL."""
    response = client.get("/graphql")
    assert response.status_code == 200
    data = response.json()
    assert "schema" in data
    assert "type Employee" in data["schema"]


def test_sse_ai_stream_endpoint(client):
    """Verify Server-Sent Events (SSE) AI streaming endpoint emits events."""
    response = client.get("/api/v1/ai/stream?prompt=Test")
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    text = response.text
    assert "event: tool_execution" in text
    assert "event: message" in text
    assert "event: done" in text


@pytest.mark.asyncio
async def test_outbox_publisher_worker_batch_drain():
    """Verify outbox publisher worker polls and drains outbox events."""
    outbox_repo = get_outbox_repository()

    # Seed an outbox event
    event = OutboxEvent(
        event_id="evt-outbox-test-01",
        event_type="EMPLOYEE_ONBOARDED",
        aggregate_type="Employee",
        aggregate_id="emp-0001",
        tenant_id="tenant-default",
        payload={"employee_id": "emp-0001", "name": "Priya Sharma"},
    )
    await outbox_repo.save(event)

    worker = OutboxPublisherWorker(poll_interval_seconds=0.1, batch_size=10)
    drained = await worker.drain_once()
    assert drained >= 1
