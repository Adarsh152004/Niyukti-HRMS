"""
Tests for CEO / Handler Control Plane — Cockpit, Autonomy Matrix, Emergency Kill Switch, Quarantine, and Health Telemetry.
"""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from backend.agents.specialized.domain.enums import AutonomyMode, SpecializedAgentRole
from backend.app import app
from backend.hrms.application.executive_control_service import ExecutiveControlService


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {
        "X-Organization-ID": "org-ceo-cockpit",
        "X-Actor-ID": "ceo-user-01",
        "X-Actor-Type": "HUMAN",
        "X-Actor-Roles": "CEO,SUPER_ADMIN",
    }


@pytest.mark.asyncio
async def test_executive_service_autonomy_matrix_and_kill_switch():
    svc = ExecutiveControlService.get_instance()
    org_id = "org-service-test"

    # 1. Autonomy Matrix
    matrix = await svc.get_autonomy_matrix(org_id)
    assert len(matrix) == len(SpecializedAgentRole)

    # 2. Update Autonomy for Payroll Agent to SUPERVISED
    updated = await svc.update_agent_autonomy(
        organization_id=org_id,
        agent_role=SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT,
        new_mode=AutonomyMode.SUPERVISED,
        updated_by="ceo-user-01",
    )
    assert updated.autonomy_mode == AutonomyMode.SUPERVISED

    # 3. Kill Switch Activation
    assert not svc.is_kill_switch_active(org_id)
    k_state = await svc.activate_kill_switch(org_id, reason="Suspicious cross-agent activity", triggered_by="ceo-user-01")
    assert k_state.is_active is True
    assert svc.is_kill_switch_active(org_id)

    # 4. Cockpit reflects Degraded health
    cockpit = await svc.get_cockpit_summary(org_id)
    assert cockpit.kill_switch_active is True
    assert cockpit.system_health_status == "DEGRADED"

    # 5. Quarantine an agent
    q_rec = await svc.quarantine_agent(
        org_id, SpecializedAgentRole.RESUME_SCREENING_AGENT, reason="Outlier drift", triggered_by="ceo-user-01"
    )
    assert q_rec.agent_role == SpecializedAgentRole.RESUME_SCREENING_AGENT
    assert svc.is_agent_quarantined(org_id, SpecializedAgentRole.RESUME_SCREENING_AGENT)

    # 6. Deactivate Kill Switch & Unquarantine
    await svc.deactivate_kill_switch(org_id, triggered_by="ceo-user-01")
    assert not svc.is_kill_switch_active(org_id)

    unfrozen = await svc.unquarantine_agent(org_id, SpecializedAgentRole.RESUME_SCREENING_AGENT, triggered_by="ceo-user-01")
    assert unfrozen is True
    assert not svc.is_agent_quarantined(org_id, SpecializedAgentRole.RESUME_SCREENING_AGENT)


def test_executive_rest_api_endpoints(client: TestClient, auth_headers: dict[str, str]):
    # 1. GET /api/v1/executive/cockpit
    res1 = client.get("/api/v1/executive/cockpit", headers=auth_headers)
    assert res1.status_code == 200
    data1 = res1.json()["data"]
    assert "total_employees" in data1
    assert "active_specialized_agents" in data1

    # 2. GET /api/v1/executive/autonomy-matrix
    res2 = client.get("/api/v1/executive/autonomy-matrix", headers=auth_headers)
    assert res2.status_code == 200
    data2 = res2.json()["data"]
    assert len(data2) == len(SpecializedAgentRole)

    # 3. PUT /api/v1/executive/autonomy-matrix
    res3 = client.put(
        "/api/v1/executive/autonomy-matrix",
        headers=auth_headers,
        json={"agent_role": SpecializedAgentRole.RECRUITMENT_AGENT.value, "autonomy_mode": AutonomyMode.ADVISORY.value},
    )
    assert res3.status_code == 200
    assert res3.json()["data"]["autonomy_mode"] == AutonomyMode.ADVISORY.value

    # 4. POST /api/v1/executive/kill-switch/activate
    res4 = client.post(
        "/api/v1/executive/kill-switch/activate",
        headers=auth_headers,
        json={"reason": "Emergency drill test"},
    )
    assert res4.status_code == 200
    assert res4.json()["data"]["is_active"] is True

    # 5. POST /api/v1/executive/kill-switch/deactivate
    res5 = client.post("/api/v1/executive/kill-switch/deactivate", headers=auth_headers)
    assert res5.status_code == 200
    assert res5.json()["data"]["is_active"] is False

    # 6. GET /api/v1/executive/health
    res6 = client.get("/api/v1/executive/health", headers=auth_headers)
    assert res6.status_code == 200
    assert "layers" in res6.json()["data"]
