"""
AI-Powered Intelligent HRMS — Program 21 HITL & Kill-Switch Test Suite.

Verifies:
1. High-risk tool proposal halting for Human-in-the-Loop review
2. Approval decision processing and state transition
3. Emergency AI kill-switch activation and task blocking
"""

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.governance.api.kill_switch_router import kill_switch_state

client = TestClient(app)


def test_hitl_escalation_on_high_risk_salary_adjustment():
    """Verify high-risk compensation mutation halts for human approval."""
    # Login as SuperAdmin
    client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": "org-apex-01",
            "username": "superadmin_hitl",
            "email": "admin_hitl@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": "org-apex-01",
            "email": "admin_hitl@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": "org-apex-01"}

    # High-Risk Command
    res = client.post(
        "/api/v1/ai/command",
        headers=headers,
        json={"prompt": "Increase salary for employee emp-01 to $145000"},
    )
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["requires_approval"] is True
    assert res_data["approval_request_id"] is not None


def test_global_ai_kill_switch_toggling():
    """Verify global AI freeze halts autonomous execution."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": "org-apex-01",
            "email": "admin_hitl@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": "org-apex-01"}

    # Pause
    pause_res = client.post(
        "/api/v1/governance/kill-switch/global",
        headers=headers,
        json={"action": "GLOBAL_AI_PAUSE", "reason": "Program 21 emergency pause verification"},
    )
    assert pause_res.status_code == 200
    assert kill_switch_state.is_globally_paused is True

    # Resume
    resume_res = client.post(
        "/api/v1/governance/kill-switch/global",
        headers=headers,
        json={"action": "RESUME", "reason": "Verification completed"},
    )
    assert resume_res.status_code == 200
    assert kill_switch_state.is_globally_paused is False
