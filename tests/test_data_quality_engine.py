"""
Tests for HR Data Quality Engine.
"""

from __future__ import annotations

from datetime import date

from backend.hrms.domain.employee import Employee, EmploymentStatus, EmploymentType, Gender
from backend.hrms.quality.engine import DataQualityEngine
from backend.hrms.quality.models import QualityRuleType


def test_data_quality_engine_detection():
    engine = DataQualityEngine.get_instance()
    org_id = "org-test-quality"

    # Create test employee records with deliberate anomalies:
    # 1. Emp1: Valid
    # 2. Emp2: Missing/invalid email
    # 3. Emp3: Duplicate email with Emp1
    # 4. Emp4: Circular manager hierarchy with Emp5

    emp1 = Employee(
        employee_id="emp-1",
        organization_id=org_id,
        employee_code="EMP-001",
        department_id="dept-1",
        designation_id="desig-1",
        first_name="Alice",
        last_name="Smith",
        email="alice@company.com",
        gender=Gender.FEMALE,
        employment_status=EmploymentStatus.ACTIVE,
        employment_type=EmploymentType.FULL_TIME,
        joining_date=date(2023, 1, 15),
    )

    emp2 = Employee(
        employee_id="emp-2",
        organization_id=org_id,
        employee_code="EMP-002",
        department_id="dept-1",
        designation_id="desig-1",
        first_name="Bob",
        last_name="Jones",
        email="invalid-email-string",
        gender=Gender.MALE,
        employment_status=EmploymentStatus.ACTIVE,
        employment_type=EmploymentType.FULL_TIME,
        joining_date=date(2023, 3, 1),
    )

    emp3 = Employee(
        employee_id="emp-3",
        organization_id=org_id,
        employee_code="EMP-003",
        department_id="dept-1",
        designation_id="desig-1",
        first_name="Charlie",
        last_name="Brown",
        email="alice@company.com",  # Duplicate with Alice
        gender=Gender.MALE,
        employment_status=EmploymentStatus.ACTIVE,
        employment_type=EmploymentType.FULL_TIME,
        joining_date=date(2023, 4, 1),
    )

    emp4 = Employee(
        employee_id="emp-4",
        organization_id=org_id,
        employee_code="EMP-004",
        department_id="dept-1",
        designation_id="desig-1",
        first_name="David",
        last_name="Miller",
        email="david@company.com",
        gender=Gender.MALE,
        employment_status=EmploymentStatus.ACTIVE,
        employment_type=EmploymentType.FULL_TIME,
        joining_date=date(2023, 5, 1),
        manager_id="emp-5",
    )

    emp5 = Employee(
        employee_id="emp-5",
        organization_id=org_id,
        employee_code="EMP-005",
        department_id="dept-1",
        designation_id="desig-1",
        first_name="Eve",
        last_name="Wilson",
        email="eve@company.com",
        gender=Gender.FEMALE,
        employment_status=EmploymentStatus.ACTIVE,
        employment_type=EmploymentType.FULL_TIME,
        joining_date=date(2023, 6, 1),
        manager_id="emp-4",  # Cycle: emp-4 -> emp-5 -> emp-4
    )

    employees = [emp1, emp2, emp3, emp4, emp5]
    report = engine.generate_health_report(org_id, employees)

    assert report.total_records_scanned == 5
    assert report.total_issues_found >= 3
    assert report.critical_issues_count >= 2  # Duplicate email + hierarchy cycle

    rule_types = {issue.rule_type for issue in report.issues}
    assert QualityRuleType.MISSING_REQUIRED_FIELD in rule_types
    assert QualityRuleType.DUPLICATE_ENTITY in rule_types
    assert QualityRuleType.HIERARCHY_CYCLE in rule_types
    assert report.overall_health_score < 80.0
