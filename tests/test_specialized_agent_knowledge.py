"""
Tests for Pre-Retrieval Knowledge Scoping and Confidentiality Tier Enforcement.
"""

from __future__ import annotations

import pytest

from backend.agents.specialized.application.specialization_service import SpecializedAgentService
from backend.agents.specialized.domain.enums import SpecializedAgentRole
from backend.agents.specialized.domain.exceptions import AgentPolicyViolationError
from backend.knowledge.domain.enums import AccessScopeType, KnowledgeClassification


def test_knowledge_scope_and_confidentiality_boundaries():
    svc = SpecializedAgentService.get_instance()

    # 1. Valid scope & classification
    svc.verify_knowledge_access(
        role=SpecializedAgentRole.RESUME_SCREENING_AGENT,
        scope=AccessScopeType.ROLE_BASED,
        classification=KnowledgeClassification.INTERNAL,
    )

    # 2. Scope violation: Resume screening cannot access DEPARTMENT_ONLY scope
    with pytest.raises(AgentPolicyViolationError):
        svc.verify_knowledge_access(
            role=SpecializedAgentRole.RESUME_SCREENING_AGENT,
            scope=AccessScopeType.DEPARTMENT_ONLY,
            classification=KnowledgeClassification.INTERNAL,
        )

    # 3. Confidentiality tier violation: Resume screening max is INTERNAL -> cannot read HIGHLY_SENSITIVE
    with pytest.raises(AgentPolicyViolationError):
        svc.verify_knowledge_access(
            role=SpecializedAgentRole.RESUME_SCREENING_AGENT,
            scope=AccessScopeType.ROLE_BASED,
            classification=KnowledgeClassification.HIGHLY_SENSITIVE,
        )
