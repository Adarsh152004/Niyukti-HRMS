"""
Delegation Repository Port — Repository interface for delegation entities.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from backend.agents.delegation.domain.models import DelegatedTask, Delegation


class DelegationRepositoryPort(ABC):
    """Abstract interface for delegation entity storage."""

    @abstractmethod
    async def save_delegation(self, delegation: Delegation) -> Delegation:
        """Save or update delegation entity."""
        pass

    @abstractmethod
    async def get_delegation(self, organization_id: str, delegation_id: str) -> Delegation | None:
        """Retrieve delegation by ID within tenant boundary."""
        pass

    @abstractmethod
    async def list_delegations(
        self,
        organization_id: str,
        delegator_agent_id: str | None = None,
        delegate_agent_id: str | None = None,
    ) -> Sequence[Delegation]:
        """List delegations filtered by delegator/delegate within tenant."""
        pass

    @abstractmethod
    async def save_delegated_task(self, task: DelegatedTask) -> DelegatedTask:
        """Save or update delegated sub-task."""
        pass

    @abstractmethod
    async def get_delegated_task(self, organization_id: str, task_id: str) -> DelegatedTask | None:
        """Retrieve delegated task by ID."""
        pass
