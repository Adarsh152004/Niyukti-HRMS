"""
Tests for Specialized AI HR Agent Catalog Completeness and Declarative Specifications.
"""

from __future__ import annotations

from backend.agents.specialized.domain.enums import SpecializedAgentRole
from backend.agents.specialized.registry.catalog import SpecializedAgentCatalog


def test_catalog_contains_all_24_agents():
    catalog = SpecializedAgentCatalog.get_instance()
    definitions = catalog.list_definitions()

    # Must contain exactly 24 standard specialized agents
    assert len(definitions) == 24
    assert catalog.count() == 24

    for role in SpecializedAgentRole:
        defn = catalog.get_definition(role)
        assert defn.role == role
        assert len(defn.display_name) > 0
        assert len(defn.purpose) > 0
        assert len(defn.responsibilities) > 0
        assert len(defn.capability_profile.capabilities) > 0
        assert len(defn.capability_profile.prohibited_capabilities) > 0
        assert len(defn.tool_policy.tool_access) > 0
        assert len(defn.knowledge_policy.allowed_scopes) > 0
        assert len(defn.memory_policy.allowed_tiers) > 0
        assert defn.evaluation_contract.min_accuracy_score > 0.5
        assert defn.daily_budget_usd > 0.0
        assert defn.version == "1.0.0"
        assert defn.is_active is True


def test_supervisor_hierarchy_integrity():
    catalog = SpecializedAgentCatalog.get_instance()

    # Top-level executive agent has no supervisor
    exec_defn = catalog.get_definition(SpecializedAgentRole.EXECUTIVE_HR_AGENT)
    assert exec_defn.supervisor_role is None

    # Subordinate agents report up the hierarchy
    subordinates = catalog.get_subordinates(SpecializedAgentRole.EXECUTIVE_HR_AGENT)
    sub_roles = [s.role for s in subordinates]
    assert SpecializedAgentRole.HR_MANAGER_AGENT in sub_roles
    assert SpecializedAgentRole.WORKFORCE_PLANNING_AGENT in sub_roles
    assert SpecializedAgentRole.HR_ANALYTICS_AGENT in sub_roles
    assert SpecializedAgentRole.COMPLIANCE_AGENT in sub_roles

    # Verify chain resolution from Resume Screening up to Executive
    chain = catalog.get_supervisor_chain(SpecializedAgentRole.RESUME_SCREENING_AGENT)
    assert chain == [
        SpecializedAgentRole.RESUME_SCREENING_AGENT,
        SpecializedAgentRole.RECRUITMENT_AGENT,
        SpecializedAgentRole.HR_MANAGER_AGENT,
        SpecializedAgentRole.EXECUTIVE_HR_AGENT,
    ]


def test_capability_and_tool_matrices():
    catalog = SpecializedAgentCatalog.get_instance()

    cap_matrix = catalog.get_capability_matrix()
    assert "resume:parse" in cap_matrix
    assert SpecializedAgentRole.RESUME_SCREENING_AGENT.value in cap_matrix["resume:parse"]

    tool_matrix = catalog.get_tool_matrix()
    assert "resume.parse" in tool_matrix
    assert tool_matrix["resume.parse"][SpecializedAgentRole.RESUME_SCREENING_AGENT.value] == "ALLOW"
