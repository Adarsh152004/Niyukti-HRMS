"""
Security Tests — Employee State Machine Transitions.

Critical Requirement:
TEST 6: Invalid employee state transition fails.
"""

from datetime import date

import pytest

from backend.hrms.domain.employee import Employee, EmploymentStatus, validate_status_transition
from backend.hrms.domain.exceptions import InvalidEmployeeState


def test_valid_employee_status_transitions():
    """Verify legal status transition paths."""
    # ACTIVE -> ON_LEAVE -> ACTIVE
    validate_status_transition(EmploymentStatus.ACTIVE, EmploymentStatus.ON_LEAVE)
    validate_status_transition(EmploymentStatus.ON_LEAVE, EmploymentStatus.ACTIVE)

    # ACTIVE -> SUSPENDED -> ACTIVE
    validate_status_transition(EmploymentStatus.ACTIVE, EmploymentStatus.SUSPENDED)
    validate_status_transition(EmploymentStatus.SUSPENDED, EmploymentStatus.ACTIVE)

    # ACTIVE -> RESIGNED -> TERMINATED
    validate_status_transition(EmploymentStatus.ACTIVE, EmploymentStatus.RESIGNED)
    validate_status_transition(EmploymentStatus.RESIGNED, EmploymentStatus.TERMINATED)


def test_invalid_employee_status_transitions():
    """TEST 6: Invalid employee state transitions fail."""
    # TERMINATED -> ACTIVE (Prohibited terminal state transition)
    with pytest.raises(InvalidEmployeeState):
        validate_status_transition(EmploymentStatus.TERMINATED, EmploymentStatus.ACTIVE)

    # RETIRED -> ACTIVE (Prohibited terminal state transition)
    with pytest.raises(InvalidEmployeeState):
        validate_status_transition(EmploymentStatus.RETIRED, EmploymentStatus.ACTIVE)

    # TERMINATED -> ON_LEAVE (Prohibited)
    with pytest.raises(InvalidEmployeeState):
        validate_status_transition(EmploymentStatus.TERMINATED, EmploymentStatus.ON_LEAVE)


def test_employee_domain_model_transition_method():
    """Test transition_status method on Employee entity."""
    emp = Employee(
        organization_id="org-A",
        employee_code="EMP-100",
        first_name="Jane",
        last_name="Doe",
        email="jane@orga.com",
        department_id="dept-1",
        designation_id="des-1",
        joining_date=date(2024, 1, 1),
    )

    # Valid transition to ON_LEAVE
    emp.transition_status(EmploymentStatus.ON_LEAVE)
    assert emp.employment_status == EmploymentStatus.ON_LEAVE

    # Valid transition back to ACTIVE
    emp.transition_status(EmploymentStatus.ACTIVE)
    assert emp.employment_status == EmploymentStatus.ACTIVE

    # Valid transition to TERMINATED sets exit_date automatically
    emp.transition_status(EmploymentStatus.TERMINATED)
    assert emp.employment_status == EmploymentStatus.TERMINATED
    assert emp.exit_date is not None

    # Invalid transition from TERMINATED to ACTIVE raises InvalidEmployeeState
    with pytest.raises(InvalidEmployeeState):
        emp.transition_status(EmploymentStatus.ACTIVE)
