"""
Agent SLA Contracts — Measurable operational boundaries for autonomous execution.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AgentSLAContract(BaseModel):
    """Formal operating SLA parameters for a production agent."""

    agent_id: str
    organization_id: str
    max_execution_time_seconds: int = Field(default=300, description="Max task wall-clock duration")
    max_cost_per_task_usd: float = Field(default=0.50, description="Max USD token spend per task")
    max_retries: int = Field(default=3, description="Max automated retry attempts")
    max_tool_calls_per_task: int = Field(default=20, description="Max tool executions per task")
    max_delegation_depth: int = Field(default=3, description="Max delegation hierarchy levels")
    min_evaluation_score: float = Field(default=0.75, description="Min acceptable trajectory score")
    max_policy_violations_before_quarantine: int = Field(default=2)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class SLAEvaluationResult(BaseModel):
    """Result of validating task execution metrics against agent SLA."""

    sla_passed: bool
    violations: list[str] = Field(default_factory=list)
    execution_time_seconds: float
    cost_usd: float
    tool_calls_count: int
    delegation_depth: int


class SLAManager:
    """Evaluates agent execution metrics against SLA contracts."""

    _instance: SLAManager | None = None

    def __init__(self) -> None:
        self._slas: dict[str, AgentSLAContract] = {}

    @classmethod
    def get_instance(cls) -> SLAManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_sla(self, sla: AgentSLAContract) -> None:
        """Register or update SLA contract for an agent."""
        key = f"{sla.organization_id}:{sla.agent_id}"
        self._slas[key] = sla
        logger.info(f"Registered SLA contract for agent [{key}]")

    def get_sla(self, organization_id: str, agent_id: str) -> AgentSLAContract:
        """Get SLA contract or return default standard SLA."""
        key = f"{organization_id}:{agent_id}"
        return self._slas.get(key) or AgentSLAContract(agent_id=agent_id, organization_id=organization_id)

    def evaluate_task_sla(
        self,
        organization_id: str,
        agent_id: str,
        duration_seconds: float,
        cost_usd: float,
        tool_calls: int,
        delegation_depth: int,
    ) -> SLAEvaluationResult:
        """Evaluate task metrics against SLA contract."""
        sla = self.get_sla(organization_id, agent_id)
        violations: list[str] = []

        if duration_seconds > sla.max_execution_time_seconds:
            violations.append(f"Execution duration {duration_seconds}s exceeded max limit {sla.max_execution_time_seconds}s")
        if cost_usd > sla.max_cost_per_task_usd:
            violations.append(f"Task token cost ${cost_usd:.4f} exceeded limit ${sla.max_cost_per_task_usd:.4f}")
        if tool_calls > sla.max_tool_calls_per_task:
            violations.append(f"Tool call count {tool_calls} exceeded limit {sla.max_tool_calls_per_task}")
        if delegation_depth > sla.max_delegation_depth:
            violations.append(f"Delegation depth {delegation_depth} exceeded limit {sla.max_delegation_depth}")

        return SLAEvaluationResult(
            sla_passed=len(violations) == 0,
            violations=violations,
            execution_time_seconds=duration_seconds,
            cost_usd=cost_usd,
            tool_calls_count=tool_calls,
            delegation_depth=delegation_depth,
        )
