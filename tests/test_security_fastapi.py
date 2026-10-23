"""Tests — FastAPI Security dependencies, Tenant binding guards, and endpoints."""

from fastapi.testclient import TestClient

from backend.app import app
from backend.hrms.domain.actor import ActorType
from backend.security.application.jwt import JWTService

client = TestClient(app)


def test_auth_me_endpoint_with_valid_jwt():
    jwt_svc = JWTService()
    tok = jwt_svc.create_access_token(
        subject="usr-001",
        actor_id="actor-001",
        organization_id="org-acme",
        actor_type=ActorType.HUMAN,
        roles={"EMPLOYEE"},
        permissions={"EMPLOYEE_READ"},
    )

    headers = {"Authorization": f"Bearer {tok}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["actor_id"] == "actor-001"
    assert res["data"]["organization_id"] == "org-acme"


def test_tenant_mismatch_header_rejected():
    jwt_svc = JWTService()
    tok = jwt_svc.create_access_token(
        subject="usr-001",
        actor_id="actor-001",
        organization_id="org-acme",
        actor_type=ActorType.HUMAN,
        permissions={"EMPLOYEE_READ"},
    )

    # Sending header for a different tenant org-other must be rejected with 403!
    headers = {
        "Authorization": f"Bearer {tok}",
        "X-Tenant-ID": "org-other",
    }
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 403
    res = response.json()
    assert "Tenant mismatch" in res["detail"]
