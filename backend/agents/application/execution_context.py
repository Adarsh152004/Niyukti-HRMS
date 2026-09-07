"""
Agent Execution Context — Factory for generating immutable execution context tokens.
"""

from __future__ import annotations

from typing import Any

from backend.agents.domain.models import Agent, AgentExecutionContext, AgentTask
from backend.hrms.domain.actor import Actor, ActorType


class AgentExecutionContextFactory:
    """
    Factory creating immutable runtime AgentExecutionContext tokens.
    """

    @staticmethod
    def create_context(
        agent: Agent,
        task: AgentTask,
        actor: Actor | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentExecutionContext:
        """Construct deterministic execution context for an active agent task."""
        cap_tokens = [f"{c.resource}:{act}" for c in agent.capabilities if c.enabled for act in c.actions]

        mapped_actor = actor or Actor(
            actor_id=agent.actor_id,
            actor_type=ActorType.AI_AGENT,
            organization_id=agent.organization_id,
            identity=f"ai_agent:{agent.name}",
        )

        return AgentExecutionContext(
            agent_id=agent.agent_id,
            actor_id=mapped_actor.actor_id,
            organization_id=task.organization_id,
            task_id=task.task_id,
            correlation_id=task.correlation_id,
            capabilities=cap_tokens,
            metadata=metadata or {},
        )
