"""
Tests for Memory Tier Scoping and Partitioning across Specialized Agents.
"""

from __future__ import annotations

import pytest

from backend.agents.memory.hierarchy.enums import MemoryTier
from backend.agents.specialized.application.specialization_service import SpecializedAgentService
from backend.agents.specialized.domain.enums import SpecializedAgentRole
from backend.agents.specialized.domain.exceptions import AgentPolicyViolationError


def test_memory_tier_access_enforcement():
    svc = SpecializedAgentService.get_instance()

    # 1. Resume screening agent permitted only AGENT tier
    svc.verify_memory_tier_access(SpecializedAgentRole.RESUME_SCREENING_AGENT, MemoryTier.AGENT)

    with pytest.raises(AgentPolicyViolationError):
        svc.verify_memory_tier_access(SpecializedAgentRole.RESUME_SCREENING_AGENT, MemoryTier.ORGANIZATION)

    # 2. Executive agent permitted AGENT and ORGANIZATION tiers
    svc.verify_memory_tier_access(SpecializedAgentRole.EXECUTIVE_HR_AGENT, MemoryTier.ORGANIZATION)

    # 3. Employee assistant permitted AGENT and EMPLOYEE tiers
    svc.verify_memory_tier_access(SpecializedAgentRole.EMPLOYEE_ASSISTANT_AGENT, MemoryTier.EMPLOYEE)
