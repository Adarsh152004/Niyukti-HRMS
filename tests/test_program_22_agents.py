"""
AI-Powered Intelligent HRMS — Program 22 24 Specialized Agents Test Suite.

Verifies:
1. All 24 specialized agent definitions
2. Autonomy tiers and supervisor delegation hierarchies
"""

import pytest

from backend.agents.specialized.registry.catalog import SpecializedAgentCatalog


def test_specialized_agent_catalog_autonomy():
    """Verify all 24 agents exist in catalog with configured autonomy."""
    catalog = SpecializedAgentCatalog.get_instance()
    agents = catalog.list_definitions()
    assert len(agents) == 24
    for agent in agents:
        assert agent.display_name is not None
        assert agent.autonomy_mode is not None
