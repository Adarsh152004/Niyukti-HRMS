"""
Tests for Human-In-The-Loop (HITL) Workflow Pausing and Token-Based Resumption.
"""

from __future__ import annotations

from backend.hrms.domain.actor import Actor, ActorType
from backend.workflows.application.hitl_resumption import HITLWorkflowResumptionService
from backend.workflows.domain.enums import WorkflowStatus
from backend.workflows.domain.models import WorkflowExecution
from backend.workflows.templates.catalog import WorkflowTemplateCatalog


def test_hitl_workflow_suspension_and_resumption():
    resumption_svc = HITLWorkflowResumptionService.get_instance()
    catalog = WorkflowTemplateCatalog.get_instance()
    wf_def = catalog.get_workflow("promotion")

    execution = WorkflowExecution(
        workflow_id=wf_def.workflow_id,
        organization_id="org-hitl-test",
        status=WorkflowStatus.RUNNING,
    )

    # 1. Suspend at executive approval step
    token = resumption_svc.suspend_workflow_step(
        workflow_def=wf_def,
        execution=execution,
        step_id="step_executive_signoff",
        approval_id="appr-prom-101",
    )
    assert token.startswith("hitl_token_")

    # 2. Approver reviews and grants approval
    approver = Actor(actor_id="ceo-01", actor_type=ActorType.HUMAN, organization_id="org-hitl-test", roles=["CEO"])
    res = resumption_svc.resume_workflow(token, approved=True, approver_actor=approver)

    assert res is not None
    assert res["status"] == "RESUMED"
    assert res["approved"] is True
    assert res["step_id"] == "step_executive_signoff"
