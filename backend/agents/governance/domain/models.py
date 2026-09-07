"""
Governance Domain Models — Entities for GovernancePolicy, AgentBudget, ExecutionLedgerEntry, GovernanceViolation, AgentEvaluation, AgentAuditRecord, AgentMetric, AgentAnomaly, and ContainmentAction.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.governance.domain.enums import (
    AnomalyType,
    ContainmentActionType,
    EvaluationStatus,
    EvaluationType,
    GovernanceState,
    LedgerEventType,
    Severity,
    ViolationType,
)


def generate_gov_id(prefix: str = "gov") -> str:
    """Generate prefixed random UUID for governance entities."""
    return f"{prefix}-{uuid.uuid4()}"


class AgentGovernancePolicy(BaseModel):
    """
    Operating policy parameters governing an AI Agent's autonomous execution bounds.
    """

    policy_id: str = Field(default_factory=lambda: generate_gov_id("pol"))
    organization_id: str = Field(description="Tenant isolation boundary")
    agent_id: str
    name: str = Field(default="Default Governance Policy")
    description: str = Field(default="Standard operational policy")
    enabled: bool = Field(default=True)
    priority: int = Field(default=100)
    governance_state: GovernanceState = Field(default=GovernanceState.ACTIVE)
    max_reasoning_steps_per_task: int = Field(default=10)
    max_tool_calls_per_task: int = Field(default=20)
    max_delegation_depth: int = Field(default=3)
    max_concurrent_tasks: int = Field(default=5)
    allowed_tool_categories: list[str] = Field(default_factory=list)
    prohibited_tool_categories: list[str] = Field(default_factory=list)
    rules: dict[str, Any] = Field(default_factory=dict)
    auto_quarantine_on_violation: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class AgentBudget(BaseModel):
    """
    Resource consumption limits and quotas allocated to an AI Agent.
    """

    budget_id: str = Field(default_factory=lambda: generate_gov_id("bdg"))
    organization_id: str
    agent_id: str
    max_token_budget: int = Field(default=100000)
    tokens_consumed: int = Field(default=0)
    max_reasoning_runs: int = Field(default=500)
    reasoning_runs_count: int = Field(default=0)
    max_tool_calls: int = Field(default=1000)
    tool_calls_count: int = Field(default=0)
    max_command_executions: int = Field(default=500)
    command_executions_count: int = Field(default=0)
    max_delegated_tasks: int = Field(default=50)
    delegated_tasks_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    def is_exhausted(self) -> bool:
        """Check if any allocated budget quota is exceeded."""
        return (
            self.tokens_consumed >= self.max_token_budget
            or self.reasoning_runs_count >= self.max_reasoning_runs
            or self.tool_calls_count >= self.max_tool_calls
            or self.command_executions_count >= self.max_command_executions
            or self.delegated_tasks_count >= self.max_delegated_tasks
        )


class UsageCounter(BaseModel):
    """
    Real-time task-scoped usage counters.
    """

    agent_id: str
    task_id: str
    reasoning_steps: int = Field(default=0)
    tool_calls: int = Field(default=0)
    command_executions: int = Field(default=0)
    estimated_tokens: int = Field(default=0)


class ExecutionLedgerEntry(BaseModel):
    """
    Immutable structured record of an agent's execution trajectory.
    """

    ledger_id: str = Field(default_factory=lambda: generate_gov_id("ledger"))
    organization_id: str
    agent_id: str
    actor_id: str
    task_id: str
    event_type: LedgerEventType
    action: str
    resource: str
    risk_level: str = Field(default="LOW")
    decision: str = Field(default="ALLOWED")
    policy_result: str = Field(default="SUCCESS")
    authorization_result: str = Field(default="AUTHORIZED")
    approval_result: str | None = Field(default=None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    duration_ms: int = Field(default=0)
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4()}")
    causation_id: str | None = Field(default=None)
    failure_reason: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GovernanceViolation(BaseModel):
    """
    Audit record of a governance policy violation.
    """

    violation_id: str = Field(default_factory=lambda: generate_gov_id("viol"))
    organization_id: str
    agent_id: str
    task_id: str | None = Field(default=None)
    violation_type: ViolationType
    details: str
    severity: str = Field(default="HIGH")
    action_taken: str = Field(default="LOGGED")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentEvaluation(BaseModel):
    """
    Evaluation record assessing an agent's task execution trajectory.
    """

    evaluation_id: str = Field(default_factory=lambda: generate_gov_id("eval"))
    organization_id: str
    agent_id: str
    task_id: str
    reasoning_run_id: str | None = Field(default=None)
    evaluation_type: EvaluationType = Field(default=EvaluationType.OVERALL)
    score: float = Field(default=1.0, ge=0.0, le=1.0)
    status: EvaluationStatus = Field(default=EvaluationStatus.PASSED)
    findings: list[str] = Field(default_factory=list)
    policy_violations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    @property
    def passed(self) -> bool:
        """Returns True if the evaluation status is PASSED."""
        return self.status == EvaluationStatus.PASSED


class AgentAuditRecord(BaseModel):
    """
    Immutable governance audit record tracking all autonomous actions and governance decisions.
    """

    audit_id: str = Field(default_factory=lambda: generate_gov_id("audit"))
    organization_id: str
    agent_id: str
    task_id: str | None = Field(default=None)
    execution_id: str | None = Field(default=None)
    event_type: str
    action: str
    resource: str
    tool_name: str | None = Field(default=None)
    command_name: str | None = Field(default=None)
    risk_level: str = Field(default="LOW")
    policy_result: str = Field(default="SUCCESS")
    authorization_result: str = Field(default="AUTHORIZED")
    approval_required: bool = Field(default=False)
    approval_status: str | None = Field(default=None)
    actor_id: str
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4()}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentMetric(BaseModel):
    """
    Operational metric data point recorded for governance observability.
    """

    metric_id: str = Field(default_factory=lambda: generate_gov_id("met"))
    organization_id: str
    agent_id: str | None = Field(default=None)
    metric_name: str
    metric_value: float
    dimensions: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class AgentAnomaly(BaseModel):
    """
    Detected suspicious behavior or boundary anomaly.
    """

    anomaly_id: str = Field(default_factory=lambda: generate_gov_id("anom"))
    organization_id: str
    agent_id: str
    task_id: str | None = Field(default=None)
    anomaly_type: AnomalyType
    severity: Severity = Field(default=Severity.MEDIUM)
    score: float = Field(default=0.8)
    evidence: dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="OPEN")
    detected_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    resolved_at: datetime | None = Field(default=None)


class ContainmentAction(BaseModel):
    """
    Record of emergency containment action performed on an agent.
    """

    containment_id: str = Field(default_factory=lambda: generate_gov_id("cnt"))
    organization_id: str
    agent_id: str
    action: ContainmentActionType
    reason: str
    triggered_by: str = Field(default="CONTAINMENT_SERVICE")
    previous_status: str
    resulting_status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
