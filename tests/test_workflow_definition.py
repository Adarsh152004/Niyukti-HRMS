"""Tests — WorkflowDefinition validation, duplicate step IDs, and cycle detection."""

import pytest

from backend.workflows.domain.definitions import get_execution_order, validate_workflow_definition
from backend.workflows.domain.exceptions import WorkflowValidationError
from backend.workflows.domain.models import WorkflowDefinition, WorkflowStepDefinition


def test_workflow_definition_validation_success():
    step1 = WorkflowStepDefinition(
        step_id="step1",
        workflow_id="wf1",
        name="Step 1",
        command_type="employee.create",
    )
    step2 = WorkflowStepDefinition(
        step_id="step2",
        workflow_id="wf1",
        name="Step 2",
        command_type="skill.create",
        dependencies=["step1"],
    )

    wf = WorkflowDefinition(
        organization_id="org-acme",
        name="Onboarding",
        steps=[step1, step2],
    )

    validate_workflow_definition(wf)
    order = get_execution_order(wf)
    assert len(order) == 2
    assert order[0][0].step_id == "step1"
    assert order[1][0].step_id == "step2"


def test_duplicate_step_id_rejected():
    step1 = WorkflowStepDefinition(step_id="step1", workflow_id="wf1", name="Step 1", command_type="employee.create")
    step1_dup = WorkflowStepDefinition(step_id="step1", workflow_id="wf1", name="Step Dup", command_type="employee.update")

    wf = WorkflowDefinition(organization_id="org-acme", name="DupTest", steps=[step1, step1_dup])
    with pytest.raises(WorkflowValidationError, match="Duplicate step ID"):
        validate_workflow_definition(wf)


def test_circular_dependency_rejected():
    step1 = WorkflowStepDefinition(
        step_id="step1", workflow_id="wf1", name="Step 1", command_type="employee.create", dependencies=["step2"]
    )
    step2 = WorkflowStepDefinition(
        step_id="step2", workflow_id="wf1", name="Step 2", command_type="skill.create", dependencies=["step1"]
    )

    wf = WorkflowDefinition(organization_id="org-acme", name="CycleTest", steps=[step1, step2])
    with pytest.raises(WorkflowValidationError, match="Circular dependency"):
        validate_workflow_definition(wf)
