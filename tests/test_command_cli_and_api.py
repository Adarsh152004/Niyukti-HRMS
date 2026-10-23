"""Tests — FastAPI Command & Approval endpoints, and CLI interface."""

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.commands.cli.cli import PlatformCLI
from backend.hrms.domain.actor import Actor, ActorType
from backend.security.application.jwt import JWTService

client = TestClient(app)
jwt_svc = JWTService()


def test_command_discovery_api():
    tok = jwt_svc.create_access_token(
        subject="usr-001",
        actor_id="actor-001",
        organization_id="org-acme",
        actor_type=ActorType.HUMAN,
        permissions={"EMPLOYEE_CREATE"},
    )
    headers = {"Authorization": f"Bearer {tok}"}

    response = client.get("/api/v1/commands/discovery", headers=headers)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert len(res["data"]["commands"]) > 0


def test_submit_command_api_success():
    tok = jwt_svc.create_access_token(
        subject="usr-001",
        actor_id="actor-001",
        organization_id="org-acme",
        actor_type=ActorType.HUMAN,
        permissions={"EMPLOYEE_CREATE"},
    )
    headers = {"Authorization": f"Bearer {tok}"}

    payload = {
        "command_type": "employee.create",
        "payload": {"first_name": "API_User", "last_name": "Test"},
    }
    response = client.post("/api/v1/commands", json=payload, headers=headers)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["status"] == "SUCCEEDED"


@pytest.mark.asyncio
async def test_cli_execute_command():
    cli = PlatformCLI()

    actor = Actor(
        actor_id="cli-user-1",
        actor_type=ActorType.HUMAN,
        organization_id="org-acme",
        permissions={"EMPLOYEE_CREATE"},
    )

    res = await cli.execute_command(
        command_type="employee.create",
        payload={"first_name": "CLI_User"},
        actor=actor,
    )
    assert res.status.value == "SUCCEEDED"
    assert res.result_data["first_name"] == "CLI_User"
