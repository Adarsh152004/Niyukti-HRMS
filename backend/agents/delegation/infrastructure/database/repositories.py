"""
Delegation Repositories — In-Memory & Database repository implementations.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from backend.agents.delegation.domain.models import DelegatedTask, Delegation
from backend.agents.delegation.ports.repositories import DelegationRepositoryPort

logger = logging.getLogger(__name__)


class InMemoryDelegationRepository(DelegationRepositoryPort):
    """In-memory repository for unit tests and local execution."""

    def __init__(self) -> None:
        self._delegations: dict[str, Delegation] = {}
        self._delegated_tasks: dict[str, DelegatedTask] = {}

    async def save_delegation(self, delegation: Delegation) -> Delegation:
        key = f"{delegation.organization_id}:{delegation.delegation_id}"
        self._delegations[key] = delegation
        return delegation

    async def get_delegation(self, organization_id: str, delegation_id: str) -> Delegation | None:
        key = f"{organization_id}:{delegation_id}"
        return self._delegations.get(key)

    async def list_delegations(
        self,
        organization_id: str,
        delegator_agent_id: str | None = None,
        delegate_agent_id: str | None = None,
    ) -> Sequence[Delegation]:
        results: list[Delegation] = []
        for del_obj in self._delegations.values():
            if del_obj.organization_id != organization_id:
                continue
            if delegator_agent_id and del_obj.delegator_agent_id != delegator_agent_id:
                continue
            if delegate_agent_id and del_obj.delegate_agent_id != delegate_agent_id:
                continue
            results.append(del_obj)
        return results

    async def save_delegated_task(self, task: DelegatedTask) -> DelegatedTask:
        key = f"{task.organization_id}:{task.task_id}"
        self._delegated_tasks[key] = task
        return task

    async def get_delegated_task(self, organization_id: str, task_id: str) -> DelegatedTask | None:
        key = f"{organization_id}:{task_id}"
        return self._delegated_tasks.get(key)
