"""Tests — AgentOrchestrator task trajectory execution and state management."""

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import AgentType, TaskStatus
from backend.agents.domain.models import AgentCapability
from backend.agents.orchestration.application.orchestrator import AgentOrchestrator
from backend.agents.orchestration.domain.enums import ExecutionState
from backend.agents.reasoning.application.reasoning_engine import ReasoningEngine
from backend.agents.reasoning.domain.enums import DecisionType
from backend.agents.reasoning.domain.models import ReasoningDecision
from backend.agents.reasoning.providers.mock import MockLLMProvider


@pytest.mark.asyncio
async def test_agent_orchestrator_run_task_completion():
    provider = MockLLMProvider()
    provider.enqueue_decision(
        ReasoningDecision(
            decision_type=DecisionType.ANSWER,
            explanation="Solved task directly.",
            final_response="Task completed cleanly.",
        )
    )

    agent_service = AgentService()
    task_service = AgentTaskService()

    cap_read = AgentCapability(
        capability_id="cap-1",
        name="Read Emp",
        resource="employee",
        actions=["read"],
    )

    agent = await agent_service.create_agent(
        organization_id="org-acme",
        name="orch-bot",
        display_name="Orch Bot",
        agent_type=AgentType.ANALYTICS_AGENT,
        capabilities=[cap_read],
    )
    await agent_service.activate_agent("org-acme", agent.agent_id)

    task = await task_service.create_task(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        goal="Direct answer task",
    )

    reasoning_engine = ReasoningEngine(provider=provider, agent_service=agent_service, task_service=task_service)
    orchestrator = AgentOrchestrator(
        registry=agent_service.registry,
        agent_service=agent_service,
        task_service=task_service,
        reasoning_engine=reasoning_engine,
    )

    execution = await orchestrator.run_task("org-acme", agent.agent_id, task.task_id)

    assert execution.state == ExecutionState.COMPLETED
    assert execution.result_data["final_response"] == "Task completed cleanly."

    updated_task = await task_service.get_task("org-acme", task.task_id)
    assert updated_task.status == TaskStatus.COMPLETED
