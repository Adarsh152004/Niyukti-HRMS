"""
Tests for Specialized Agent Capability Profiles and Prohibited Action Enforcement.
"""

from __future__ import annotations

import pytest

from backend.agents.specialized.application.specialization_service import SpecializedAgentService
from backend.agents.specialized.domain.enums import SpecializedAgentRole
from backend.agents.specialized.domain.exceptions import UnauthorizedCapabilityError


def test_explicit_capability_grant_and_denial():
    svc = SpecializedAgentService.get_instance()

    # Resume screening agent has resume:parse
    svc.verify_capability(SpecializedAgentRole.RESUME_SCREENING_AGENT, "resume:parse")
    svc.verify_capability(SpecializedAgentRole.RESUME_SCREENING_AGENT, "skills:extract")

    # Resume screening agent does NOT have payroll:read
    with pytest.raises(UnauthorizedCapabilityError):
        svc.verify_capability(SpecializedAgentRole.RESUME_SCREENING_AGENT, "payroll:read")


def test_high_impact_prohibited_capabilities_blocked():
    svc = SpecializedAgentService.get_instance()

    # Payroll assistant cannot modify salary
    with pytest.raises(UnauthorizedCapabilityError):
        svc.verify_capability(SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT, "salary:alter_unilateral")

    # Performance agent cannot approve promotion
    with pytest.raises(UnauthorizedCapabilityError):
        svc.verify_capability(SpecializedAgentRole.PERFORMANCE_AGENT, "promotion:approve_unilateral")

    # Employee assistant cannot view other employees' salaries
    with pytest.raises(UnauthorizedCapabilityError):
        svc.verify_capability(SpecializedAgentRole.EMPLOYEE_ASSISTANT_AGENT, "employee:read_other_salary")

    # Compliance agent cannot conceal violations
    with pytest.raises(UnauthorizedCapabilityError):
        svc.verify_capability(SpecializedAgentRole.COMPLIANCE_AGENT, "violation:conceal")
