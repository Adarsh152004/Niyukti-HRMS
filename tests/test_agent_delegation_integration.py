"""Tests — End-to-End Multi-Agent Delegation & Integration."""

from datetime import UTC, datetime, timedelta

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.delegation.application.delegation_executor import DelegationExecutor
from backend.agents.delegation.application.delegation_service import DelegationService
from backend.agents.domain.models import AgentCapability
from backend.agents.tools.application.tool_registry import ToolRegistry
from backend.agents.tools.infrastructure.builtin_tools import register_builtin_tools
from backend.commands.application.bus import CommandBus
from backend.commands.application.handlers import GetEmployeeCommandHandler
from backend.commands.domain.enums import RiskLevel
from backend.commands.domain.models import CommandMetadata


@pytest.mark.asyncio
async def test_end_to_end_delegated_task_execution():
    bus = CommandBus()
    bus.registry.register(
        "employee.read",
        GetEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.read",
            description="Read employee",
            required_permissions=["EMPLOYEE_READ"],
            risk_level=RiskLevel.LOW,
        ),
    )

    tool_reg = ToolRegistry()
    register_builtin_tools(tool_reg)

    agent_svc = AgentService()
    del_svc = DelegationService(agent_service=agent_svc)
    executor = DelegationExecutor(delegation_service=del_svc, agent_service=agent_svc)

    cap_read = AgentCapability(capability_id="c1", name="Read Emp", resource="employee", actions=["read"])

    sup = await agent_svc.create_agent(
        organization_id="org-acme",
        name="sup-e2e",
        display_name="Supervisor E2E",
        actor_id="act-sup-e2e",
        capabilities=[cap_read],
    )
    await agent_svc.activate_agent("org-acme", sup.agent_id)

    wrk = await agent_svc.create_agent(
        organization_id="org-acme",
        name="wrk-e2e",
        display_name="Worker E2E",
        actor_id="act-wrk-e2e",
        capabilities=[],
    )
    await agent_svc.activate_agent("org-acme", wrk.agent_id)

    expires_at = datetime.now(tz=UTC) + timedelta(hours=2)

    delegation = await del_svc.create_delegation(
        organization_id="org-acme",
        delegator_agent_id=sup.agent_id,
        delegate_agent_id=wrk.agent_id,
        parent_task_id="task-root-99",
        requested_capabilities=[cap_read],
        expires_at=expires_at,
    )

    task = await executor.execute_delegated_task(
        organization_id="org-acme",
        delegation_id=delegation.delegation_id,
        goal="Fetch employee profile for emp-100",
    )

    assert task.status == "COMPLETED"
    assert task.delegate_agent_id == wrk.agent_id
    assert task.delegator_agent_id == sup.agent_id
