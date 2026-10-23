"""
Idempotency Engine — Guarantees exactly-once semantics for mutation endpoints.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from backend.api.governance.models import IdempotencyRecord

logger = logging.getLogger(__name__)


class IdempotencyConflictError(Exception):
    """Raised when a matching idempotency key is reused with different request payload."""

    pass


class IdempotencyEngine:
    """In-memory idempotency cache and validation engine."""

    _instance: IdempotencyEngine | None = None

    def __init__(self, ttl_seconds: int = 86400) -> None:
        self._lock = asyncio.Lock()
        self._store: dict[str, IdempotencyRecord] = {}
        self.ttl_seconds = ttl_seconds

    @classmethod
    def get_instance(cls) -> IdempotencyEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def compute_hash(payload: Any) -> str:
        """Deterministic SHA-256 hash of request payload."""
        normalized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    async def get_or_lock(
        self,
        idempotency_key: str,
        organization_id: str,
        actor_id: str,
        request_path: str,
        payload: Any,
    ) -> IdempotencyRecord | None:
        """
        Retrieve existing cached response for key.
        Validates that the payload hash matches the original request.
        """
        key = f"{organization_id}:{idempotency_key}"
        request_hash = self.compute_hash(payload)

        async with self._lock:
            record = self._store.get(key)
            if not record:
                return None

            # Check expiration
            if datetime.now(tz=UTC) > record.expires_at:
                del self._store[key]
                return None

            # Verify request hash
            if record.request_hash != request_hash:
                raise IdempotencyConflictError(
                    f"Idempotency key '{idempotency_key}' was previously used with a different request payload."
                )

            logger.info(f"Idempotency cache hit for key '{idempotency_key}'")
            return record

    async def store_response(
        self,
        idempotency_key: str,
        organization_id: str,
        actor_id: str,
        request_path: str,
        payload: Any,
        status_code: int,
        response_body: dict[str, Any],
    ) -> IdempotencyRecord:
        """Cache the completed response under the idempotency key."""
        key = f"{organization_id}:{idempotency_key}"
        now = datetime.now(tz=UTC)
        record = IdempotencyRecord(
            idempotency_key=idempotency_key,
            organization_id=organization_id,
            actor_id=actor_id,
            request_path=request_path,
            request_hash=self.compute_hash(payload),
            status_code=status_code,
            response_body=response_body,
            created_at=now,
            expires_at=now + timedelta(seconds=self.ttl_seconds),
        )

        async with self._lock:
            self._store[key] = record
            return record

    async def clear(self) -> None:
        """Clear all stored records."""
        async with self._lock:
            self._store.clear()
