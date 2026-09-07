"""
Data Subject Access Request (DSAR) Workflows — GDPR/CCPA Compliance Engine.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DSARType(StrEnum):
    ACCESS_EXPORT = "ACCESS_EXPORT"
    CORRECTION = "CORRECTION"
    DELETION_ERASURE = "DELETION_ERASURE"
    PORTABILITY = "PORTABILITY"


class DSARStatus(StrEnum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class DSARRequest(BaseModel):
    """Encapsulates a formal employee data access/deletion request."""

    request_id: str = Field(default_factory=lambda: f"dsar-{uuid.uuid4()}")
    organization_id: str
    employee_id: str
    request_type: DSARType
    status: DSARStatus = Field(default=DSARStatus.SUBMITTED)
    details: str = Field(default="")
    review_notes: str | None = None
    reviewed_by: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    completed_at: datetime | None = None


class DSARService:
    """Service processing employee DSAR workflows."""

    _instance: DSARService | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._requests: dict[str, DSARRequest] = {}

    @classmethod
    def get_instance(cls) -> DSARService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def create_request(
        self,
        organization_id: str,
        employee_id: str,
        request_type: DSARType,
        details: str = "",
    ) -> DSARRequest:
        """Submit a new DSAR request."""
        req = DSARRequest(
            organization_id=organization_id,
            employee_id=employee_id,
            request_type=request_type,
            details=details,
        )
        async with self._lock:
            self._requests[req.request_id] = req
            logger.info(f"Created DSAR [{req.request_id}] type '{request_type.value}' for employee '{employee_id}'")
            return req

    async def review_request(
        self,
        request_id: str,
        reviewer_id: str,
        approved: bool,
        notes: str = "",
    ) -> DSARRequest:
        """Human DPO/Admin reviews and approves or rejects request."""
        async with self._lock:
            req = self._requests.get(request_id)
            if not req:
                raise ValueError(f"DSAR request '{request_id}' not found.")

            req.reviewed_by = reviewer_id
            req.review_notes = notes
            req.status = DSARStatus.APPROVED if approved else DSARStatus.REJECTED
            logger.info(f"DSAR [{request_id}] reviewed by '{reviewer_id}': {req.status.value}")
            return req

    async def complete_request(self, request_id: str) -> DSARRequest:
        """Mark DSAR request as fulfilled and completed."""
        async with self._lock:
            req = self._requests.get(request_id)
            if not req:
                raise ValueError(f"DSAR request '{request_id}' not found.")
            req.status = DSARStatus.COMPLETED
            req.completed_at = datetime.now(tz=UTC)
            return req

    async def list_requests(
        self,
        organization_id: str,
        employee_id: str | None = None,
    ) -> Sequence[DSARRequest]:
        """List requests for organization or employee."""
        async with self._lock:
            return [
                r
                for r in self._requests.values()
                if r.organization_id == organization_id and (employee_id is None or r.employee_id == employee_id)
            ]
