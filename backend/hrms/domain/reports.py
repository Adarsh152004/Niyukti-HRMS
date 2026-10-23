"""
HRMS Domain — HRReportDefinition, HRReportExecution.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from backend.hrms.domain.common import HRMSBaseModel, generate_id, utc_now


class ReportCategory(StrEnum):
    HEADCOUNT = "HEADCOUNT"
    ATTRITION = "ATTRITION"
    PAYROLL = "PAYROLL"
    ATTENDANCE = "ATTENDANCE"
    LEAVE = "LEAVE"
    RECRUITMENT = "RECRUITMENT"
    COMPLIANCE = "COMPLIANCE"
    PERFORMANCE = "PERFORMANCE"


class ReportFormat(StrEnum):
    JSON = "JSON"
    CSV = "CSV"
    TABULAR = "TABULAR"
    PDF = "PDF"


class HRReportDefinition(HRMSBaseModel):
    """Declarative specification for an authoritative, deterministic HR report."""

    report_id: str = Field(default_factory=generate_id)
    organization_id: str
    title: str
    category: ReportCategory
    description: str = ""
    query_template: str
    required_parameters: list[str] = Field(default_factory=list)
    output_columns: list[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=utc_now)


class HRReportExecution(HRMSBaseModel):
    """Output record of a deterministic report generation run."""

    execution_id: str = Field(default_factory=generate_id)
    report_id: str
    organization_id: str
    requested_by: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    format: ReportFormat = ReportFormat.TABULAR
    total_records: int = 0
    records: list[dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)
