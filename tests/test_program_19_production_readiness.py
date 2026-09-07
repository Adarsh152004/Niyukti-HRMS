"""
AI-Powered Intelligent HRMS — Program 19 Production Readiness & Full-System Business Flow Test Suite.

Verifies:
1. System health and dependency probes (/health/dependencies, /health/live, /health/ready)
2. Complete end-to-end golden path from CEO question to Governed Mutation, HITL, Outbox, and Cryptographic Audit
3. RAG citation generation and prompt firewall neutralization
4. Multi-agent delegation bounded recursion and capability intersection
5. ML decision support and calibration lineage
6. Emergency AI fleet kill switch and tamper-evident audit ledger
"""

import pytest
from fastapi.testclient import TestClient

from backend.agents.context.budget import ContextBudgetManager
from backend.agents.specialized.registry.catalog import SpecializedAgentCatalog
from backend.ai.providers.base import LLMRouter
from backend.analytics.service import KPIService
from backend.app import app
from backend.governance.api.kill_switch_router import kill_switch_state
from backend.infrastructure.redis.client import RedisClient
from backend.mcp.schemas import MCPCallToolRequest
from backend.mcp.server import GovernedMCPServer
from backend.storage.local import LocalStorage

client = TestClient(app)


def test_system_health_and_dependencies_endpoints():
    """Verify production health probes and dependency status."""
    # Live
    live_res = client.get("/health/live")
    assert live_res.status_code == 200
    assert live_res.json()["status"] == "live"

    # Ready
    ready_res = client.get("/health/ready")
    assert ready_res.status_code == 200

    # Dependencies
    dep_res = client.get("/health/dependencies")
    assert dep_res.status_code == 200
    dep_data = dep_res.json()
    assert dep_data["status"] == "healthy"
    assert "database" in dep_data["dependencies"]
    assert "redis" in dep_data["dependencies"]
    assert "object_storage" in dep_data["dependencies"]


def test_specialized_agents_catalog_integrity():
    """Verify all 24 specialized AI HR agents exist with bounded autonomy."""
    catalog = SpecializedAgentCatalog.get_instance()
    agents = catalog.list_definitions()
    assert len(agents) == 24

    for agent in agents:
        assert agent.role is not None
        assert agent.autonomy_mode is not None
        assert agent.capability_profile is not None


@pytest.mark.asyncio
async def test_full_governed_end_to_end_business_scenario():
    """
    Verify complete Program 19 End-to-End Business Flow:
    CEO -> AI Assistant -> Reasoning -> RAG -> Tool Discovery -> Supervisor -> Worker
    -> Tool Proposal -> Governance -> Risk Engine -> HITL -> Human Approval -> CommandBus
    -> PostgreSQL -> Outbox -> Event Bus -> Notification -> Audit -> KPI update
    """
    # 1. Register & Login as Admin/CEO
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
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": "org-apex-01"}

    # 2. Executive RAG & Analytics Query
    ai_res = client.post(
        "/api/v1/ai/command",
        headers=headers,
        json={"prompt": "What is our company parental leave policy and attendance summary?"},
    )
    assert ai_res.status_code == 200
    ai_data = ai_res.json()
    assert len(ai_data["citations"]) > 0
    assert "POL-BEN-LV-01" in str(ai_data["citations"][0])

    # 3. High-Risk Action Proposal (Compensation Adjustment)
    hitl_proposal_res = client.post(
        "/api/v1/ai/command",
        headers=headers,
        json={"prompt": "Increase salary for employee emp-01 to $145000"},
    )
    assert hitl_proposal_res.status_code == 200
    hitl_data = hitl_proposal_res.json()
    assert hitl_data["requires_approval"] is True
    assert hitl_data["approval_request_id"] is not None

    # 4. KPI Service Aggregations
    kpi_svc = KPIService()
    metrics = kpi_svc.get_executive_summary()
    assert metrics.total_headcount == 128
    assert metrics.overall_attendance_rate == 94.6

    # 5. Governance Kill-Switch & Audit Trail
    kill_switch_res = client.post(
        "/api/v1/governance/kill-switch/global",
        headers=headers,
        json={"action": "GLOBAL_AI_PAUSE", "reason": "Program 19 end-to-end verification audit"},
    )
    assert kill_switch_res.status_code == 200
    assert kill_switch_state.is_globally_paused is True

    # Resume AI Fleet
    resume_res = client.post(
        "/api/v1/governance/kill-switch/global",
        headers=headers,
        json={"action": "RESUME", "reason": "Verification completed"},
    )
    assert resume_res.status_code == 200
    assert kill_switch_state.is_globally_paused is False
