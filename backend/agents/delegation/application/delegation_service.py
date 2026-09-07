"""
Delegation Service — Application service managing Delegation lifecycle and events.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from backend.agents.application.agent_service import AgentService
from backend.agents.delegation.application.delegation_validator import DelegationValidator
from backend.agents.delegation.domain.enums import DelegationScope, DelegationStatus
from backend.agents.delegation.domain.exceptions import DelegationAccessDeniedError, DelegationExpiredError
from backend.agents.delegation.domain.models import Delegation
from backend.agents.delegation.infrastructure.database.repositories import InMemoryDelegationRepository
from backend.agents.delegation.ports.repositories import DelegationRepositoryPort
from backend.agents.domain.models import AgentCapability
from backend.hrms.domain.actor import Actor, ActorType
from backend.runtime.events import Event, EventBus

logger = logging.getLogger(__name__)


class DelegationService:
    """
    Manages complete Delegation lifecycle: creation, approval, activation, revocation, cancellation, and event publishing.
    """

    def __init__(
        self,
        repository: DelegationRepositoryPort | None = None,
        validator: DelegationValidator | None = None,
        agent_service: AgentService | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.repository = repository or InMemoryDelegationRepository()
        self.agent_service = agent_service or AgentService()
        self.validator = validator or DelegationValidator(agent_service=self.agent_service)
        self.event_bus = event_bus or EventBus.get_instance()

    async def create_delegation(
        self,
        organization_id: str,
        delegator_agent_id: str,
        delegate_agent_id: str,
        parent_task_id: str,
        requested_capabilities: list[AgentCapability],
        expires_at: datetime,
        scope: DelegationScope = DelegationScope.TASK_SCOPED,
        allow_further_delegation: bool = False,
        parent_delegation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Delegation:
        """Create a new delegation request after validating against DelegationPolicy."""
        parent_del = None
        if parent_delegation_id:
            parent_del = await self.repository.get_delegation(organization_id, parent_delegation_id)

        # Pre-flight validation & capability intersection
        effective_caps = await self.validator.validate_request(
            organization_id=organization_id,
            delegator_agent_id=delegator_agent_id,
            delegate_agent_id=delegate_agent_id,
            requested_capabilities=requested_capabilities,
            expires_at=expires_at,
            parent_delegation=parent_del,
        )

        # Check if any effective cap requires HITL approval
        requires_hitl = any(c.requires_hitl or c.risk_level in ["HIGH", "CRITICAL"] for c in effective_caps)

        # Compute payload hash
        payload_data = {
            "delegator_agent_id": delegator_agent_id,
            "delegate_agent_id": delegate_agent_id,
            "parent_task_id": parent_task_id,
            "capabilities": [c.model_dump() for c in effective_caps],
        }
        payload_hash = hashlib.sha256(json.dumps(payload_data, sort_keys=True, default=str).encode("utf-8")).hexdigest()

        delegation = Delegation(
            organization_id=organization_id,
            delegator_agent_id=delegator_agent_id,
            delegate_agent_id=delegate_agent_id,
            parent_task_id=parent_task_id,
            capabilities=effective_caps,
            scope=scope,
            status=DelegationStatus.REQUESTED,
            expires_at=expires_at,
            parent_delegation_id=parent_delegation_id,
            allow_further_delegation=allow_further_delegation,
            payload_hash=payload_hash,
            metadata=metadata or {},
        )

        # Auto-activate if no HITL required; otherwise stay in REQUESTED/APPROVED flow
        if not requires_hitl:
            delegation.transition_to(DelegationStatus.APPROVED)
            delegation.transition_to(DelegationStatus.ACTIVE)
        else:
            logger.info(f"Delegation '{delegation.delegation_id}' requires HITL approval due to high risk capabilities.")

        saved = await self.repository.save_delegation(delegation)

        # Emit event
        event_type = (
            "hrms.agent.delegation.activated" if saved.status == DelegationStatus.ACTIVE else "hrms.agent.delegation.requested"
        )
        await self.event_bus.publish(
            Event(
                event_type=event_type,
                source="delegation_service",
                payload={
                    "delegation_id": saved.delegation_id,
                    "organization_id": saved.organization_id,
                    "delegator_agent_id": saved.delegator_agent_id,
                    "delegate_agent_id": saved.delegate_agent_id,
                    "correlation_id": saved.correlation_id,
                    "status": saved.status.value,
                },
            )
        )

        return saved

    async def approve_delegation(
        self,
        organization_id: str,
        delegation_id: str,
        approver_actor: Actor,
    ) -> Delegation:
        """Approve a requested delegation. Approver actor MUST be HUMAN."""
        delegation = await self.repository.get_delegation(organization_id, delegation_id)
        if not delegation:
            raise ValueError(f"Delegation '{delegation_id}' not found.")

        # AI Agent cannot approve delegation
        if approver_actor.actor_type == ActorType.AI_AGENT:
            raise DelegationAccessDeniedError("AI Agents are strictly prohibited from approving delegation requests.")

        if approver_actor.organization_id != organization_id:
            raise DelegationAccessDeniedError("Approver organization mismatch.")

        if datetime.now(tz=UTC) >= delegation.expires_at:
            delegation.transition_to(DelegationStatus.EXPIRED)
            await self.repository.save_delegation(delegation)
            raise DelegationExpiredError(f"Delegation '{delegation_id}' has expired.")

        delegation.transition_to(DelegationStatus.APPROVED)
        delegation.transition_to(DelegationStatus.ACTIVE)
        saved = await self.repository.save_delegation(delegation)

        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.delegation.approved",
                source="delegation_service",
                payload={
                    "delegation_id": saved.delegation_id,
                    "organization_id": saved.organization_id,
                    "approver_actor_id": approver_actor.actor_id,
                    "correlation_id": saved.correlation_id,
                },
            )
        )

        return saved

    async def reject_delegation(
        self,
        organization_id: str,
        delegation_id: str,
        reason: str,
    ) -> Delegation:
        """Reject a requested delegation."""
        delegation = await self.repository.get_delegation(organization_id, delegation_id)
        if not delegation:
            raise ValueError(f"Delegation '{delegation_id}' not found.")

        delegation.transition_to(DelegationStatus.REJECTED)
        delegation.rejection_reason = reason
        saved = await self.repository.save_delegation(delegation)

        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.delegation.rejected",
                source="delegation_service",
                payload={
                    "delegation_id": saved.delegation_id,
                    "organization_id": saved.organization_id,
                    "reason": reason,
                    "correlation_id": saved.correlation_id,
                },
            )
        )

        return saved

    async def revoke_delegation(
        self,
        organization_id: str,
        delegation_id: str,
        reason: str,
    ) -> Delegation:
        """Revoke an active delegation."""
        delegation = await self.repository.get_delegation(organization_id, delegation_id)
        if not delegation:
            raise ValueError(f"Delegation '{delegation_id}' not found.")

        delegation.transition_to(DelegationStatus.REVOKED)
        delegation.revocation_reason = reason
        saved = await self.repository.save_delegation(delegation)

        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.delegation.revoked",
                source="delegation_service",
                payload={
                    "delegation_id": saved.delegation_id,
                    "organization_id": saved.organization_id,
                    "reason": reason,
                    "correlation_id": saved.correlation_id,
                },
            )
        )

        return saved

    async def cancel_delegation(
        self,
        organization_id: str,
        delegation_id: str,
    ) -> Delegation:
        """Cancel a delegation."""
        delegation = await self.repository.get_delegation(organization_id, delegation_id)
        if not delegation:
            raise ValueError(f"Delegation '{delegation_id}' not found.")

        delegation.transition_to(DelegationStatus.CANCELLED)
        saved = await self.repository.save_delegation(delegation)

        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.delegation.cancelled",
                source="delegation_service",
                payload={
                    "delegation_id": saved.delegation_id,
                    "organization_id": saved.organization_id,
                    "correlation_id": saved.correlation_id,
                },
            )
        )

        return saved

    async def get_delegation(self, organization_id: str, delegation_id: str) -> Delegation | None:
        """Retrieve delegation by ID within tenant boundary."""
        delegation = await self.repository.get_delegation(organization_id, delegation_id)
        if delegation and delegation.status == DelegationStatus.ACTIVE and datetime.now(tz=UTC) >= delegation.expires_at:
            delegation.transition_to(DelegationStatus.EXPIRED)
            await self.repository.save_delegation(delegation)
        return delegation

    async def list_delegations(
        self,
        organization_id: str,
        delegator_agent_id: str | None = None,
        delegate_agent_id: str | None = None,
    ) -> Sequence[Delegation]:
        """List delegations within tenant boundary."""
        return await self.repository.list_delegations(
            organization_id=organization_id,
            delegator_agent_id=delegator_agent_id,
            delegate_agent_id=delegate_agent_id,
        )
