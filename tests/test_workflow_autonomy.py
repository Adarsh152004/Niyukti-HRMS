"""Tests — Autonomy readiness end-to-end multi-step event-driven workflow with HITL approval gate."""

import pytest

from backend.commands.application.bus import CommandBus
from backend.commands.application.handlers import (
    CreateEmployeeCommandHandler,
    CreateSkillCommandHandler,
    TerminateEmployeeCommandHandler,
)
from backend.commands.domain.enums import RiskLevel
from backend.commands.domain.models import CommandMetadata
from backend.hrms.domain.actor import Actor, ActorType
from backend.runtime.events import Event
from backend.workflows.application.event_trigger_processor import EventTriggerProcessor
from backend.workflows.application.step_executor import StepExecutor
from backend.workflows.application.workflow_engine import WorkflowEngine
from backend.workflows.domain.enums import TriggerType, WorkflowStatus
from backend.workflows.domain.models import WorkflowDefinition, WorkflowStepDefinition
from backend.workflows.infrastructure.database.repositories import (
    InMemoryDeadLetterJobRepository,
    InMemoryStepExecutionRepository,
    InMemoryWorkflowDefinitionRepository,
    InMemoryWorkflowExecutionRepository,
)


@pytest.mark.asyncio
async def test_end_to_end_autonomous_event_driven_workflow_with_hitl():
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
        "skill.create",
        CreateSkillCommandHandler(),
        CommandMetadata(
            command_type="skill.create",
            description="Create skill",
            required_permissions=["EMPLOYEE_MANAGE_SKILLS"],
            risk_level=RiskLevel.LOW,
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

    # 2. Setup Repositories and WorkflowEngine
    wf_def_repo = InMemoryWorkflowDefinitionRepository()
    wf_exec_repo = InMemoryWorkflowExecutionRepository()
    step_exec_repo = InMemoryStepExecutionRepository()
    dlq_repo = InMemoryDeadLetterJobRepository()

    engine = WorkflowEngine(
        step_executor=StepExecutor(command_bus=bus),
        wf_def_repo=wf_def_repo,
        wf_exec_repo=wf_exec_repo,
        step_exec_repo=step_exec_repo,
        dlq_repo=dlq_repo,
    )

    # 3. Create Event-Triggered Workflow Definition
    s1 = WorkflowStepDefinition(
        step_id="s1",
        workflow_id="wf1",
        name="Create",
        command_type="employee.create",
        command_payload={"first_name": "Autonomy_Emp"},
    )
    s2 = WorkflowStepDefinition(
        step_id="s2",
        workflow_id="wf1",
        name="Skill",
        command_type="skill.create",
        command_payload={"name": "AI_Ops"},
        dependencies=["s1"],
    )
    s3 = WorkflowStepDefinition(
        step_id="s3",
        workflow_id="wf1",
        name="Terminate",
        command_type="employee.terminate",
        command_payload={"employee_id": "emp-001"},
        dependencies=["s2"],
    )

    wf_def = WorkflowDefinition(
        organization_id="org-acme",
        name="Employee Onboarding & Compliance Workflow",
        trigger_type=TriggerType.EVENT,
        trigger_config={"event_type": "employee.joined"},
        steps=[s1, s2, s3],
        enabled=True,
    )
    await wf_def_repo.save(wf_def)

    # 4. Trigger Workflow via EventTriggerProcessor
    processor = EventTriggerProcessor(
        wf_def_repo=wf_def_repo,
        wf_exec_repo=wf_exec_repo,
        workflow_engine=engine,
    )

    joined_event = Event(
        event_type="employee.joined",
        source="org-acme",
        payload={"organization_id": "org-acme", "candidate_id": "cand-99"},
        correlation_id="corr-onboard-100",
    )

    execution = await processor.handle_event(joined_event)
    assert execution is not None

    # Step 1 and Step 2 execute successfully via CommandBus, but Step 3 (HIGH risk) pauses in WAITING_APPROVAL
    assert execution.status == WorkflowStatus.WAITING_APPROVAL

    # 5. Verify Pending HITL Approval Request created in Node 5 ApprovalService
    pending_approvals = bus.approval_service.list_pending_for_organization("org-acme")
    assert len(pending_approvals) == 1
    appr_req = pending_approvals[0]

    # 6. CEO approves the HITL request
    ceo_actor = Actor(
        actor_id="ceo-actor-1",
        actor_type=ActorType.HUMAN,
        organization_id="org-acme",
        permissions={"EMPLOYEE_CREATE", "EMPLOYEE_MANAGE_SKILLS", "EMPLOYEE_DELETE"},
    )
    bus.approval_service.approve(appr_req.request_id, approver_actor=ceo_actor)

    # 7. Resume workflow execution
    execution.transition_to(WorkflowStatus.RUNNING)
    final_execution = await engine.execute_workflow(wf_def, execution, ceo_actor)

    # Workflow successfully completed!
    print("FINAL EXECUTION FAILURE REASON:", final_execution.failure_reason)
    assert final_execution.status == WorkflowStatus.COMPLETED
    assert final_execution.output_payload["first_name"] == "Autonomy_Emp"
