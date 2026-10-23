"""
Tests — HR Domain Imports.

Verifies that all HRMS domain modules import successfully
and that the expected entity types are accessible.
"""


def test_organization_imports():
    from backend.hrms.domain.organization import Department, Designation, Organization

    assert Organization is not None
    assert Department is not None
    assert Designation is not None


def test_employee_imports():
    from backend.hrms.domain.employee import Employee, EmployeeDocument, EmploymentHistory

    assert Employee is not None
    assert EmployeeDocument is not None
    assert EmploymentHistory is not None


def test_skills_imports():
    from backend.hrms.domain.skills import EmployeeSkill, Skill

    assert Skill is not None
    assert EmployeeSkill is not None


def test_recruitment_imports():
    from backend.hrms.domain.recruitment import Candidate, Interview, Job, JobApplication

    assert Job is not None
    assert JobApplication is not None
    assert Candidate is not None
    assert Interview is not None


def test_attendance_imports():
    from backend.hrms.domain.attendance import AttendanceRecord, Holiday, Shift

    assert AttendanceRecord is not None
    assert Shift is not None
    assert Holiday is not None


def test_leave_imports():
    from backend.hrms.domain.leave import LeaveRequest

    assert LeaveRequest is not None


def test_payroll_imports():
    from backend.hrms.domain.payroll import Bonus, Deduction, PayrollRecord, SalaryComponent

    assert PayrollRecord is not None
    assert SalaryComponent is not None
    assert Bonus is not None
    assert Deduction is not None


def test_performance_imports():
    from backend.hrms.domain.performance import KPI, PerformanceGoal, PerformanceReview

    assert PerformanceGoal is not None
    assert KPI is not None
    assert PerformanceReview is not None


def test_learning_imports():
    from backend.hrms.domain.learning import (
        CareerPlan,
        Certification,
        TrainingEnrollment,
        TrainingProgram,
    )

    assert TrainingProgram is not None
    assert TrainingEnrollment is not None
    assert Certification is not None
    assert CareerPlan is not None


def test_feedback_imports():
    from backend.hrms.domain.feedback import EmployeeSentiment, Feedback, Survey

    assert Survey is not None
    assert Feedback is not None
    assert EmployeeSentiment is not None


def test_policy_imports():
    from backend.hrms.domain.policy import HRPolicy

    assert HRPolicy is not None


def test_notifications_imports():
    from backend.hrms.domain.notifications import Notification

    assert Notification is not None


def test_common_imports():
    from backend.hrms.domain.common import (
        EmploymentStatus,
        HRMSBaseModel,
    )

    assert EmploymentStatus is not None
    assert HRMSBaseModel is not None


def test_agent_roster_imports():
    from backend.hrms.agents.roster import HRAgentRole

    assert HRAgentRole is not None


def test_no_startup_incubator_domain():
    """Verify that no startup-incubator domain concepts are exposed through HRMS API."""
    import backend.hrms.domain as domain_module

    # These attributes must not exist in the HRMS domain namespace
    forbidden_names = [
        "startup",
        "venture",
        "investor",
        "incubator",
        "branding",
        "market_research",
    ]
    domain_attrs = dir(domain_module)
    for name in forbidden_names:
        assert name not in domain_attrs, f"Startup-incubator concept '{name}' found in HRMS domain namespace"
