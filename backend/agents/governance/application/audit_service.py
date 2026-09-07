"""
Audit Service — Produces immutable governance audit records with secret redaction and correlation IDs.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from backend.agents.governance.domain.models import AgentAuditRecord
from backend.agents.governance.infrastructure.database.repositories import InMemoryGovernanceRepository
from backend.agents.governance.ports.repositories import GovernanceRepositoryPort
from backend.runtime.events import Event, EventBus

logger = logging.getLogger(__name__)

SECRET_KEYS = {"password", "token", "secret", "api_key", "jwt", "authorization", "bearer"}


def redact_secrets(data: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive keys from audit dictionary metadata."""
    redacted: dict[str, Any] = {}
    for k, v in data.items():
        if any(sk in k.lower() for sk in SECRET_KEYS):
            redacted[k] = "[REDACTED]"
        elif isinstance(v, dict):
            redacted[k] = redact_secrets(v)
        else:
            redacted[k] = v
    return redacted


class AuditService:
    """
    Application service managing immutable governance audit records.
    """

    def __init__(
        self,
        repository: GovernanceRepositoryPort | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.repository = repository or InMemoryGovernanceRepository()
        self.event_bus = event_bus or EventBus.get_instance()

    async def record_audit(
        self,
        organization_id: str,
        agent_id: str,
        event_type: str,
        action: str,
        resource: str,
        actor_id: str,
        task_id: str | None = None,
        tool_name: str | None = None,
        command_name: str | None = None,
        risk_level: str = "LOW",
        policy_result: str = "SUCCESS",
        authorization_result: str = "AUTHORIZED",
        approval_required: bool = False,
        approval_status: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentAuditRecord:
        """Create and persist an immutable governance audit record with secret redaction."""
        safe_meta = redact_secrets(metadata or {})

        record = AgentAuditRecord(
            organization_id=organization_id,
            agent_id=agent_id,
            task_id=task_id,
            event_type=event_type,
            action=action,
            resource=resource,
            tool_name=tool_name,
            command_name=command_name,
            risk_level=risk_level,
            policy_result=policy_result,
            authorization_result=authorization_result,
            approval_required=approval_required,
            approval_status=approval_status,
            actor_id=actor_id,
            metadata=safe_meta,
        )

        saved = await self.repository.save_audit_record(record)

        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.audit_recorded",
                source="audit_service",
                payload={
                    "audit_id": saved.audit_id,
                    "agent_id": agent_id,
                    "organization_id": organization_id,
                    "event_type": event_type,
                    "action": action,
                },
            )
        )

        return saved

    async def list_audit_records(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str | None = None,
    ) -> Sequence[AgentAuditRecord]:
        """Retrieve audit records within tenant boundary."""
        return await self.repository.list_audit_records(organization_id, agent_id, task_id=task_id)
