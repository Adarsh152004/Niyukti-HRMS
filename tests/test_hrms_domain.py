"""Tests — HRMS Domain models (instantiation and field validation)."""

from datetime import date


def test_organization_instantiation():
    from backend.hrms.domain.organization import Organization

    org = Organization(legal_name="Acme Corporation Pvt Ltd", display_name="Acme Corp", slug="acme-corp")
    assert org.organization_id is not None
    assert org.country == "IN"
    assert org.currency == "INR"
    assert org.is_active is True


def test_department_instantiation():
    from backend.hrms.domain.organization import Department

    dept = Department(organization_id="org-001", name="Engineering", code="ENG")
    assert dept.department_id is not None
    assert dept.is_active is True


def test_designation_instantiation():
    from backend.hrms.domain.organization import Designation

    des = Designation(organization_id="org-001", name="Senior Software Engineer", code="SSE", level=3)
    assert des.designation_id is not None
    assert des.is_managerial is False


def test_employee_instantiation():
    from backend.hrms.domain.common import EmploymentType
    from backend.hrms.domain.employee import Employee

    emp = Employee(
        organization_id="org-001",
        employee_code="EMP-001",
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@company.com",
        department_id="dept-001",
        designation_id="des-001",
        employment_type=EmploymentType.FULL_TIME,
        joining_date=date(2022, 6, 1),
    )
    assert emp.employee_id is not None
    assert emp.is_active is True


def test_job_instantiation():
    from backend.hrms.domain.common import JobStatus
    from backend.hrms.domain.recruitment import Job

    job = Job(
        organization_id="org-001",
        department_id="dept-001",
        title="Senior React Developer",
        description="We are looking for a senior React developer.",
        status=JobStatus.OPEN,
        posted_by="hr-001",
    )
    assert job.job_id is not None
    assert job.ai_screening_enabled is True


def test_leave_request_instantiation():
    from backend.hrms.domain.common import LeaveStatus, LeaveType
    from backend.hrms.domain.leave import LeaveRequest

    leave = LeaveRequest(
        employee_id="emp-001",
        organization_id="org-001",
        leave_type=LeaveType.ANNUAL,
        start_date=date(2024, 3, 18),
        end_date=date(2024, 3, 20),
        total_days=3.0,
    )
    assert leave.leave_id is not None
    assert leave.status == LeaveStatus.PENDING


def test_payroll_record_instantiation():
    from backend.hrms.domain.payroll import PayrollRecord, PayrollStatus

    pr = PayrollRecord(
        employee_id="emp-001",
        organization_id="org-001",
        payroll_period="2024-01",
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        gross_salary=100000.0,
        basic_salary=60000.0,
        net_salary=85000.0,
    )
    assert pr.payroll_id is not None
    assert pr.status == PayrollStatus.DRAFT
    assert pr.approval_request_id is None


def test_payroll_requires_approval_field():
    """PayrollRecord must have approval_request_id field for governance tracking."""
    from backend.hrms.domain.payroll import PayrollRecord

    fields = PayrollRecord.model_fields
    assert "approval_request_id" in fields


def test_agent_roster_completeness():
    from backend.hrms.agents.roster import HRAgentRole

    roles = [r.value for r in HRAgentRole]
    assert len(roles) == 24

    assert "RESUME_SCREENING_AGENT" in roles
    assert "CANDIDATE_RANKING_AGENT" in roles
    assert "ATTRITION_PREDICTION_AGENT" in roles
    assert "PAYROLL_AGENT" in roles
    assert "EMPLOYEE_HR_ASSISTANT" in roles
    assert "AUDIT_AGENT" in roles


def test_performance_review_has_ai_prediction_field():
    """PerformanceReview must support AI-predicted ratings for explainability."""
    from backend.hrms.domain.performance import PerformanceReview

    fields = PerformanceReview.model_fields
    assert "ai_predicted_rating" in fields
    assert "ai_prediction_decision_id" in fields


def test_candidate_has_ai_fields():
    """Candidate must link to AIDecision for screening explainability."""
    from backend.hrms.domain.recruitment import Candidate

    fields = Candidate.model_fields
    assert "ai_score" in fields
    assert "ai_screening_decision_id" in fields
