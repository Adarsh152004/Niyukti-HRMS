"""Tests — WorkflowEngine CommandBus integration and AI Agent non-bypass invariant."""

import pytest

from backend.commands.application.bus import CommandBus
from backend.commands.application.handlers import CreateEmployeeCommandHandler, TerminateEmployeeCommandHandler
from backend.commands.domain.enums import RiskLevel
from backend.commands.domain.models import CommandMetadata
from backend.hrms.domain.actor import Actor, ActorType
from backend.workflows.application.step_executor import StepExecutor
from backend.workflows.application.workflow_engine import WorkflowEngine
from backend.workflows.domain.enums import WorkflowStatus
from backend.workflows.domain.models import WorkflowDefinition, WorkflowExecution, WorkflowStepDefinition


@pytest.mark.asyncio
async def test_workflow_executes_steps_via_command_bus():
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

    engine = WorkflowEngine(step_executor=StepExecutor(command_bus=bus))

    step1 = WorkflowStepDefinition(
        step_id="s1",
        workflow_id="wf1",
        name="Create Emp",
        command_type="employee.create",
        command_payload={"first_name": "WF_User", "last_name": "Test"},
    )
    wf_def = WorkflowDefinition(
        organization_id="org-acme",
        name="WF Command Test",
        steps=[step1],
    )
    execution = WorkflowExecution(
        workflow_id=wf_def.workflow_id,
        organization_id="org-acme",
    )

    actor = Actor(
        actor_id="usr-1",
        actor_type=ActorType.HUMAN,
        organization_id="org-acme",
        permissions={"EMPLOYEE_CREATE"},
    )

    res = await engine.execute_workflow(wf_def, execution, actor)
    assert res.status == WorkflowStatus.COMPLETED
    assert res.output_payload["first_name"] == "WF_User"


@pytest.mark.asyncio
async def test_ai_agent_cannot_bypass_command_bus_unauthorized_step_failed():
    """CRITICAL INVARIANT TEST: AI Agent executing unauthorized step via WorkflowEngine MUST fail at CommandBus."""
    bus = CommandBus()
    bus.registry.register(
        "employee.terminate",
        TerminateEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.terminate",
            description="Terminate employee",
            required_permissions=["EMPLOYEE_DELETE"],
            risk_level=RiskLevel.HIGH,
        ),
    )

    engine = WorkflowEngine(step_executor=StepExecutor(command_bus=bus))

    step_term = WorkflowStepDefinition(
        step_id="st1",
        workflow_id="wf1",
        name="Terminate Emp",
        command_type="employee.terminate",
        command_payload={"employee_id": "emp-999"},
    )
    wf_def = WorkflowDefinition(
        organization_id="org-acme",
        name="Agent Terminate WF",
        steps=[step_term],
    )
    execution = WorkflowExecution(
        workflow_id=wf_def.workflow_id,
        organization_id="org-acme",
    )

    # AI Agent without EMPLOYEE_DELETE permission
    agent_actor = Actor(
        actor_id="agent-scout-01",
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
        permissions=set(),
    )

    res = await engine.execute_workflow(wf_def, execution, agent_actor)

    # CommandBus authorization failure MUST fail the workflow step execution!
    assert res.status == WorkflowStatus.FAILED
    assert "unauthorized" in (res.failure_reason or "").lower()
