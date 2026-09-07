"""
HRMS Domain — Role model.

Roles are custom tenant-level security roles defined per organization.
Do not hardcode company-specific roles.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from backend.hrms.domain.common import HRMSBaseModel, generate_id, utc_now


class RoleStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class Role(HRMSBaseModel):
    """
    Tenant-customizable security role.
    """

    role_id: str = Field(default_factory=generate_id)
    organization_id: str = Field(description="Tenant ID boundary")
    name: str = Field(description="Role name e.g. 'Payroll Specialist', 'Engineering Manager'")
    code: str = Field(description="Role identifier code, e.g. 'ROLE_PAYROLL_SPEC'")
    description: str | None = Field(default=None)
    permissions: set[str] = Field(
        default_factory=set,
        description="Set of fine-grained permission codes granted to this role",
    )
    status: RoleStatus = Field(default=RoleStatus.ACTIVE)
    is_system_role: bool = Field(default=False, description="System default role vs custom role")
    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @property
    def id(self) -> str:
        return self.role_id

    @property
    def is_active(self) -> bool:
        return self.status == RoleStatus.ACTIVE
