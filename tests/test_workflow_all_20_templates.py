"""
Tests for all 20 Autonomous HR Workflow Templates in WorkflowTemplateCatalog.
"""

from __future__ import annotations

from backend.workflows.domain.definitions import get_execution_order, validate_workflow_definition
from backend.workflows.templates.catalog import WorkflowTemplateCatalog


def test_catalog_contains_all_20_templates():
    catalog = WorkflowTemplateCatalog.get_instance()
    names = catalog.list_template_names()

    assert len(names) == 20
    expected_templates = [
        "onboarding",
        "offboarding",
        "recruitment_to_hire",
        "payroll_processing",
        "performance_review_cycle",
        "leave_approval",
        "promotion",
        "disciplinary",
        "probation_confirmation",
        "training_plan",
        "internal_transfer",
        "salary_revision",
        "document_verification",
        "attendance_regularization",
        "bonus_distribution",
        "health_and_safety",
        "contract_renewal",
        "certification_tracking",
        "employee_survey",
        "exit_interview",
    ]
    for tpl in expected_templates:
        assert tpl in names


def test_all_20_workflow_templates_are_valid_dags():
    catalog = WorkflowTemplateCatalog.get_instance()
    org_id = "org-test-wf-dags"

    for name in catalog.list_template_names():
        wf_def = catalog.get_workflow(name, org_id)

        # 1. Structural validation
        validate_workflow_definition(wf_def)
        assert wf_def.workflow_id is not None
        assert len(wf_def.steps) >= 3

        # 2. Topological execution order resolution
        order = get_execution_order(wf_def)
        total_steps = sum(len(lvl) for lvl in order)
        assert total_steps == len(wf_def.steps)
