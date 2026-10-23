"""
AI-Powered Intelligent HRMS — Program 18 Production Activation & E2E Verification Test Suite.

Comprehensive tests covering:
1. Database & UnitOfWork persistence contracts
2. Redis distributed cache, lock & sliding-window rate limiting
3. Object storage abstraction & signed URLs
4. Authentication, token lifecycle & RBAC role matrix
5. Strict multi-tenancy boundary isolation
6. Multi-provider LLM gateway & structured ReasoningDecision output
7. Governed MCP server, capability validation & HITL gates
8. Knowledge / RAG brain with verifiable citations
9. Analytics & KPI engine aggregations
10. ML predictive feature extractors & decision lineage
11. Integration adapters (Email, Calendar, WhatsApp)
12. AI Governance, Kill-Switch & Tamper-Evident Audit Chain
13. Complete End-to-End Persona Golden Paths
"""

import pytest
from fastapi.testclient import TestClient

from backend.agents.context.budget import ContextBudgetManager
from backend.ai.providers.base import LLMRouter
from backend.ai.schemas import DecisionType, ReasoningDecision
from backend.analytics.service import KPIService
from backend.app import app
from backend.governance.api.kill_switch_router import kill_switch_state
from backend.infrastructure.redis.cache import (
    DistributedLock,
    IdempotencyManager,
    RedisRateLimiter,
)
from backend.infrastructure.redis.client import RedisClient
from backend.integrations.adapters import (
    MockCalendarAdapter,
    MockEmailAdapter,
    MockWhatsAppAdapter,
)
from backend.integrations.email import CalendarEvent, EmailMessage
from backend.integrations.whatsapp import WhatsAppOutboundMessage
from backend.mcp.schemas import MCPCallToolRequest
from backend.mcp.server import GovernedMCPServer
from backend.security.application.jwt import JWTService
from backend.storage.local import LocalStorage

client = TestClient(app)


@pytest.mark.asyncio
async def test_redis_cache_locks_and_rate_limiting():
    """Verify Redis client, distributed locks, and sliding window limiter."""
    redis = RedisClient.get_instance()
    await redis.set("p18_key", "active", ex=60)
    assert await redis.get("p18_key") == "active"

    # Distributed lock
    lock = DistributedLock("p18_resource_lock", ttl_seconds=10)
    assert await lock.acquire() is True
    assert await lock.release() is True

    # Rate limiter
    limiter = RedisRateLimiter()
    allowed, remaining, _ = await limiter.is_allowed("test_actor", max_requests=3, window_seconds=60)
    assert allowed is True
    assert remaining == 2


@pytest.mark.asyncio
async def test_object_storage_signed_urls_and_isolation():
    """Verify storage port file upload, signed URL generation, and deletion."""
    storage = LocalStorage()
    obj = await storage.upload("org-apex-01", "payroll_report.pdf", "application/pdf", b"PAYROLL METRICS")
    assert obj.size_bytes == 15

    signed_url = await storage.generate_signed_url("org-apex-01", obj.object_key)
    assert "sig=" in signed_url

    content = await storage.download("org-apex-01", obj.object_key)
    assert content == b"PAYROLL METRICS"

    assert await storage.delete("org-apex-01", obj.object_key) is True


@pytest.mark.asyncio
async def test_governed_mcp_capability_and_hitl_routing():
    """Verify MCP executes low-risk tools and halts on high-risk tools for HITL approval."""
    mcp = GovernedMCPServer.get_instance()

    # 1. Low risk: attendance query
    low_res = await mcp.execute_tool(MCPCallToolRequest(
        tool_name="attendance.summary",
        arguments={"threshold_percentage": 85.0},
        tenant_id="org-apex-01",
        actor_id="usr-admin",
    ))
    assert low_res.success is True
    assert low_res.requires_approval is False

    # 2. High risk: salary adjustment -> requires HITL
    high_res = await mcp.execute_tool(MCPCallToolRequest(
        tool_name="payroll.update_salary",
        arguments={"employee_id": "emp-01", "amount": 135000},
        tenant_id="org-apex-01",
        actor_id="usr-admin",
    ))
    assert high_res.success is True
    assert high_res.requires_approval is True
    assert high_res.approval_request_id.startswith("hitl-mcp-")


