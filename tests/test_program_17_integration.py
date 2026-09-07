"""
AI-Powered Intelligent HRMS — Program 17 Full System Integration Test Suite.

Verifies:
1. Redis infrastructure client, in-memory fallback, distributed locks, rate limiting & idempotency
2. Object storage upload, download, deletion & signed URL generation
3. Multi-provider LLM gateway & structured ReasoningDecision schemas
4. Context window token budgeting & history compression
5. Governed Model Context Protocol (MCP) server & tool execution
6. Unified Authentication API endpoints (Login, Refresh, Me)
7. Analytics & KPI engine aggregations
8. AI Command Center natural language reasoning & HITL routing
"""

import pytest
from fastapi.testclient import TestClient

from backend.agents.context.budget import ContextBudgetManager, TokenBudgetAllocation
from backend.agents.context.compressor import ContextCompressor
from backend.ai.providers.base import LLMRouter, MockLLMProvider
from backend.ai.schemas import DecisionType, ReasoningDecision, ToolProposal
from backend.analytics.service import KPIService
from backend.app import app
from backend.infrastructure.redis.cache import (
    CacheManager,
    DistributedLock,
    IdempotencyManager,
    RedisRateLimiter,
)
from backend.infrastructure.redis.client import RedisClient
from backend.mcp.schemas import MCPCallToolRequest
from backend.mcp.server import GovernedMCPServer
from backend.storage.local import LocalStorage


@pytest.mark.asyncio
async def test_redis_client_and_fallback_store():
    """Verify Redis client get, set, delete with fallback in-memory store."""
    client = RedisClient.get_instance()
    await client.set("key_1", "value_1", ex=60)
    assert await client.get("key_1") == "value_1"
    assert await client.exists("key_1") == 1

    await client.delete("key_1")
    assert await client.get("key_1") is None


@pytest.mark.asyncio
async def test_distributed_lock_lifecycle():
    """Verify distributed lock acquire and release semantics."""
    lock = DistributedLock(lock_name="test_res_01", ttl_seconds=10)
    acquired = await lock.acquire()
    assert acquired is True

    # Concurrent acquire on same lock should fail
    lock2 = DistributedLock(lock_name="test_res_01", ttl_seconds=10)
    assert await lock2.acquire() is False

    # Release lock
    assert await lock.release() is True
    assert await lock2.acquire() is True
    await lock2.release()


@pytest.mark.asyncio
async def test_redis_rate_limiter_and_idempotency():
    """Verify rate limiter decrement and idempotency result caching."""
    limiter = RedisRateLimiter()
    allowed, remaining, _ = await limiter.is_allowed("user_ip_1", max_requests=2, window_seconds=60)
    assert allowed is True
    assert remaining == 1

    allowed, remaining, _ = await limiter.is_allowed("user_ip_1", max_requests=2, window_seconds=60)
    assert allowed is True
    assert remaining == 0

    allowed, remaining, _ = await limiter.is_allowed("user_ip_1", max_requests=2, window_seconds=60)
    assert allowed is False

    # Idempotency
    idemp = IdempotencyManager()
    await idemp.record_result("org-01", "cmd-key-99", {"status": "SUCCESS", "id": 101})
    cached = await idemp.get_result("org-01", "cmd-key-99")
    assert cached == {"status": "SUCCESS", "id": 101}


@pytest.mark.asyncio
async def test_object_storage_operations():
    """Verify local object storage upload, download, and signed URLs."""
    storage = LocalStorage()
    obj = await storage.upload("tenant-01", "resume.pdf", "application/pdf", b"PDF CONTENT DUMMY")
    assert obj.size_bytes == 17
    assert obj.object_key.endswith(".pdf")

    downloaded = await storage.download("tenant-01", obj.object_key)
    assert downloaded == b"PDF CONTENT DUMMY"

    signed_url = await storage.generate_signed_url("tenant-01", obj.object_key)
    assert "sig=" in signed_url

    deleted = await storage.delete("tenant-01", obj.object_key)
    assert deleted is True


@pytest.mark.asyncio
async def test_multi_provider_llm_gateway():
    """Verify LLM router produces structured ReasoningDecision schemas."""
    router = LLMRouter()
    res = await router.generate_reasoning(
        system_prompt="You are an HR Assistant",
        user_prompt="Show employees with attendance below 85%",
    )
    assert res.decision is not None
    assert res.decision.decision_type == DecisionType.TOOL_PROPOSAL
    assert res.decision.tool_proposal.tool_name == "attendance.summary"


def test_context_budget_manager():
    """Verify token budgeting truncates oversized inputs."""
    mgr = ContextBudgetManager(allocation=TokenBudgetAllocation(user_prompt_limit=10))
    long_prompt = "A" * 1000  # 250 tokens > 10 token limit
    ctx, usage = mgr.assemble_budgeted_context("System prompt", long_prompt)

    assert "Context truncated" in ctx["user_prompt"]
    assert usage.user_tokens <= 25


def test_context_compressor():
    """Verify context compressor summarizes old turns."""
    comp = ContextCompressor(max_history_turns=3)
    history = [
        {"role": "user", "content": "Initial prompt"},
        {"role": "assistant", "content": "Turn 1"},
        {"role": "user", "content": "Turn 2"},
        {"role": "assistant", "content": "Turn 3"},
        {"role": "user", "content": "Turn 4"},
    ]
    compressed = comp.compress_history(history)
    assert len(compressed) <= 4
    assert "[Earlier conversation history" in compressed[1]["content"]


@pytest.mark.asyncio
async def test_governed_mcp_server():
    """Verify MCP Server lists tools and creates HITL gate for high risk tool."""
    mcp = GovernedMCPServer.get_instance()
    tools = mcp.list_tools()
    assert len(tools) >= 6

    # Low risk tool executes
    low_res = await mcp.execute_tool(MCPCallToolRequest(
        tool_name="attendance.summary",
        arguments={"threshold_percentage": 85.0},
        tenant_id="org-apex",
        actor_id="usr-01",
    ))
    assert low_res.success is True
    assert len(low_res.data) >= 2

    # High risk tool requires approval
    high_res = await mcp.execute_tool(MCPCallToolRequest(
        tool_name="payroll.update_salary",
        arguments={"employee_id": "emp-01", "amount": 140000},
        tenant_id="org-apex",
        actor_id="usr-01",
    ))
    assert high_res.requires_approval is True
    assert high_res.approval_request_id.startswith("hitl-mcp-")


def test_auth_and_ai_command_api_endpoints():
    """Verify REST API v1 endpoints for Auth and AI Command Center."""
    client = TestClient(app)

    # 1. Register User
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": "org-apex-01",
            "username": "admin_test",
            "email": "admintest@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    assert reg_res.status_code in [200, 201]

    # 2. Login User
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": "org-apex-01",
            "email": "admintest@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    assert login_res.status_code == 200
    token_data = login_res.json()["data"]
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Get Me
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["success"] is True
    assert me_res.json()["data"]["organization_id"] == "org-apex-01"

    # 4. AI Command
    cmd_res = client.post(
        "/api/v1/ai/command",
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": "Show employees with attendance below 85%"},
    )
    assert cmd_res.status_code == 200
    cmd_data = cmd_res.json()
    assert cmd_data["tool_executed"] == "attendance.summary"
    assert cmd_data["suggested_visualization"] == "bar_chart"

    # 5. Analytics Dashboard
    dash_res = client.get("/api/v1/analytics/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert dash_res.status_code == 200
    assert dash_res.json()["summary"]["total_headcount"] == 128
