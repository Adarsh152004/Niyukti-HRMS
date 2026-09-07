"""
AI-Powered Intelligent HRMS — Program 22 Multi-Tenant Isolation Test Suite.

Verifies:
1. Strict cross-tenant data isolation
2. Header vs token mismatch rejection (403 Forbidden)
"""

import pytest
from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_cross_tenant_isolation_boundary():
    """Verify Tenant A token cannot access Tenant B resources with tenant header mismatch."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": "org-apex-01",
            "email": "admin_p22@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    token = login_res.json()["data"]["access_token"]

    # Header mismatch: Token says org-apex-01, Header claims org-beta-02
    mismatch_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": "org-beta-02"},
    )
    assert mismatch_res.status_code == 403
