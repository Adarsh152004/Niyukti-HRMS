"""
Idempotency Engine — Command deduplication and payload hash mismatch protection.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.commands.domain.enums import CommandStatus
from backend.commands.domain.models import IdempotencyRecord


class IdempotencyMismatchError(Exception):
    """Raised when an idempotency key is reused with a different payload hash."""

    pass


class IdempotencyEngine:
    """
    Deduplication engine managing command idempotency records.
    """

    def __init__(self) -> None:
        self._records: dict[tuple[str, str], IdempotencyRecord] = {}  # (org_id, key) -> Record

    def get_record(self, organization_id: str, idempotency_key: str) -> IdempotencyRecord | None:
        """Lookup idempotency record by tenant and key."""
        return self._records.get((organization_id, idempotency_key))

    def record_execution(
        self,
        organization_id: str,
        idempotency_key: str,
        command_id: str,
        payload_hash: str,
        status: CommandStatus,
        result_data: dict[str, Any],
    ) -> IdempotencyRecord:
        """Record command execution result under idempotency key."""
        existing = self.get_record(organization_id, idempotency_key)
        if existing and existing.payload_hash != payload_hash:
            raise IdempotencyMismatchError(f"Idempotency key '{idempotency_key}' was previously used with a different payload.")

        rec = IdempotencyRecord(
            idempotency_key=idempotency_key,
            command_id=command_id,
            organization_id=organization_id,
            payload_hash=payload_hash,
            status=status,
            result_data=result_data,
            created_at=datetime.now(tz=UTC),
        )
        self._records[(organization_id, idempotency_key)] = rec
        return rec
