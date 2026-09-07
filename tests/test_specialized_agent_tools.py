"""
Tests for Agent Tool Access Policies and Server-Side Tool Execution Boundaries.
"""

from __future__ import annotations

import pytest

from backend.agents.specialized.application.specialization_service import SpecializedAgentService
from backend.agents.specialized.domain.enums import SpecializedAgentRole, ToolAccessLevel
from backend.agents.specialized.domain.exceptions import ProhibitedToolExecutionError


def test_tool_access_levels_allow_deny_approval():
    svc = SpecializedAgentService.get_instance()

    # 1. ALLOW
    lvl_allow = svc.verify_tool_access(SpecializedAgentRole.RESUME_SCREENING_AGENT, "resume.parse")
    assert lvl_allow == ToolAccessLevel.ALLOW

    # 2. REQUIRES_APPROVAL
    lvl_appr = svc.verify_tool_access(SpecializedAgentRole.RECRUITMENT_AGENT, "candidate.reject")
    assert lvl_appr == ToolAccessLevel.REQUIRES_APPROVAL

    # 3. DENY (Explicitly prohibited)
    with pytest.raises(ProhibitedToolExecutionError):
        svc.verify_tool_access(SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT, "payroll.update_salary")

    # 4. DENY (Undeclared tool)
    with pytest.raises(ProhibitedToolExecutionError):
        svc.verify_tool_access(SpecializedAgentRole.NOTIFICATION_AGENT, "database.drop_all_tables")
