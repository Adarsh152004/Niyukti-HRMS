"""
Agent Ports — Abstract Repository Interfaces.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from backend.agents.domain.models import Agent, AgentTask


class AgentRepositoryPort(ABC):
    @abstractmethod
    async def save(self, agent: Agent) -> Agent:
        pass

    @abstractmethod
    async def get_by_id(self, organization_id: str, agent_id: str) -> Agent | None:
        pass

    @abstractmethod
    async def get_by_name(self, organization_id: str, name: str) -> Agent | None:
        pass

    @abstractmethod
    async def list_by_organization(self, organization_id: str) -> Sequence[Agent]:
        pass

    @abstractmethod
    async def delete(self, organization_id: str, agent_id: str) -> bool:
        pass


class AgentTaskRepositoryPort(ABC):
    @abstractmethod
    async def save(self, task: AgentTask) -> AgentTask:
        pass

    @abstractmethod
    async def get_by_id(self, organization_id: str, task_id: str) -> AgentTask | None:
        pass

    @abstractmethod
    async def list_by_agent(self, organization_id: str, agent_id: str) -> Sequence[AgentTask]:
        pass

    @abstractmethod
    async def list_by_organization(self, organization_id: str) -> Sequence[AgentTask]:
        pass
