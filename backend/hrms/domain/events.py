"""
HRMS Domain Events — Tenant-aware, audit-ready domain event contracts.

Domain events are published when state mutations occur.
Every event explicitly includes `organization_id` and `actor`.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    """
    Base contract for all HRMS domain events.
    """

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str = Field(description="Tenant boundary")
    aggregate_id: str = Field(description="ID of the entity that underwent change")
    event_type: str = Field(description="Class name or event category identifier")
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    actor: dict[str, Any] = Field(description="Actor snapshot (actor_id, actor_type, identity)")
    metadata: dict[str, Any] = Field(default_factory=dict)


class OrganizationCreated(DomainEvent):
    event_type: str = "OrganizationCreated"


class DepartmentCreated(DomainEvent):
    event_type: str = "DepartmentCreated"


class DesignationCreated(DomainEvent):
    event_type: str = "DesignationCreated"


class EmployeeCreated(DomainEvent):
    event_type: str = "EmployeeCreated"


class EmployeeUpdated(DomainEvent):
    event_type: str = "EmployeeUpdated"


class EmployeeJoined(DomainEvent):
    event_type: str = "EmployeeJoined"


class EmployeeTransferred(DomainEvent):
    event_type: str = "EmployeeTransferred"


class EmployeeResigned(DomainEvent):
    event_type: str = "EmployeeResigned"


class EmployeeTerminated(DomainEvent):
    event_type: str = "EmployeeTerminated"


class EmployeeSkillAdded(DomainEvent):
    event_type: str = "EmployeeSkillAdded"


class EmployeeSkillUpdated(DomainEvent):
    event_type: str = "EmployeeSkillUpdated"


class EmployeeDocumentUploaded(DomainEvent):
    event_type: str = "EmployeeDocumentUploaded"


class EmployeeDocumentVerified(DomainEvent):
    event_type: str = "EmployeeDocumentVerified"
