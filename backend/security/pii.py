"""
Security — PII Classification and Protection contracts.

HRMS handles highly sensitive employee information.
This module defines classification levels, field-level PII tagging,
masking contracts, and data protection policies.

CRITICAL: PII must never appear in logs, audit records, or AI decision records.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class PIIClassification(StrEnum):
    """
    PII sensitivity classification levels.

    Levels:
        PUBLIC:           Non-personal, publicly shareable (e.g., job title, department name).
        INTERNAL:         Internal-only (e.g., employee ID, first_name, last_name, work email).
        CONFIDENTIAL:     Personally identifiable (e.g., phone, location, personal address).
        SENSITIVE:        Sensitive operational data (e.g., DOB, performance rating).
        HIGHLY_SENSITIVE: Highly sensitive / restricted (e.g., salary, SSN/National ID, bank account).
    """

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    SENSITIVE = "SENSITIVE"
    HIGHLY_SENSITIVE = "HIGHLY_SENSITIVE"

    # Backward compatibility alias
    RESTRICTED = "HIGHLY_SENSITIVE"

    @property
    def requires_encryption_at_rest(self) -> bool:
        return self in (PIIClassification.SENSITIVE, PIIClassification.HIGHLY_SENSITIVE)

    @property
    def requires_access_log(self) -> bool:
        return self in (
            PIIClassification.CONFIDENTIAL,
            PIIClassification.SENSITIVE,
            PIIClassification.HIGHLY_SENSITIVE,
        )

    @property
    def mask_in_logs(self) -> bool:
        return self in (
            PIIClassification.CONFIDENTIAL,
            PIIClassification.SENSITIVE,
            PIIClassification.HIGHLY_SENSITIVE,
        )

    @property
    def ai_agent_access_allowed(self) -> bool:
        """
        Return True if AI agents may access fields with this classification.
        CONFIDENTIAL, SENSITIVE, and HIGHLY_SENSITIVE require explicit scope grant.
        """
        return self in (PIIClassification.PUBLIC, PIIClassification.INTERNAL)


class PIIField(BaseModel):
    """
    Metadata for a single PII field within a domain model.
    """

    field_name: str
    model_name: str = Field(description="Domain model this field belongs to, e.g. 'Employee'")
    classification: PIIClassification
    description: str = Field(default="")
    retention_days: int | None = Field(
        default=None,
        description="Days to retain this data after employee offboarding.",
    )
    encrypt_at_rest: bool = Field(default=False)
    mask_pattern: str | None = Field(
        default=None,
        description="Regex or format pattern for masking, e.g. '***@***.***' for email.",
    )

    @property
    def must_be_masked_in_logs(self) -> bool:
        return self.classification.mask_in_logs


class PIIProtectionPolicy(BaseModel):
    """
    Organization-level PII protection configuration.
    """

    organization_id: str
    data_residency_region: str = Field(default="IN", description="ISO 3166 country code")
    encryption_algorithm: str = Field(default="AES-256-GCM")
    pii_access_audit_enabled: bool = Field(default=True)
    log_pii_masking_enabled: bool = Field(default=True)
    ai_pii_access_restricted: bool = Field(
        default=True,
        description="If True, AI agents cannot access CONFIDENTIAL+ fields without explicit grant.",
    )
    data_minimization_enabled: bool = Field(default=True)
    default_retention_days: int = Field(default=2555)


# Registry of known PII fields across the HRMS domain
HRMS_PII_FIELDS: list[PIIField] = [
    # Employee
    PIIField(field_name="first_name", model_name="Employee", classification=PIIClassification.INTERNAL),
    PIIField(field_name="last_name", model_name="Employee", classification=PIIClassification.INTERNAL),
    PIIField(field_name="email", model_name="Employee", classification=PIIClassification.INTERNAL),
    PIIField(
        field_name="phone", model_name="Employee", classification=PIIClassification.CONFIDENTIAL, mask_pattern="***-***-****"
    ),
    PIIField(field_name="date_of_birth", model_name="Employee", classification=PIIClassification.SENSITIVE),
    PIIField(
        field_name="national_id", model_name="Employee", classification=PIIClassification.HIGHLY_SENSITIVE, encrypt_at_rest=True
    ),
    PIIField(
        field_name="bank_account_number",
        model_name="Employee",
        classification=PIIClassification.HIGHLY_SENSITIVE,
        encrypt_at_rest=True,
    ),
    PIIField(field_name="location", model_name="Employee", classification=PIIClassification.CONFIDENTIAL),
    # Payroll
    PIIField(
        field_name="gross_salary",
        model_name="PayrollRecord",
        classification=PIIClassification.HIGHLY_SENSITIVE,
        encrypt_at_rest=True,
    ),
    PIIField(
        field_name="net_salary",
        model_name="PayrollRecord",
        classification=PIIClassification.HIGHLY_SENSITIVE,
        encrypt_at_rest=True,
    ),
    PIIField(
        field_name="basic_salary",
        model_name="PayrollRecord",
        classification=PIIClassification.HIGHLY_SENSITIVE,
        encrypt_at_rest=True,
    ),
    # Performance
    PIIField(field_name="performance_rating", model_name="PerformanceReview", classification=PIIClassification.SENSITIVE),
]


def get_pii_fields_for_model(model_name: str) -> list[PIIField]:
    return [f for f in HRMS_PII_FIELDS if f.model_name == model_name]


def mask_value(value: Any, field: PIIField) -> str:
    """Return a masked representation of a PII field value."""
    if not field.must_be_masked_in_logs:
        return str(value)
    if field.mask_pattern:
        return field.mask_pattern
    return "[REDACTED]"
