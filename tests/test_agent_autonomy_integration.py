"""Tests — End-to-end Autonomous Agent Integration with CommandBus and HITL Gate."""

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.application.command_gateway import AgentCommandGateway
from backend.agents.application.execution_context import AgentExecutionContextFactory
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import AgentType, TaskPriority
from backend.agents.domain.models import AgentCapability
from backend.commands.application.bus import CommandBus
from backend.commands.application.handlers import CreateEmployeeCommandHandler, TerminateEmployeeCommandHandler
from backend.commands.domain.enums import CommandStatus, RiskLevel
from backend.commands.domain.models import CommandMetadata
from backend.hrms.domain.actor import Actor, ActorType
from backend.runtime.events import EventBus


@pytest.mark.asyncio
async def test_end_to_end_autonomous_agent_flow_with_command_bus_and_hitl():
    # 1. Setup CommandBus and Handlers
    bus = CommandBus()
    bus.registry.register(
        "employee.create",
        CreateEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.create",
            description="Create employee",
            required_permissions=["EMPLOYEE_CREATE"],
            risk_level=RiskLevel.MEDIUM,
        ),
    )
    bus.registry.register(
        "employee.terminate",
        TerminateEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.terminate",
            description="Terminate employee",
            required_permissions=["EMPLOYEE_DELETE"],
            risk_level=RiskLevel.HIGH,
            requires_approval=True,
        ),
    )

    event_bus = EventBus.get_instance()
    agent_service = AgentService(event_bus=event_bus)
    task_service = AgentTaskService(event_bus=event_bus)
    gateway = AgentCommandGateway(command_bus=bus)

    # 2. Human creates and activates AI Agent with declared capabilities
    cap_create = AgentCapability(
        capability_id="cap-create",
        name="Create Emp",
        resource="employee",
        actions=["create"],
        risk_level="MEDIUM",
    )
    cap_term = AgentCapability(
        capability_id="cap-term",
        name="Terminate Emp",
        resource="employee",
        actions=["terminate"],
        risk_level="HIGH",
        requires_hitl=True,
    )

    agent = await agent_service.create_agent(
        organization_id="org-acme",
        name="onboarding-bot-01",
        display_name="Onboarding Assistant Bot",
        agent_type=AgentType.ONBOARDING_AGENT,
        capabilities=[cap_create, cap_term],
    )

    await agent_service.activate_agent("org-acme", agent.agent_id)

    # 3. Agent receives Task
    task = await task_service.create_task(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        goal="Onboard candidate John Doe",
        priority=TaskPriority.HIGH,
    )

    await task_service.start_task("org-acme", task.task_id)

    # 4. Agent Execution Context created
    agent_actor = Actor(
        actor_id=agent.actor_id,
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
        permissions={"EMPLOYEE_CREATE", "EMPLOYEE_DELETE"},
    )
    ctx = AgentExecutionContextFactory.create_context(agent, task, actor=agent_actor)

    # 5. Agent requests state mutation action via AgentCommandGateway
    cmd_res = await gateway.request_action(
        agent=agent,
        context=ctx,
        resource="employee",
        action="create",
        command_type="employee.create",
        payload={"first_name": "John", "last_name": "Doe"},
        actor=agent_actor,
    )

    assert cmd_res.status == CommandStatus.SUCCEEDED
    assert cmd_res.result_data["first_name"] == "John"

    # Complete initial task
    await task_service.complete_task("org-acme", task.task_id, output=cmd_res.result_data)

    # 6. High-risk action (employee.terminate) requesting HITL approval
    term_task = await task_service.create_task(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        goal="Offboard non-compliant employee",
    )
    await task_service.start_task("org-acme", term_task.task_id)

    term_ctx = AgentExecutionContextFactory.create_context(agent, term_task, actor=agent_actor)

    hitl_res = await gateway.request_action(
        agent=agent,
        context=term_ctx,
        resource="employee",
        action="terminate",
        command_type="employee.terminate",
        payload={"employee_id": "emp-101"},
        actor=agent_actor,
    )

    # High-risk action MUST pause in WAITING_APPROVAL!
    assert hitl_res.status == CommandStatus.WAITING_APPROVAL
    assert "approval_request_id" in hitl_res.result_data

    # Pending approval in Node 5 ApprovalService
    pending = bus.approval_service.list_pending_for_organization("org-acme")
    assert len(pending) == 1