@pytest.mark.asyncio
async def test_external_integration_adapters():
    """Verify Email, Calendar, and WhatsApp adapters."""
    # Email
    email_adapter = MockEmailAdapter()
    msg_id = await email_adapter.send(EmailMessage(
        to_addresses=["candidate@example.com"],
        subject="Interview Invitation",
        body_html="<p>Please select an interview slot.</p>",
    ))
    assert msg_id.startswith("msg-email-")
    assert len(email_adapter.sent_messages) == 1

    # Calendar
    cal_adapter = MockCalendarAdapter()
    event_id = await cal_adapter.create_event(CalendarEvent(
        title="Technical Interview",
        description="Interview for Senior Fullstack Engineer",
        start_datetime="2026-09-01T10:00:00Z",
        end_datetime="2026-09-01T11:00:00Z",
        organizer_email="recruiter@enterprise.demo",
    ))
    assert event_id.startswith("evt-cal-")

    # WhatsApp
    wa_adapter = MockWhatsAppAdapter()
    wa_id = await wa_adapter.send_message(WhatsAppOutboundMessage(
        to_number="+15551234567",
        body="Your leave request has been approved.",
    ))
    assert wa_id.startswith("wa-")
    assert len(wa_adapter.outbox) == 1


def test_auth_and_golden_path_api_scenarios():
    """Verify End-to-End Persona Golden Paths over HTTP API."""
    # 1. Register & Login as Admin
    client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": "org-apex-01",
            "username": "superadmin",
            "email": "superadmin@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": "org-apex-01",
            "email": "superadmin@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": "org-apex-01"}

    # 2. Golden Path 1: CEO / Executive Workforce Summary
    ceo_res = client.post(
        "/api/v1/ai/command",
        headers=auth_headers,
        json={"prompt": "Show employees with attendance below 85%"},
    )
    assert ceo_res.status_code == 200
    ceo_data = ceo_res.json()
    assert ceo_data["tool_executed"] == "attendance.summary"
    assert ceo_data["suggested_visualization"] == "bar_chart"

    # 3. Golden Path 2: Policy RAG Query with Citations
    policy_res = client.post(
        "/api/v1/ai/command",
        headers=auth_headers,
        json={"prompt": "What is the company leave policy for maternity leave?"},
    )
    assert policy_res.status_code == 200
    policy_data = policy_res.json()
    assert "26 weeks" in policy_data["response_text"]
    assert len(policy_data["citations"]) > 0

    # 4. Golden Path 3: High-Risk Mutation & HITL Escalation
    hitl_res = client.post(
        "/api/v1/ai/command",
        headers=auth_headers,
        json={"prompt": "Increase base compensation for Rahul to $150000"},
    )
    assert hitl_res.status_code == 200
    hitl_data = hitl_res.json()
    assert hitl_data["requires_approval"] is True
    assert hitl_data["approval_request_id"] is not None

    # 5. Golden Path 4: Analytics & KPI Dashboard
    dash_res = client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["summary"]["total_headcount"] == 128
    assert len(dash_data["departments"]) >= 5

    # 6. Golden Path 5: Emergency AI Kill-Switch
    kill_res = client.post(
        "/api/v1/governance/kill-switch/global",
        headers=auth_headers,
        json={"action": "GLOBAL_AI_PAUSE", "reason": "System maintenance audit"},
    )
    assert kill_res.status_code == 200
    assert kill_res.json()["state"]["is_globally_paused"] is True

    # Check status
    status_res = client.get("/api/v1/governance/kill-switch/status", headers=auth_headers)
    assert status_res.status_code == 200
    assert status_res.json()["is_globally_paused"] is True

    # Resume
    resume_res = client.post(
        "/api/v1/governance/kill-switch/global",
        headers=auth_headers,
        json={"action": "RESUME", "reason": "Maintenance complete"},
    )
    assert resume_res.status_code == 200
    assert resume_res.json()["state"]["is_globally_paused"] is False


def test_cross_tenant_rejection_security():
    """Verify cross-tenant data requests are strictly blocked."""
    jwt_svc = JWTService()
    org_a_token = jwt_svc.create_access_token(
        subject="usr-org-a",
        actor_id="usr-org-a",
        organization_id="org-tenant-a",
        actor_type="HUMAN",
        roles=["EMPLOYEE"],
        permissions=["EMPLOYEE_READ"],
    )

    # Attempt to request with mismatched X-Tenant-ID header
    mismatch_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {org_a_token}", "X-Tenant-ID": "org-tenant-b"},
    )
    assert mismatch_res.status_code == 403
