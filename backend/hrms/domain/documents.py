"""
HRMS Domain — Employee Document metadata.

Manages metadata and verification status of employee documents.
Storage reference points to an abstract storage port key.
No document files or OCR logic are implemented in this domain layer.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import Field

from backend.hrms.domain.common import HRMSBaseModel, generate_id, utc_now


class DocumentType(StrEnum):
    """Extensible document categories."""

    RESUME = "RESUME"
    ID_DOCUMENT = "ID_DOCUMENT"
    EDUCATION_CERTIFICATE = "EDUCATION_CERTIFICATE"
    PROFESSIONAL_CERTIFICATION = "PROFESSIONAL_CERTIFICATION"
    OFFER_LETTER = "OFFER_LETTER"
    CONTRACT = "CONTRACT"
    PAYSLIP = "PAYSLIP"
    OTHER = "OTHER"


class VerificationStatus(StrEnum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class EmployeeDocument(HRMSBaseModel):
    """
    Metadata record for an employee document.
    """

    document_id: str = Field(default_factory=generate_id)
    organization_id: str = Field(description="Tenant ID boundary")
    employee_id: str
    document_type: DocumentType = Field(default=DocumentType.OTHER)
    document_name: str
    storage_reference: str = Field(description="Opaque reference key in StorageAdapter")
    mime_type: str = Field(default="application/pdf")
    size: int = Field(ge=0, description="Size in bytes")
    checksum: str | None = Field(default=None, description="SHA-256 checksum for integrity")
    verification_status: VerificationStatus = Field(default=VerificationStatus.UNVERIFIED)

    uploaded_at: datetime = Field(default_factory=utc_now)
    verified_at: datetime | None = Field(default=None)
    verified_by: str | None = Field(default=None, description="Actor ID who verified")
    expires_at: date | None = Field(default=None)

    @property
    def id(self) -> str:
        return self.document_id

    @property
    def is_verified(self) -> bool:
        return self.verification_status == VerificationStatus.VERIFIED
