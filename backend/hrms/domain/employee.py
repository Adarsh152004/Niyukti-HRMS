"""
HRMS Domain — Employee model and State Transition Validation.

PII Classification:
- INTERNAL: first_name, last_name, preferred_name, email, employee_code
- CONFIDENTIAL: phone, location, address
- SENSITIVE: date_of_birth, performance
- HIGHLY_SENSITIVE: salary, national_id, bank_account_number
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from backend.hrms.domain.common import Gender, HRMSBaseModel, generate_id, utc_now
from backend.hrms.domain.exceptions import InvalidEmployeeState


class EmploymentStatus(StrEnum):
    """Lifecycle status of an employee."""

    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    SUSPENDED = "SUSPENDED"
    RESIGNED = "RESIGNED"
    TERMINATED = "TERMINATED"
    RETIRED = "RETIRED"


class EmploymentType(StrEnum):
    """Type of employment contract."""

    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERN = "INTERN"
    TEMPORARY = "TEMPORARY"


# Allowed state transition mapping
ALLOWED_STATUS_TRANSITIONS: dict[EmploymentStatus, set[EmploymentStatus]] = {
    EmploymentStatus.ACTIVE: {
        EmploymentStatus.ON_LEAVE,
        EmploymentStatus.SUSPENDED,
        EmploymentStatus.RESIGNED,
        EmploymentStatus.TERMINATED,
        EmploymentStatus.RETIRED,
    },
    EmploymentStatus.ON_LEAVE: {
        EmploymentStatus.ACTIVE,
        EmploymentStatus.RESIGNED,
        EmploymentStatus.TERMINATED,
    },
    EmploymentStatus.SUSPENDED: {
        EmploymentStatus.ACTIVE,
        EmploymentStatus.TERMINATED,
        EmploymentStatus.RESIGNED,
    },
    EmploymentStatus.RESIGNED: {
        EmploymentStatus.TERMINATED,
        EmploymentStatus.RETIRED,
    },
    # Terminal states (cannot transition to any other status)
    EmploymentStatus.TERMINATED: set(),
    EmploymentStatus.RETIRED: set(),
}


def validate_status_transition(current: EmploymentStatus, target: EmploymentStatus) -> None:
    """
    Validate that an employee status transition is legally allowed.

    Raises:
        InvalidEmployeeState: If the transition is prohibited.
    """
    if current == target:
        return
    allowed = ALLOWED_STATUS_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidEmployeeState(current.value, target.value)


class Employee(HRMSBaseModel):
    """
    Core Employee domain entity.
    """

    employee_id: str = Field(default_factory=generate_id)
    organization_id: str = Field(description="Tenant ID boundary")
    employee_code: str = Field(description="Unique employee code within tenant e.g. 'EMP-001'")

    # Personal Information
    first_name: str = Field(description="[PII:INTERNAL]")
    last_name: str = Field(description="[PII:INTERNAL]")
    preferred_name: str | None = Field(default=None, description="[PII:INTERNAL]")
    email: str = Field(description="[PII:INTERNAL] Work email address")
    phone: str | None = Field(default=None, description="[PII:CONFIDENTIAL]")
    date_of_birth: date | None = Field(default=None, description="[PII:SENSITIVE]")
    gender: Gender | None = Field(default=None)

    # Organizational Structure
    department_id: str
    designation_id: str
    manager_id: str | None = Field(default=None, description="Employee ID of reporting manager")

    # Employment Information
    employment_status: EmploymentStatus = Field(default=EmploymentStatus.ACTIVE)
    employment_type: EmploymentType = Field(default=EmploymentType.FULL_TIME)
    joining_date: date
    exit_date: date | None = Field(default=None)

    # Location & Timezone
    location: str | None = Field(default=None, description="Work location e.g. 'Mumbai HQ'")
    timezone: str = Field(default="Asia/Kolkata")

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @property
    def id(self) -> str:
        return self.employee_id

    @property
    def full_name(self) -> str:
        """Derive full name from first and last name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active(self) -> bool:
        return self.employment_status == EmploymentStatus.ACTIVE

    def transition_status(self, target_status: EmploymentStatus) -> None:
        """Transition employee status after validating state machine rules."""
        validate_status_transition(self.employment_status, target_status)
        self.employment_status = target_status
        self.updated_at = utc_now()
        if target_status in (EmploymentStatus.TERMINATED, EmploymentStatus.RETIRED) and not self.exit_date:
            self.exit_date = date.today()


class EmployeeDocument(HRMSBaseModel):
    """
    Metadata record for an employee document.
    """

    document_id: str = Field(default_factory=generate_id)
    organization_id: str = Field(description="Tenant ID boundary")
    employee_id: str
    document_type: str = Field(description="e.g. 'RESUME', 'ID_DOCUMENT', 'CONTRACT'")
    document_name: str
    storage_reference: str = Field(description="Opaque storage reference / object key")
    mime_type: str = Field(default="application/pdf")
    size: int = Field(ge=0, description="Size in bytes")
    checksum: str | None = Field(default=None, description="SHA-256 checksum")
    verification_status: str = Field(default="UNVERIFIED", description="UNVERIFIED, VERIFIED, REJECTED")
    uploaded_at: datetime = Field(default_factory=utc_now)
    verified_at: datetime | None = Field(default=None)
    expires_at: date | None = Field(default=None)

    @property
    def id(self) -> str:
        return self.document_id


class EmploymentHistory(HRMSBaseModel):
    """Internal or external employment movement history."""

    history_id: str = Field(default_factory=generate_id)
    employee_id: str
    organization_id: str
    is_internal: bool = Field(default=True)
    from_department_id: str | None = Field(default=None)
    to_department_id: str | None = Field(default=None)
    from_designation_id: str | None = Field(default=None)
    to_designation_id: str | None = Field(default=None)
    start_date: date
    end_date: date | None = Field(default=None)
    reason_for_change: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
