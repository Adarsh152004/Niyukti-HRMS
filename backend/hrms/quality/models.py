"""
Data Quality Domain Models — Issues, severity, and report containers.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class QualitySeverity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class QualityRuleType(StrEnum):
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INCONSISTENT_DATE = "INCONSISTENT_DATE"
    HIERARCHY_CYCLE = "HIERARCHY_CYCLE"
    DUPLICATE_ENTITY = "DUPLICATE_ENTITY"
    ORPHAN_RECORD = "ORPHAN_RECORD"
    INVALID_BALANCE = "INVALID_BALANCE"
    IMPOSSIBLE_ATTENDANCE = "IMPOSSIBLE_ATTENDANCE"


class DataQualityIssue(BaseModel):
    """Specific detected data quality discrepancy."""

    issue_id: str = Field(default_factory=lambda: f"dqi-{uuid.uuid4()}")
    organization_id: str
    rule_type: QualityRuleType
    entity_type: str
    entity_id: str
    severity: QualitySeverity
    field_name: str | None = None
    description: str
    suggested_fix: str | None = None
    detected_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class DataQualityReport(BaseModel):
    """Aggregated organization data health score and findings."""

    report_id: str = Field(default_factory=lambda: f"dqr-{uuid.uuid4()}")
    organization_id: str
    overall_health_score: float = Field(ge=0.0, le=100.0, description="0-100 data health score")
    total_records_scanned: int = Field(ge=0)
    total_issues_found: int = Field(ge=0)
    critical_issues_count: int = Field(ge=0)
    issues: Sequence[DataQualityIssue] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
