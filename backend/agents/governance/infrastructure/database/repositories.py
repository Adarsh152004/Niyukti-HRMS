"""
Governance Repositories — In-Memory & Database repository implementations.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from backend.agents.governance.domain.models import (
    AgentAnomaly,
    AgentAuditRecord,
    AgentBudget,
    AgentEvaluation,
    AgentGovernancePolicy,
    AgentMetric,
    ContainmentAction,
    ExecutionLedgerEntry,
    GovernanceViolation,
)
from backend.agents.governance.ports.repositories import GovernanceRepositoryPort

logger = logging.getLogger(__name__)


class InMemoryGovernanceRepository(GovernanceRepositoryPort):
    """In-memory repository for governance entities."""

    def __init__(self) -> None:
        self._policies: dict[str, AgentGovernancePolicy] = {}
        self._budgets: dict[str, AgentBudget] = {}
        self._ledger: list[ExecutionLedgerEntry] = []
        self._violations: list[GovernanceViolation] = []
        self._evaluations: list[AgentEvaluation] = []
        self._audit_records: list[AgentAuditRecord] = []
        self._metrics: list[AgentMetric] = []
        self._anomalies: dict[str, AgentAnomaly] = {}
        self._containments: list[ContainmentAction] = []

    async def save_policy(self, policy: AgentGovernancePolicy) -> AgentGovernancePolicy:
        key = f"{policy.organization_id}:{policy.agent_id}"
        self._policies[key] = policy
        return policy

    async def get_policy(self, organization_id: str, agent_id: str) -> AgentGovernancePolicy | None:
        key = f"{organization_id}:{agent_id}"
        return self._policies.get(key)

    async def save_budget(self, budget: AgentBudget) -> AgentBudget:
        key = f"{budget.organization_id}:{budget.agent_id}"
        self._budgets[key] = budget
        return budget

    async def get_budget(self, organization_id: str, agent_id: str) -> AgentBudget | None:
        key = f"{organization_id}:{agent_id}"
        return self._budgets.get(key)

    async def append_ledger_entry(self, entry: ExecutionLedgerEntry) -> ExecutionLedgerEntry:
        self._ledger.append(entry)
        return entry

    async def list_ledger_entries(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str | None = None,
    ) -> Sequence[ExecutionLedgerEntry]:
        results: list[ExecutionLedgerEntry] = []
        for entry in self._ledger:
            if entry.organization_id != organization_id or entry.agent_id != agent_id:
                continue
            if task_id and entry.task_id != task_id:
                continue
            results.append(entry)
        return results

    async def save_violation(self, violation: GovernanceViolation) -> GovernanceViolation:
        self._violations.append(violation)
        return violation

    async def list_violations(self, organization_id: str, agent_id: str) -> Sequence[GovernanceViolation]:
        return [v for v in self._violations if v.organization_id == organization_id and v.agent_id == agent_id]

    async def save_evaluation(self, evaluation: AgentEvaluation) -> AgentEvaluation:
        self._evaluations.append(evaluation)
        return evaluation

    async def list_evaluations(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str | None = None,
    ) -> Sequence[AgentEvaluation]:
        results: list[AgentEvaluation] = []
        for ev in self._evaluations:
            if ev.organization_id != organization_id or ev.agent_id != agent_id:
                continue
            if task_id and ev.task_id != task_id:
                continue
            results.append(ev)
        return results

    async def save_audit_record(self, record: AgentAuditRecord) -> AgentAuditRecord:
        self._audit_records.append(record)
        return record

    async def list_audit_records(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str | None = None,
    ) -> Sequence[AgentAuditRecord]:
        results: list[AgentAuditRecord] = []
        for rec in self._audit_records:
            if rec.organization_id != organization_id or rec.agent_id != agent_id:
                continue
            if task_id and rec.task_id != task_id:
                continue
            results.append(rec)
        return results

    async def save_metric(self, metric: AgentMetric) -> AgentMetric:
        self._metrics.append(metric)
        return metric

    async def list_metrics(
        self,
        organization_id: str,
        agent_id: str | None = None,
        metric_name: str | None = None,
    ) -> Sequence[AgentMetric]:
        results: list[AgentMetric] = []
        for m in self._metrics:
            if m.organization_id != organization_id:
                continue
            if agent_id and m.agent_id != agent_id:
                continue
            if metric_name and m.metric_name != metric_name:
                continue
            results.append(m)
        return results

    async def save_anomaly(self, anomaly: AgentAnomaly) -> AgentAnomaly:
        key = f"{anomaly.organization_id}:{anomaly.anomaly_id}"
        self._anomalies[key] = anomaly
        return anomaly

    async def list_anomalies(
        self,
        organization_id: str,
        agent_id: str,
        status: str | None = None,
    ) -> Sequence[AgentAnomaly]:
        results: list[AgentAnomaly] = []
        for a in self._anomalies.values():
            if a.organization_id != organization_id or a.agent_id != agent_id:
                continue
            if status and a.status != status:
                continue
            results.append(a)
        return results

    async def get_anomaly(self, organization_id: str, anomaly_id: str) -> AgentAnomaly | None:
        key = f"{organization_id}:{anomaly_id}"
        return self._anomalies.get(key)

    async def save_containment_action(self, action: ContainmentAction) -> ContainmentAction:
        self._containments.append(action)
        return action

    async def list_containment_actions(
        self,
        organization_id: str,
        agent_id: str,
    ) -> Sequence[ContainmentAction]:
        return [c for c in self._containments if c.organization_id == organization_id and c.agent_id == agent_id]
