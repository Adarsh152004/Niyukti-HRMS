"""
Tests for Supervisor Hierarchy, Subordinate Delegation, and Privilege Containment.
"""

from __future__ import annotations

import pytest

from backend.agents.specialized.application.specialization_service import SpecializedAgentService
from backend.agents.specialized.domain.enums import SpecializedAgentRole
from backend.agents.specialized.domain.exceptions import AgentPolicyViolationError


def test_supervisor_hierarchy_delegation_validation():
    svc = SpecializedAgentService.get_instance()

    # 1. Valid delegation: HR Manager -> Recruitment Agent
    svc.validate_delegation(
        supervisor_role=SpecializedAgentRole.HR_MANAGER_AGENT,
        subordinate_role=SpecializedAgentRole.RECRUITMENT_AGENT,
    )

    # 2. Valid multi-tier delegation: Executive -> Resume Screening (Executive is ancestor in hierarchy)
    svc.validate_delegation(
        supervisor_role=SpecializedAgentRole.EXECUTIVE_HR_AGENT,
        subordinate_role=SpecializedAgentRole.RESUME_SCREENING_AGENT,
    )

    # 3. Invalid delegation: Resume Screening cannot supervise Executive HR Agent (Privilege escalation)
    with pytest.raises(AgentPolicyViolationError):
        svc.validate_delegation(
            supervisor_role=SpecializedAgentRole.RESUME_SCREENING_AGENT,
            subordinate_role=SpecializedAgentRole.EXECUTIVE_HR_AGENT,
        )

    # 4. Peer agents without supervisory relationship cannot delegate across trees
    with pytest.raises(AgentPolicyViolationError):
        svc.validate_delegation(
            supervisor_role=SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT,
            subordinate_role=SpecializedAgentRole.CANDIDATE_RANKING_AGENT,
        )
