"""Tests — Agent Governance Domain Models & Enums."""

from backend.agents.governance.domain.enums import (
    AnomalyType,
    ContainmentActionType,
    EvaluationStatus,
    EvaluationType,
    GovernanceState,
    Severity,
)
from backend.agents.governance.domain.models import (
    AgentAnomaly,
    AgentEvaluation,
    AgentGovernancePolicy,
    ContainmentAction,
)


def test_governance_domain_model_instantiations():
    policy = AgentGovernancePolicy(organization_id="org-1", agent_id="agent-1", name="Test Policy")
    assert policy.enabled is True
    assert policy.governance_state == GovernanceState.ACTIVE

    eval_obj = AgentEvaluation(
        organization_id="org-1",
        agent_id="agent-1",
        task_id="task-1",
        evaluation_type=EvaluationType.SAFETY,
        score=0.95,
        status=EvaluationStatus.PASSED,
    )
    assert eval_obj.score == 0.95
    assert eval_obj.status == EvaluationStatus.PASSED

    anomaly = AgentAnomaly(
        organization_id="org-1",
        agent_id="agent-1",
        anomaly_type=AnomalyType.EXCESSIVE_TOOL_USAGE,
        severity=Severity.HIGH,
    )
    assert anomaly.anomaly_type == AnomalyType.EXCESSIVE_TOOL_USAGE
    assert anomaly.severity == Severity.HIGH

    containment = ContainmentAction(
        organization_id="org-1",
        agent_id="agent-1",
        action=ContainmentActionType.PAUSE,
        reason="Test pause",
        triggered_by="human-admin",
        previous_status="ACTIVE",
        resulting_status="PAUSED",
    )
    assert containment.action == ContainmentActionType.PAUSE
    assert containment.resulting_status == "PAUSED"
