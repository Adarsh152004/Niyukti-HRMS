"""
Data Retention, Archival & Legal Hold Engine.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RetentionCategory(StrEnum):
    EMPLOYEE_RECORD = "EMPLOYEE_RECORD"
    PAYROLL_RECORD = "PAYROLL_RECORD"
    CANDIDATE_RESUME = "CANDIDATE_RESUME"
    AUDIT_LOG = "AUDIT_LOG"
    AI_CONVERSATION = "AI_CONVERSATION"
    PERFORMANCE_REVIEW = "PERFORMANCE_REVIEW"


class ArchivalStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
    LEGAL_HOLD = "LEGAL_HOLD"
    ELIGIBLE_FOR_PURGE = "ELIGIBLE_FOR_PURGE"
    PURGED = "PURGED"


class RetentionPolicy(BaseModel):
    """Defines statutory and corporate retention periods."""

    category: RetentionCategory
    retention_days: int
    archive_after_days: int
    requires_approval_to_purge: bool = Field(default=True)


class RetentionRecord(BaseModel):
    """Tracks archival and legal hold state for a specific resource."""

    record_id: str
    organization_id: str
    category: RetentionCategory
    resource_id: str
    status: ArchivalStatus = Field(default=ArchivalStatus.ACTIVE)
    legal_hold_reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    archived_at: datetime | None = None
    purged_at: datetime | None = None


class DataRetentionEngine:
    """Engine managing lifecycle transitions, legal holds, and data minimization."""

    _instance: DataRetentionEngine | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._records: dict[str, RetentionRecord] = {}
        self._policies: dict[RetentionCategory, RetentionPolicy] = {
            RetentionCategory.CANDIDATE_RESUME: RetentionPolicy(
                category=RetentionCategory.CANDIDATE_RESUME, retention_days=180, archive_after_days=90
            ),
            RetentionCategory.AI_CONVERSATION: RetentionPolicy(
                category=RetentionCategory.AI_CONVERSATION, retention_days=365, archive_after_days=90
            ),
            RetentionCategory.PAYROLL_RECORD: RetentionPolicy(
                category=RetentionCategory.PAYROLL_RECORD, retention_days=2555, archive_after_days=365
            ),  # 7 years
            RetentionCategory.EMPLOYEE_RECORD: RetentionPolicy(
                category=RetentionCategory.EMPLOYEE_RECORD, retention_days=2555, archive_after_days=365
            ),
        }

    @classmethod
    def get_instance(cls) -> DataRetentionEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def register_record(
        self,
        organization_id: str,
        category: RetentionCategory,
        resource_id: str,
    ) -> RetentionRecord:
        """Register resource under retention tracking."""
        key = f"{organization_id}:{category.value}:{resource_id}"
        record = RetentionRecord(
            record_id=key,
            organization_id=organization_id,
            category=category,
            resource_id=resource_id,
        )
        async with self._lock:
            self._records[key] = record
            return record

    async def apply_legal_hold(
        self,
        organization_id: str,
        category: RetentionCategory,
        resource_id: str,
        reason: str,
    ) -> RetentionRecord:
        """Place record on legal hold, blocking any deletion or purging."""
        key = f"{organization_id}:{category.value}:{resource_id}"
        async with self._lock:
            record = self._records.get(key)
            if not record:
                record = await self.register_record(organization_id, category, resource_id)
            record.status = ArchivalStatus.LEGAL_HOLD
            record.legal_hold_reason = reason
            logger.warning(f"Applied LEGAL HOLD on [{key}]: {reason}")
            return record

    async def release_legal_hold(
        self,
        organization_id: str,
        category: RetentionCategory,
        resource_id: str,
    ) -> RetentionRecord:
        """Release legal hold back to active or archived status."""
        key = f"{organization_id}:{category.value}:{resource_id}"
        async with self._lock:
            record = self._records.get(key)
            if not record:
                raise ValueError(f"Retention record '{key}' not found.")
            record.status = ArchivalStatus.ARCHIVED if record.archived_at else ArchivalStatus.ACTIVE
            record.legal_hold_reason = None
            logger.info(f"Released legal hold on [{key}]")
            return record

    async def evaluate_retention_lifecycle(self, organization_id: str) -> list[RetentionRecord]:
        """
        Evaluate age of records against retention policies.
        Transitions eligible records to ARCHIVED or ELIGIBLE_FOR_PURGE unless on LEGAL_HOLD.
        """
        now = datetime.now(tz=UTC)
        updated: list[RetentionRecord] = []

        async with self._lock:
            for record in self._records.values():
                if record.organization_id != organization_id:
                    continue
                if record.status == ArchivalStatus.LEGAL_HOLD or record.status == ArchivalStatus.PURGED:
                    continue

                policy = self._policies.get(record.category)
                if not policy:
                    continue

                age_days = (now - record.created_at).days

                # Check archival eligibility
                if age_days >= policy.archive_after_days and record.status == ArchivalStatus.ACTIVE:
                    record.status = ArchivalStatus.ARCHIVED
                    record.archived_at = now
                    updated.append(record)
                    logger.info(f"Archived resource [{record.record_id}]")

                # Check purge eligibility
                elif age_days >= policy.retention_days and record.status == ArchivalStatus.ARCHIVED:
                    record.status = ArchivalStatus.ELIGIBLE_FOR_PURGE
                    updated.append(record)
                    logger.info(f"Resource [{record.record_id}] is now ELIGIBLE_FOR_PURGE")

        return updated
