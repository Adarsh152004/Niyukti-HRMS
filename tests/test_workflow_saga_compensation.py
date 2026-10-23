"""
Tests for Saga Pattern Rollback & Inverse Compensation Handlers.
"""

from __future__ import annotations

import pytest

from backend.workflows.domain.enums import StepStatus, WorkflowStatus
from backend.workflows.domain.models import StepExecution, WorkflowExecution
from backend.workflows.saga.compensation_registry import CompensationRegistry
from backend.workflows.saga.saga_coordinator import SagaCoordinator


@pytest.mark.asyncio
async def test_saga_compensation_executes_in_reverse_order():
    coordinator = SagaCoordinator.get_instance()
    reg = CompensationRegistry.get_instance()

    reg.register_compensation("employee.create", "employee.terminate")
    reg.register_compensation("it.provision_account", "it.revoke_account")
    reg.register_compensation("asset.assign_laptop", "asset.unassign_laptop")

    execution = WorkflowExecution(
        workflow_id="wf-test-saga",
        organization_id="org-saga-test",
        status=WorkflowStatus.FAILED,
    )

    completed_steps = [
        StepExecution(
            execution_id=execution.execution_id,
            step_id="step_create_profile",
            command_type="employee.create",
            status=StepStatus.SUCCEEDED,
            output_payload={"employee_id": "emp-101"},
        ),
        StepExecution(
            execution_id=execution.execution_id,
            step_id="step_provision_it",
            command_type="it.provision_account",
            status=StepStatus.SUCCEEDED,
            output_payload={"email": "emp101@acme.com"},
        ),
        StepExecution(
            execution_id=execution.execution_id,
            step_id="step_assign_asset",
            command_type="asset.assign_laptop",
            status=StepStatus.SUCCEEDED,
            output_payload={"serial": "SN-9988"},
        ),
    ]

    # Execute rollback
    logs = await coordinator.compensate_failed_workflow(execution, completed_steps)

    assert len(logs) == 3
    # Invariant: Reverse execution order (Step 3 -> Step 2 -> Step 1)
    assert logs[0].step_id == "step_assign_asset"
    assert logs[0].compensating_command_type == "asset.unassign_laptop"
    assert logs[1].step_id == "step_provision_it"
    assert logs[1].compensating_command_type == "it.revoke_account"
    assert logs[2].step_id == "step_create_profile"
    assert logs[2].compensating_command_type == "employee.terminate"
