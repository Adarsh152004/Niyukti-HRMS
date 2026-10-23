"""
Tests for Security Invariants, Least Privilege, and CommandBus Boundary Enforcement.
"""

from __future__ import annotations

import pytest

from backend.agents.specialized.application.specialization_service import SpecializedAgentService
from backend.agents.specialized.domain.enums import SpecializedAgentRole
from backend.agents.specialized.domain.exceptions import (
    ProhibitedToolExecutionError,
)


def test_ai_agent_cannot_gain_unauthorized_authority():
    svc = SpecializedAgentService.get_instance()

    # Invariant: AI Agent cannot grant itself employee termination authority
    for defn in svc.list_definitions():
        assert not defn.capability_profile.has_capability("employee:terminate")
        assert not defn.capability_profile.has_capability("salary:update")

    # Invariant: AI Agent cannot directly modify payroll balances
    assert "salary:alter_unilateral" in svc.get_capabilities(SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT).prohibited_capabilities


def test_employee_assistant_strict_isolation():
    svc = SpecializedAgentService.get_instance()
    caps = svc.get_capabilities(SpecializedAgentRole.EMPLOYEE_ASSISTANT_AGENT)

    # Employee assistant can read own leave/payslip, but strictly prohibited from reading other employees' data
    assert "leave:read_own" in caps.capabilities
    assert "payslip:explain_own" in caps.capabilities
    assert "employee:read_other_salary" in caps.prohibited_capabilities
    assert "employee:read_other_confidential" in caps.prohibited_capabilities


def test_prohibited_tools_instantly_rejected():
    svc = SpecializedAgentService.get_instance()

    # Even if LLM generates a tool call for payroll.update_salary, tool policy blocks it
    with pytest.raises(ProhibitedToolExecutionError):
        svc.verify_tool_access(SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT, "payroll.update_salary")
