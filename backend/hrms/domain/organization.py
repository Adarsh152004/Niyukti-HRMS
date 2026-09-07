"""
HRMS Domain — Organization, Multi-Tenancy, Department, Designation.

The system is designed as a multi-tenant SaaS platform. Every HRMS organization
is a tenant. Tenant isolation is an architectural requirement: every entity
owned by a tenant carries `organization_id`.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from backend.hrms.domain.common import HRMSBaseModel, generate_id, utc_now


class OrganizationStatus(StrEnum):
    """Possible organization/tenant operational statuses."""

    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TRIAL = "TRIAL"
    ARCHIVED = "ARCHIVED"


class DepartmentStatus(StrEnum):
    """Department operational status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class DesignationStatus(StrEnum):
    """Designation operational status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class Organization(HRMSBaseModel):
    """
    The Tenant / Organization domain entity.

    Represents a tenant company operating on the HRMS platform.
    """

    organization_id: str = Field(default_factory=generate_id)
    legal_name: str = Field(description="Legal entity name")
    display_name: str = Field(description="Public/trade display name")
    slug: str = Field(description="Unique URL/tenant identifier slug, e.g. 'acme-corp'")
    industry: str | None = Field(default=None)
    country: str = Field(default="IN", description="ISO 3166 country code")
    timezone: str = Field(default="Asia/Kolkata")
    currency: str = Field(default="INR")
    status: OrganizationStatus = Field(default=OrganizationStatus.ACTIVE)

    # Optional metadata
    registration_number: str | None = Field(default=None)
    logo_url: str | None = Field(default=None)
    website: str | None = Field(default=None)
    address: str | None = Field(default=None)
    founded_year: int | None = Field(default=None)
    employee_count: int = Field(default=0, ge=0)
    settings: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @property
    def id(self) -> str:
        """Alias for organization_id."""
        return self.organization_id

    @property
    def is_active(self) -> bool:
        return self.status == OrganizationStatus.ACTIVE


class Department(HRMSBaseModel):
    """
    An organizational department within a specific tenant.
    """

    department_id: str = Field(default_factory=generate_id)
    organization_id: str = Field(description="Tenant ID boundary")
    name: str
    code: str = Field(description="Short code, e.g. 'ENG'")
    description: str | None = Field(default=None)
    parent_department_id: str | None = Field(default=None)
    manager_employee_id: str | None = Field(default=None, description="Employee ID of department manager/head")
    cost_center: str | None = Field(default=None)
    location: str | None = Field(default=None)
    status: DepartmentStatus = Field(default=DepartmentStatus.ACTIVE)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @property
    def id(self) -> str:
        return self.department_id

    @property
    def is_active(self) -> bool:
        return self.status == DepartmentStatus.ACTIVE


class Designation(HRMSBaseModel):
    """
    A job designation / title within a specific tenant.
    """

    designation_id: str = Field(default_factory=generate_id)
    organization_id: str = Field(description="Tenant ID boundary")
    name: str = Field(description="Designation name, e.g. 'Senior Software Engineer'")
    code: str = Field(description="Designation code, e.g. 'SSE-L3'")
    description: str | None = Field(default=None)
    level: int = Field(default=1, ge=1, description="Hierarchy level — 1 is entry level")
    department_id: str | None = Field(default=None)
    status: DesignationStatus = Field(default=DesignationStatus.ACTIVE)

    min_experience_years: float | None = Field(default=None, ge=0.0)
    is_managerial: bool = Field(default=False)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @property
    def id(self) -> str:
        return self.designation_id

    @property
    def title(self) -> str:
        """Compatibility property for title."""
        return self.name

    @property
    def is_active(self) -> bool:
        return self.status == DesignationStatus.ACTIVE
