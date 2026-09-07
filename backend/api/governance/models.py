"""
API Governance Models — Standard contracts for pagination, error envelopes, and idempotency.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Standard cursor and offset pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number, 1-indexed")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    cursor: str | None = Field(default=None, description="Opaque cursor for keyset pagination")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated container."""

    items: Sequence[T]
    total_count: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_pages: int = Field(ge=0)
    has_next: bool
    has_previous: bool
    next_cursor: str | None = None


class StandardErrorDetail(BaseModel):
    """Detailed error object conforming to enterprise standards."""

    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error description")
    field: str | None = Field(default=None, description="Target field name if validation error")
    details: dict[str, Any] | None = Field(default=None, description="Additional debug/context metadata")


class StandardErrorEnvelope(BaseModel):
    """Standard top-level error response envelope."""

    error: StandardErrorDetail
    request_id: str = Field(description="Trace / correlation ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    status_code: int = Field(default=400)


class IdempotencyRecord(BaseModel):
    """Record of an idempotent request and its cached response."""

    idempotency_key: str
    organization_id: str
    actor_id: str
    request_path: str
    request_hash: str
    status_code: int
    response_body: dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    expires_at: datetime
