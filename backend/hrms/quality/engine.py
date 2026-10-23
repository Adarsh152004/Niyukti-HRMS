"""
Data Quality Engine — Scans domain records and produces diagnostic health reports and anomaly fixes.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from datetime import date

from backend.hrms.domain.employee import Employee
from backend.hrms.quality.models import (
    DataQualityIssue,
    DataQualityReport,
    QualityRuleType,
    QualitySeverity,
)

logger = logging.getLogger(__name__)


class DataQualityEngine:
    """Validator scanning core HRMS domain entities for consistency and correctness."""

    _instance: DataQualityEngine | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    @classmethod
    def get_instance(cls) -> DataQualityEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def audit_employees(
        self,
        organization_id: str,
        employees: Sequence[Employee],
    ) -> list[DataQualityIssue]:
        """Scan a list of employee records for anomalies and quality defects."""
        issues: list[DataQualityIssue] = []
        seen_emails: dict[str, str] = {}
        manager_map: dict[str, str] = {}

        for emp in employees:
            if emp.organization_id != organization_id:
                continue

            # 1. Missing vital fields
            if not emp.email or "@" not in emp.email:
                issues.append(
                    DataQualityIssue(
                        organization_id=organization_id,
                        rule_type=QualityRuleType.MISSING_REQUIRED_FIELD,
                        entity_type="employee",
                        entity_id=emp.employee_id,
                        severity=QualitySeverity.HIGH,
                        field_name="email",
                        description=f"Employee '{emp.first_name} {emp.last_name}' has invalid or missing email.",
                        suggested_fix="Update with valid corporate email address.",
                    )
                )

            # 2. Duplicate emails
            if emp.email:
                lower_email = emp.email.lower()
                if lower_email in seen_emails:
                    issues.append(
                        DataQualityIssue(
                            organization_id=organization_id,
                            rule_type=QualityRuleType.DUPLICATE_ENTITY,
                            entity_type="employee",
                            entity_id=emp.employee_id,
                            severity=QualitySeverity.CRITICAL,
                            field_name="email",
                            description=f"Duplicate email '{emp.email}' shared with employee '{seen_emails[lower_email]}'.",
                            suggested_fix="Ensure each employee has a unique email address.",
                        )
                    )
                else:
                    seen_emails[lower_email] = emp.employee_id

            # 3. Inconsistent hire date
            if emp.joining_date and emp.joining_date > date.today() and emp.employment_status.value == "ACTIVE":
                issues.append(
                    DataQualityIssue(
                        organization_id=organization_id,
                        rule_type=QualityRuleType.INCONSISTENT_DATE,
                        entity_type="employee",
                        entity_id=emp.employee_id,
                        severity=QualitySeverity.MEDIUM,
                        field_name="joining_date",
                        description=f"Employee status is ACTIVE but joining date '{emp.joining_date}' is in the future.",
                        suggested_fix="Change status to PENDING_ONBOARDING or adjust joining date.",
                    )
                )

            if emp.manager_id:
                manager_map[emp.employee_id] = emp.manager_id

        # 4. Check for cycles in manager hierarchy
        for emp_id, mgr_id in manager_map.items():
            visited = {emp_id}
            curr = mgr_id
            while curr in manager_map:
                if curr in visited:
                    issues.append(
                        DataQualityIssue(
                            organization_id=organization_id,
                            rule_type=QualityRuleType.HIERARCHY_CYCLE,
                            entity_type="employee",
                            entity_id=emp_id,
                            severity=QualitySeverity.CRITICAL,
                            field_name="manager_id",
                            description=f"Circular reporting hierarchy detected involving employee '{emp_id}'.",
                            suggested_fix="Break reporting cycle by reassigning manager.",
                        )
                    )
                    break
                visited.add(curr)
                curr = manager_map[curr]

        return issues

    def generate_health_report(
        self,
        organization_id: str,
        employees: Sequence[Employee],
    ) -> DataQualityReport:
        """Run full quality audit and compile health score."""
        issues = self.audit_employees(organization_id, employees)
        total_scanned = len(employees)

        critical_count = sum(1 for i in issues if i.severity == QualitySeverity.CRITICAL)
        high_count = sum(1 for i in issues if i.severity == QualitySeverity.HIGH)
        med_count = sum(1 for i in issues if i.severity == QualitySeverity.MEDIUM)

        # Deduct penalties from base score 100
        penalties = (critical_count * 20.0) + (high_count * 10.0) + (med_count * 5.0)
        score = max(0.0, min(100.0, round(100.0 - penalties, 1)))

        return DataQualityReport(
            organization_id=organization_id,
            overall_health_score=score,
            total_records_scanned=total_scanned,
            total_issues_found=len(issues),
            critical_issues_count=critical_count,
            issues=issues,
        )
