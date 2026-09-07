"""
Agent Domain ↕ Database Mappers.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.agents.domain.enums import AgentStatus, AgentType, TaskPriority, TaskStatus
from backend.agents.domain.models import Agent, AgentCapability, AgentTask
from backend.agents.infrastructure.database.models import AgentModel, AgentTaskModel


class AgentMapper:
    @staticmethod
    def to_domain(model: AgentModel) -> Agent:
        now = datetime.now(tz=UTC)
        caps = [AgentCapability(**c) for c in (model.capabilities_json or [])]
        return Agent(
            agent_id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            display_name=model.display_name,
            description=model.description,
            agent_type=AgentType(model.agent_type),
            status=AgentStatus(model.status),
            actor_id=model.actor_id,
            version=model.version,
            capabilities=caps,
            metadata=model.metadata_json or {},
            system_instructions_reference=model.system_instructions_reference,
            max_concurrent_tasks=model.max_concurrent_tasks,
            created_at=model.created_at or now,
            updated_at=model.updated_at or now,
        )

    @staticmethod
    def to_model(domain: Agent) -> AgentModel:
        caps_json = [c.model_dump() for c in domain.capabilities]
        return AgentModel(
            id=domain.agent_id,
            organization_id=domain.organization_id,
            name=domain.name,
            display_name=domain.display_name,
            description=domain.description,
            agent_type=domain.agent_type.value,
            status=domain.status.value,
            actor_id=domain.actor_id,
            version=domain.version,
            capabilities_json=caps_json,
            metadata_json=domain.metadata,
            system_instructions_reference=domain.system_instructions_reference,
            max_concurrent_tasks=domain.max_concurrent_tasks,
        )


class AgentTaskMapper:
    @staticmethod
    def to_domain(model: AgentTaskModel) -> AgentTask:
        now = datetime.now(tz=UTC)
        return AgentTask(
            task_id=model.id,
            organization_id=model.organization_id,
            agent_id=model.agent_id,
            parent_task_id=model.parent_task_id,
            correlation_id=model.correlation_id,
            goal=model.goal,
            description=model.description,
            priority=TaskPriority(model.priority),
            status=TaskStatus(model.status),
            input=model.input_json or {},
            output=model.output_json or {},
            created_at=model.created_at or now,
            started_at=model.started_at,
            completed_at=model.completed_at,
            failure_reason=model.failure_reason,
            retry_count=model.retry_count,
            metadata=model.metadata_json or {},
        )

    @staticmethod
    def to_model(domain: AgentTask) -> AgentTaskModel:
        return AgentTaskModel(
            id=domain.task_id,
            organization_id=domain.organization_id,
            agent_id=domain.agent_id,
            parent_task_id=domain.parent_task_id,
            correlation_id=domain.correlation_id,
            goal=domain.goal,
            description=domain.description,
            priority=domain.priority.value,
            status=domain.status.value,
            input_json=domain.input,
            output_json=domain.output,
            started_at=domain.started_at,
            completed_at=domain.completed_at,
            failure_reason=domain.failure_reason,
            retry_count=domain.retry_count,
            metadata_json=domain.metadata,
        )
