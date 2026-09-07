"""
AI-Powered Intelligent HRMS — Database & Repository Seeding Engine.

Coordinates deterministic synthetic data generation and persistence across:
- Organizations, Departments, Salary Bands
- Employees, Reporting DAGs, Skills
- Daily Attendance & Biometrics, Leave Policies & Ledgers
- Deterministic Monthly Payroll Runs & Payslips
- Job Openings, Candidate Pipeline, Performance Review Cycles
- AI Agent Fleet Telemetry, HITL Approvals, Cryptographic Audit Logs
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from backend.database.seeder.generators.agent_governance_generator import (
    SyntheticAgentFleetItem,
    SyntheticAuditLog,
    SyntheticHITLApproval,
    generate_agents_and_governance,
)
from backend.database.seeder.generators.attendance_leave_generator import (
    SyntheticAttendanceRecord,
    SyntheticLeavePolicy,
    SyntheticLeaveRequest,
    generate_attendance_and_leave,
)
from backend.database.seeder.generators.employee_generator import (
    SyntheticEmployee,
    generate_employees,
)
from backend.database.seeder.generators.org_generator import (
    SyntheticOrgData,
    generate_organization_structure,
)
from backend.database.seeder.generators.payroll_generator import (
    SyntheticPayrollRun,
    generate_payroll_runs,
)
from backend.database.seeder.generators.recruitment_perf_generator import (
    SyntheticJobOpening,
    SyntheticPerformanceReview,
    generate_recruitment_and_performance,
)

logger = logging.getLogger(__name__)


@dataclass
class SeedResult:
    """Statistical summary of database seeding execution."""

    organization_id: str
    employee_count: int
    department_count: int
    attendance_records_count: int
    leave_requests_count: int
    payroll_runs_count: int
    payslips_count: int
    jobs_count: int
    candidates_count: int
    reviews_count: int
    agents_count: int
    approvals_count: int
    audit_logs_count: int
    duration_seconds: float


class DatabaseSeeder:
    """Central synthetic enterprise database seeding coordinator."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed

    def generate_all(
        self,
        scale: str = "medium",
        organization_id: str = "org-apex-01",
        legal_name: str = "Apex Technologies Global Inc.",
    ) -> dict[str, Any]:
        """
        Generates full synthetic enterprise graph in memory.
        Scale options:
        - 'small': 20 employees
        - 'medium': 60 employees
        - 'large': 250 employees
        """
        start_time = time.time()
        emp_target = 20 if scale == "small" else 250 if scale == "large" else 60

        # 1. Organization & Departments
        org_data = generate_organization_structure(
            organization_id=organization_id, legal_name=legal_name, seed=self.seed
        )

        # 2. Employees & Reporting DAG
        employees = generate_employees(org_data=org_data, count=emp_target, seed=self.seed)

        # 3. Attendance & Leave Ledgers
        attendance, leave_policies, leave_requests = generate_attendance_and_leave(
            employees=employees, days_history=30, seed=self.seed
        )

        # 4. Deterministic Payroll
        payroll_runs = generate_payroll_runs(employees=employees, months_count=3, seed=self.seed)

        # 5. Recruitment & Performance
        jobs, reviews = generate_recruitment_and_performance(
            org_data=org_data, employees=employees, seed=self.seed
        )

        # 6. Agents, Approvals & Audit Trail
        agents, approvals, audit_logs = generate_agents_and_governance(
            org_data=org_data, employees=employees, seed=self.seed
        )

        duration = time.time() - start_time
        payslip_count = sum(len(p.payslips) for p in payroll_runs)
        candidate_count = sum(len(j.candidates) for j in jobs)

        summary = SeedResult(
            organization_id=organization_id,
            employee_count=len(employees),
            department_count=len(org_data.departments),
            attendance_records_count=len(attendance),
            leave_requests_count=len(leave_requests),
            payroll_runs_count=len(payroll_runs),
            payslips_count=payslip_count,
            jobs_count=len(jobs),
            candidates_count=candidate_count,
            reviews_count=len(reviews),
            agents_count=len(agents),
            approvals_count=len(approvals),
            audit_logs_count=len(audit_logs),
            duration_seconds=round(duration, 3),
        )

        return {
            "summary": summary,
            "org_data": org_data,
            "employees": employees,
            "attendance": attendance,
            "leave_policies": leave_policies,
            "leave_requests": leave_requests,
            "payroll_runs": payroll_runs,
            "jobs": jobs,
            "reviews": reviews,
            "agents": agents,
            "approvals": approvals,
            "audit_logs": audit_logs,
        }
