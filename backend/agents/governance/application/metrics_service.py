"""
Metrics Service — Tracks operational metrics and provides aggregation methods for governance observability.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from backend.agents.governance.domain.models import AgentMetric
from backend.agents.governance.infrastructure.database.repositories import InMemoryGovernanceRepository
from backend.agents.governance.ports.repositories import GovernanceRepositoryPort
from backend.runtime.events import Event, EventBus

logger = logging.getLogger(__name__)


class MetricsService:
    """
    Manages tenant and agent-scoped operational metrics.
    """

    def __init__(
        self,
        repository: GovernanceRepositoryPort | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.repository = repository or InMemoryGovernanceRepository()
        self.event_bus = event_bus or EventBus.get_instance()

    async def record_metric(
        self,
        organization_id: str,
        metric_name: str,
        metric_value: float,
        agent_id: str | None = None,
        dimensions: dict[str, Any] | None = None,
    ) -> AgentMetric:
        """Record a single metric data point."""
        metric = AgentMetric(
            organization_id=organization_id,
            agent_id=agent_id,
            metric_name=metric_name,
            metric_value=metric_value,
            dimensions=dimensions or {},
        )
        saved = await self.repository.save_metric(metric)

        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.metric_recorded",
                source="metrics_service",
                payload={
                    "organization_id": organization_id,
                    "agent_id": agent_id,
                    "metric_name": metric_name,
                    "metric_value": metric_value,
                },
            )
        )

        return saved

    async def get_metrics_summary(
        self,
        organization_id: str,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        """Aggregate metrics summary for tenant or specific agent."""
        all_metrics: Sequence[AgentMetric] = await self.repository.list_metrics(
            organization_id=organization_id,
            agent_id=agent_id,
        )

        summary: dict[str, float] = {}
        counts: dict[str, int] = {}

        for m in all_metrics:
            key = m.metric_name
            summary[key] = summary.get(key, 0.0) + m.metric_value
            counts[key] = counts.get(key, 0) + 1

        return {
            "organization_id": organization_id,
            "agent_id": agent_id,
            "metrics": summary,
            "total_metric_records": len(all_metrics),
        }
