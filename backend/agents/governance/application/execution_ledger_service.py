"""
Execution Ledger Service — Appends and maintains immutable structured execution trajectory records.
Agents cannot modify or delete execution ledger entries.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from backend.agents.governance.domain.exceptions import LedgerImmutabilityError
from backend.agents.governance.domain.models import ExecutionLedgerEntry
from backend.agents.governance.infrastructure.database.repositories import InMemoryGovernanceRepository
from backend.agents.governance.ports.repositories import GovernanceRepositoryPort
from backend.hrms.domain.actor import Actor

logger = logging.getLogger(__name__)


class ExecutionLedgerService:
    """
    Application Service managing the append-only Execution Ledger.
    """

    def __init__(
        self,
        repository: GovernanceRepositoryPort | None = None,
    ) -> None:
        self.repository = repository or InMemoryGovernanceRepository()

    async def record_execution(self, entry: ExecutionLedgerEntry) -> ExecutionLedgerEntry:
        """Append an immutable ledger record."""
        return await self.repository.append_ledger_entry(entry)

    async def list_ledger_entries(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str | None = None,
    ) -> Sequence[ExecutionLedgerEntry]:
        """Retrieve ledger records within tenant boundary."""
        return await self.repository.list_ledger_entries(
            organization_id=organization_id,
            agent_id=agent_id,
            task_id=task_id,
        )

    async def attempt_delete_ledger(self, actor: Actor) -> None:
        """
        SECURITY INVARIANT: Execution Ledger is IMMUTABLE.
        Deleting ledger records is strictly forbidden for all actors.
        """
        raise LedgerImmutabilityError("Execution Ledger entries are immutable and cannot be deleted.")
