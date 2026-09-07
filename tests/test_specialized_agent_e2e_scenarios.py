"""
End-to-End Test Scenarios for Specialized AI HR Agents (Recruitment, Support, Attrition, Payroll).
"""

from __future__ import annotations

import pytest

from backend.agents.specialized.application.specialization_service import SpecializedAgentService
from backend.agents.specialized.domain.enums import SpecializedAgentRole, ToolAccessLevel
from backend.knowledge.domain.enums import AccessScopeType, KnowledgeClassification
from backend.ml.domain.enums import PredictionDecision
from backend.ml.domain.models import ModelVersion, PredictionRequest
from backend.ml.inference.prediction_service import PredictionService
from backend.ml.lineage.lineage_service import DecisionLineageService
from backend.ml.registry.model_registry import ModelRegistryService


@pytest.mark.asyncio
async def test_scenario_a_recruitment_pipeline():
    svc = SpecializedAgentService.get_instance()
    org_id = "org-e2e-recruitment"
    svc.bootstrap_tenant(org_id)

    # 1. Recruitment Agent verifies requisition creation tool
    assert svc.verify_tool_access(SpecializedAgentRole.RECRUITMENT_AGENT, "job.create") == ToolAccessLevel.ALLOW

    # 2. Resume Screening Agent parses untrusted candidate resume under DataFirewall
    assert svc.verify_tool_access(SpecializedAgentRole.RESUME_SCREENING_AGENT, "resume.parse") == ToolAccessLevel.ALLOW
    # Resume screening agent CANNOT hire candidate
    assert svc.get_tool_policy(SpecializedAgentRole.RESUME_SCREENING_AGENT).is_prohibited("candidate.hire")

    # 3. Candidate Ranking Agent ranks candidates
    assert svc.verify_tool_access(SpecializedAgentRole.CANDIDATE_RANKING_AGENT, "ml.predict_ranking") == ToolAccessLevel.ALLOW

    # 4. Interview Intelligence Agent creates interview guide
    assert (
        svc.verify_tool_access(SpecializedAgentRole.INTERVIEW_INTELLIGENCE_AGENT, "interview.get_plan") == ToolAccessLevel.ALLOW
    )

    # 5. Candidate rejection or hiring requires human manager approval
    assert svc.verify_tool_access(SpecializedAgentRole.RECRUITMENT_AGENT, "candidate.reject") == ToolAccessLevel.REQUIRES_APPROVAL


@pytest.mark.asyncio
async def test_scenario_b_employee_support_self_service():
    svc = SpecializedAgentService.get_instance()
    org_id = "org-e2e-support"
    svc.bootstrap_tenant(org_id)

    # 1. Employee assistant retrieves policy knowledge in authorized scope
    svc.verify_knowledge_access(
        role=SpecializedAgentRole.EMPLOYEE_ASSISTANT_AGENT,
        scope=AccessScopeType.ROLE_BASED,
        classification=KnowledgeClassification.INTERNAL,
    )

    # 2. Employee assistant checks own leave balance tool
    assert svc.verify_tool_access(SpecializedAgentRole.EMPLOYEE_ASSISTANT_AGENT, "leave.get_own_balance") == ToolAccessLevel.ALLOW

    # 3. Privacy Boundary: Prohibited from viewing other employee's salary
    assert svc.get_tool_policy(SpecializedAgentRole.EMPLOYEE_ASSISTANT_AGENT).is_prohibited("employee.view_other_salary")


@pytest.mark.asyncio
async def test_scenario_c_attrition_prediction_to_retention_flow():
    svc = SpecializedAgentService.get_instance()
    reg = ModelRegistryService.get_instance()
    pred_svc = PredictionService.get_instance()
    lin_svc = DecisionLineageService.get_instance()

    org_id = "org-e2e-attrition"
    svc.bootstrap_tenant(org_id)

    # 1. Register & activate predictive attrition model
    model = await reg.register_model(org_id, name="AttritionPredictorLiveE2E")
    v1 = ModelVersion(
        model_id=model.model_id,
        organization_id=org_id,
        version_number=1,
        algorithm="LogisticRegression",
        dataset_version_id="dsv-101",
        feature_set_version="1.0",
        storage_reference="ref",
    )
    await reg.store.save_version(v1)
    await reg.release_service.activate_model(org_id, model.model_id, v1.version_id, approved_by="hr-admin")

    # 2. Generate calibrated ML prediction
    req = PredictionRequest(
        organization_id=org_id,
        model_id=model.model_id,
        actor_id="attrition-agent",
        actor_roles=["AI_AGENT"],
        input_features={"employee_tenure_months": 36.0, "leave_frequency_90d": 4.0},
    )
    res = await pred_svc.predict(req)
    assert res.decision == PredictionDecision.PREDICT
    assert len(res.lineage_id) > 0

    # 3. Attrition Agent triggers Retention Agent workflow with Lineage
    assert svc.verify_tool_access(SpecializedAgentRole.ATTRITION_AGENT, "workflow.trigger_retention") == ToolAccessLevel.ALLOW

    # 4. Retention Agent designs intervention plan and records outcome feedback
    assert svc.verify_tool_access(SpecializedAgentRole.RETENTION_AGENT, "retention.create_plan") == ToolAccessLevel.ALLOW
    feedback = await lin_svc.record_outcome_feedback(
        organization_id=org_id,
        prediction_id=res.prediction_id,
        lineage_id=res.lineage_id,
        actual_outcome="RETENTION_INTERVENTION_COMPLETED",
        human_override=False,
    )
    assert feedback.actual_outcome == "RETENTION_INTERVENTION_COMPLETED"


@pytest.mark.asyncio
async def test_scenario_d_payroll_assistance_read_only():
    svc = SpecializedAgentService.get_instance()
    org_id = "org-e2e-payroll"
    svc.bootstrap_tenant(org_id)

    # 1. Payroll Assistant can read payslip and detect anomalies
    assert svc.verify_tool_access(SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT, "payroll.get_payslip") == ToolAccessLevel.ALLOW
    assert (
        svc.verify_tool_access(SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT, "payroll.detect_anomalies") == ToolAccessLevel.ALLOW
    )

    # 2. Invariant: Payroll calculations remain deterministic; assistant cannot execute runs or alter salary
    assert svc.get_tool_policy(SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT).is_prohibited("payroll.update_salary")
    assert svc.get_tool_policy(SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT).is_prohibited("payroll.execute_run")
