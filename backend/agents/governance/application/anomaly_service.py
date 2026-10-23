"""
Anomaly Service — Rule-based deterministic anomaly detection engine.
Detects suspicious agent behavior, capability escalation, policy violations, and cross-tenant attempts.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from backend.agents.governance.domain.enums import AnomalyType, Severity
from backend.agents.governance.domain.models import AgentAnomaly
from backend.agents.governance.infrastructure.database.repositories import InMemoryGovernanceRepository
from backend.agents.governance.ports.repositories import GovernanceRepositoryPort
from backend.runtime.events import Event, EventBus

logger = logging.getLogger(__name__)


class AnomalyService:
    """
    Application Service performing deterministic anomaly detection and evidence logging.
    """

    def __init__(
        self,
        repository: GovernanceRepositoryPort | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.repository = repository or InMemoryGovernanceRepository()
        self.event_bus = event_bus or EventBus.get_instance()

    async def detect_and_record_anomaly(
        self,
        organization_id: str,
        agent_id: str,
        anomaly_type: AnomalyType,
        severity: Severity,
        evidence: dict[str, Any],
        task_id: str | None = None,
    ) -> AgentAnomaly:
        """
        Record a detected anomaly with evidence and publish an anomaly event.
        """
        anomaly = AgentAnomaly(
            organization_id=organization_id,
            agent_id=agent_id,
            task_id=task_id,
            anomaly_type=anomaly_type,
            severity=severity,
            score=1.0 if severity == Severity.CRITICAL else (0.8 if severity == Severity.HIGH else 0.5),
            evidence=evidence,
        )

        saved = await self.repository.save_anomaly(anomaly)
        logger.warning(f"Anomaly detected [{severity.value}] for agent '{agent_id}': {anomaly_type.value}")

        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.anomaly_detected",
                source="anomaly_service",
                payload={
                    "anomaly_id": saved.anomaly_id,
                    "agent_id": agent_id,
                    "organization_id": organization_id,
                    "anomaly_type": anomaly_type.value,
                    "severity": severity.value,
                    "evidence": evidence,
                },
            )
        )

        return saved

    async def list_anomalies(
        self,
        organization_id: str,
        agent_id: str,
        status: str | None = None,
    ) -> Sequence[AgentAnomaly]:
        """List recorded anomalies for an agent."""
        return await self.repository.list_anomalies(organization_id, agent_id, status=status)
