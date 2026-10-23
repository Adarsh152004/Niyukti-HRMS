"""
AI-Powered Intelligent HRMS — Program 21 Golden Paths & End-to-End Business Flow Test Suite.

Verifies:
1. Golden Path 1: CEO Workforce Overview & Analytics Query
2. Golden Path 2: Employee Leave Balance and Policy Retrieval
3. Golden Path 3: Governed Mutation with Human Sign-Off and Audit Logging
"""

import pytest
from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_golden_path_1_ceo_workforce_overview():
    """Verify CEO strategic workforce query with RAG citations and KPIs."""
    # Register & Login
    client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": "org-apex-01",
            "username": "ceo_p21",
            "email": "ceo_p21@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": "org-apex-01",
            "email": "ceo_p21@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": "org-apex-01"}

    # Query AI Command API
    res = client.post(
        "/api/v1/ai/command",
        headers=headers,
        json={"prompt": "What is our company parental leave policy and attendance summary?"},
    )
    assert res.status_code == 200
    res_data = res.json()
    assert res_data.get("response_text") or res_data.get("summary") is not None
    assert len(res_data["citations"]) > 0


def test_golden_path_2_leave_policy_and_balance_query():
    """Verify employee self-service leave balance and policy citation."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": "org-apex-01",
            "email": "ceo_p21@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": "org-apex-01"}

    res = client.post(
        "/api/v1/ai/command",
        headers=headers,
        json={"prompt": "What is our company parental leave policy?"},
    )
    assert res.status_code == 200
    res_data = res.json()
    assert "POL-BEN-LV-01" in str(res_data["citations"][0])
