"""
Agent Lifecycle Manager — Enforces valid AgentStatus state transitions.
"""

from __future__ import annotations

from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.models import Agent


class AgentLifecycleManager:
    """
    Evaluates and applies state transitions for Agent entities.
    """

    @staticmethod
    def activate(agent: Agent) -> Agent:
        agent.transition_to(AgentStatus.ACTIVE)
        return agent

    @staticmethod
    def pause(agent: Agent) -> Agent:
        agent.transition_to(AgentStatus.PAUSED)
        return agent

    @staticmethod
    def suspend(agent: Agent) -> Agent:
        agent.transition_to(AgentStatus.SUSPENDED)
        return agent

    @staticmethod
    def disable(agent: Agent) -> Agent:
        agent.transition_to(AgentStatus.DISABLED)
        return agent

    @staticmethod
    def terminate(agent: Agent) -> Agent:
        agent.transition_to(AgentStatus.TERMINATED)
        return agent
