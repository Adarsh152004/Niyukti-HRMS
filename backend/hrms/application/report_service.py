"""
Reporting Application Service — Deterministic tabular HR reports and workforce metrics computation.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from backend.hrms.application.services import BaseApplicationService
from backend.hrms.domain.reports import HRReportDefinition, HRReportExecution, ReportCategory, ReportFormat
from backend.hrms.ports.repositories import EmployeeRepository, ReportRepository


class ReportingService(BaseApplicationService):
    """Deterministic reporting engine for headcount, retention, and departmental metrics."""

    def __init__(self, report_repo: ReportRepository, employee_repo: EmployeeRepository) -> None:
        super().__init__()
        self.repo = report_repo
        self.emp_repo = employee_repo

    async def create_definition(
        self,
        organization_id: str,
        title: str,
        category: ReportCategory,
        query_template: str,
        output_columns: list[str],
        description: str = "",
    ) -> HRReportDefinition:
        definition = HRReportDefinition(
            organization_id=organization_id,
            title=title,
            category=category,
            query_template=query_template,
            output_columns=output_columns,
            description=description,
        )
        return await self.repo.create_definition(definition)

    async def execute_headcount_report(
        self,
        organization_id: str,
        requested_by: str,
        report_id: str = "rep-headcount-default",
    ) -> HRReportExecution:
        """Deterministically aggregate active employees and departmental headcount."""
        employees = await self.emp_repo.list_by_organization(organization_id)
        records: list[dict[str, Any]] = []

        for emp in employees:
            records.append(
                {
                    "employee_id": emp.employee_id,
                    "employee_code": emp.employee_code,
                    "full_name": f"{emp.first_name} {emp.last_name}",
                    "department_id": emp.department_id,
                    "designation_id": emp.designation_id,
                    "employment_status": emp.employment_status.value,
                }
            )

        execution = HRReportExecution(
            report_id=report_id,
            organization_id=organization_id,
            requested_by=requested_by,
            format=ReportFormat.TABULAR,
            total_records=len(records),
            records=records,
        )
        return await self.repo.record_execution(execution)

    async def list_definitions(self, organization_id: str) -> Sequence[HRReportDefinition]:
        return await self.repo.list_definitions(organization_id)
