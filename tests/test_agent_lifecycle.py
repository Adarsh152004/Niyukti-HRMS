"""Tests — Agent lifecycle state transitions and invalid transition enforcement."""

import pytest

from backend.agents.application.agent_lifecycle import AgentLifecycleManager
from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.exceptions import AgentLifecycleError
from backend.agents.domain.models import Agent


def test_agent_lifecycle_valid_transitions():
    agent = Agent(
        organization_id="org-acme",
        name="test-agent",
        display_name="Test Agent",
        actor_id="actor-test",
    )

    assert agent.status == AgentStatus.CREATED

    AgentLifecycleManager.activate(agent)
    assert agent.status == AgentStatus.ACTIVE

    AgentLifecycleManager.pause(agent)
    assert agent.status == AgentStatus.PAUSED

    AgentLifecycleManager.activate(agent)
    assert agent.status == AgentStatus.ACTIVE

    AgentLifecycleManager.disable(agent)
    assert agent.status == AgentStatus.DISABLED

    AgentLifecycleManager.terminate(agent)
    assert agent.status == AgentStatus.TERMINATED


def test_terminated_agent_is_terminal():
    agent = Agent(
        organization_id="org-acme",
        name="test-agent",
        display_name="Test Agent",
        actor_id="actor-test",
        status=AgentStatus.TERMINATED,
    )

    with pytest.raises(AgentLifecycleError, match="Invalid agent status transition"):
        AgentLifecycleManager.activate(agent)
