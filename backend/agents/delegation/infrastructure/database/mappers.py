"""
Delegation Database Mappers — Bidirectional mapping between domain entities and ORM models.
"""

from __future__ import annotations

from backend.agents.delegation.domain.enums import DelegationScope, DelegationStatus
from backend.agents.delegation.domain.models import DelegatedTask, Delegation
from backend.agents.delegation.infrastructure.database.models import DelegatedTaskModel, DelegationModel
from backend.agents.domain.models import AgentCapability


class DelegationMapper:
    """Bidirectional mapper for Delegation domain model."""

    @staticmethod
    def to_model(domain: Delegation) -> DelegationModel:
        return DelegationModel(
            id=domain.delegation_id,
            organization_id=domain.organization_id,
            delegator_agent_id=domain.delegator_agent_id,
            delegate_agent_id=domain.delegate_agent_id,
            parent_task_id=domain.parent_task_id,
            delegated_task_id=domain.delegated_task_id,
            capabilities_json=[c.model_dump() for c in domain.capabilities],
            scope=domain.scope.value,
            status=domain.status.value,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            expires_at=domain.expires_at,
            correlation_id=domain.correlation_id,
            parent_delegation_id=domain.parent_delegation_id,
            allow_further_delegation=domain.allow_further_delegation,
            payload_hash=domain.payload_hash,
            rejection_reason=domain.rejection_reason,
            revocation_reason=domain.revocation_reason,
            metadata_json=domain.metadata,
        )

    @staticmethod
    def to_domain(model: DelegationModel) -> Delegation:
        return Delegation(
            delegation_id=model.id,
            organization_id=model.organization_id,
            delegator_agent_id=model.delegator_agent_id,
            delegate_agent_id=model.delegate_agent_id,
            parent_task_id=model.parent_task_id,
            delegated_task_id=model.delegated_task_id,
            capabilities=[AgentCapability(**c) for c in model.capabilities_json],
            scope=DelegationScope(model.scope),
            status=DelegationStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            expires_at=model.expires_at,
            correlation_id=model.correlation_id,
            parent_delegation_id=model.parent_delegation_id,
            allow_further_delegation=model.allow_further_delegation,
            payload_hash=model.payload_hash,
            rejection_reason=model.rejection_reason,
            revocation_reason=model.revocation_reason,
            metadata=model.metadata_json,
        )


class DelegatedTaskMapper:
    """Bidirectional mapper for DelegatedTask domain model."""

    @staticmethod
    def to_model(domain: DelegatedTask) -> DelegatedTaskModel:
        return DelegatedTaskModel(
            id=domain.task_id,
            delegation_id=domain.delegation_id,
            organization_id=domain.organization_id,
            delegator_agent_id=domain.delegator_agent_id,
            delegate_agent_id=domain.delegate_agent_id,
            goal=domain.goal,
            status=domain.status,
            result_json=domain.result,
            failure_reason=domain.failure_reason,
            created_at=domain.created_at,
            completed_at=domain.completed_at,
        )

    @staticmethod
    def to_domain(model: DelegatedTaskModel) -> DelegatedTask:
        return DelegatedTask(
            task_id=model.id,
            delegation_id=model.delegation_id,
            organization_id=model.organization_id,
            delegator_agent_id=model.delegator_agent_id,
            delegate_agent_id=model.delegate_agent_id,
            goal=model.goal,
            status=model.status,
            result=model.result_json,
            failure_reason=model.failure_reason,
            created_at=model.created_at,
            completed_at=model.completed_at,
        )
