"""
Governance Repository Port — Abstract interface for Governance, Safety, Audit, Metrics, Anomalies, and Containment storage.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
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


class GovernanceRepositoryPort(ABC):
    """Abstract interface for governance control plane storage."""

    @abstractmethod
    async def save_policy(self, policy: AgentGovernancePolicy) -> AgentGovernancePolicy:
        """Save or update governance policy."""
        pass

    @abstractmethod
    async def get_policy(self, organization_id: str, agent_id: str) -> AgentGovernancePolicy | None:
        """Retrieve policy for agent."""
        pass

    @abstractmethod
    async def save_budget(self, budget: AgentBudget) -> AgentBudget:
        """Save or update agent budget."""
        pass

    @abstractmethod
    async def get_budget(self, organization_id: str, agent_id: str) -> AgentBudget | None:
        """Retrieve budget for agent."""
        pass

    @abstractmethod
    async def append_ledger_entry(self, entry: ExecutionLedgerEntry) -> ExecutionLedgerEntry:
        """Append immutable execution ledger record."""
        pass

    @abstractmethod
    async def list_ledger_entries(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str | None = None,
    ) -> Sequence[ExecutionLedgerEntry]:
        """List ledger entries for agent/task."""
        pass

    @abstractmethod
    async def save_violation(self, violation: GovernanceViolation) -> GovernanceViolation:
        """Record governance violation."""
        pass

    @abstractmethod
    async def list_violations(self, organization_id: str, agent_id: str) -> Sequence[GovernanceViolation]:
        """List violations for agent."""
        pass

    @abstractmethod
    async def save_evaluation(self, evaluation: AgentEvaluation) -> AgentEvaluation:
        """Save agent evaluation record."""
        pass

    @abstractmethod
    async def list_evaluations(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str | None = None,
    ) -> Sequence[AgentEvaluation]:
        """List evaluations for agent."""
        pass

    @abstractmethod
    async def save_audit_record(self, record: AgentAuditRecord) -> AgentAuditRecord:
        """Save immutable governance audit record."""
        pass

    @abstractmethod
    async def list_audit_records(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str | None = None,
    ) -> Sequence[AgentAuditRecord]:
        """List audit records for agent/tenant."""
        pass

    @abstractmethod
    async def save_metric(self, metric: AgentMetric) -> AgentMetric:
        """Save operational metric."""
        pass

    @abstractmethod
    async def list_metrics(
        self,
        organization_id: str,
        agent_id: str | None = None,
        metric_name: str | None = None,
    ) -> Sequence[AgentMetric]:
        """List metrics for tenant/agent."""
        pass

    @abstractmethod
    async def save_anomaly(self, anomaly: AgentAnomaly) -> AgentAnomaly:
        """Save detected anomaly."""
        pass

    @abstractmethod
    async def list_anomalies(
        self,
        organization_id: str,
        agent_id: str,
        status: str | None = None,
    ) -> Sequence[AgentAnomaly]:
        """List anomalies for agent."""
        pass

    @abstractmethod
    async def get_anomaly(self, organization_id: str, anomaly_id: str) -> AgentAnomaly | None:
        """Retrieve anomaly by ID."""
        pass

    @abstractmethod
    async def save_containment_action(self, action: ContainmentAction) -> ContainmentAction:
        """Record containment action."""
        pass

    @abstractmethod
    async def list_containment_actions(
        self,
        organization_id: str,
        agent_id: str,
    ) -> Sequence[ContainmentAction]:
        """List containment actions for agent."""
        pass
