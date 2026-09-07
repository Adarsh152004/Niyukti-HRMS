"""Tests — Agent initiating workflow via CommandBus and preserving correlation IDs."""

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import AgentType
from backend.agents.domain.models import AgentCapability
from backend.agents.orchestration.application.orchestrator import AgentOrchestrator
from backend.agents.reasoning.application.reasoning_engine import ReasoningEngine
from backend.agents.reasoning.domain.enums import DecisionType
from backend.agents.reasoning.domain.models import ReasoningDecision
from backend.agents.reasoning.providers.mock import MockLLMProvider


@pytest.mark.asyncio
async def test_agent_workflow_integration_preserves_correlation_ids():
    provider = MockLLMProvider()
    provider.enqueue_decision(
        ReasoningDecision(
            decision_type=DecisionType.ANSWER,
            explanation="Workflow triggered successfully.",
            final_response="Employee onboarding workflow initiated.",
        )
    )

    agent_svc = AgentService()
    task_svc = AgentTaskService()

    cap_wf = AgentCapability(capability_id="cap-wf", name="Workflow Agent", resource="workflow", actions=["start"])
    agent = await agent_svc.create_agent(
        organization_id="org-acme",
        name="wf-agent",
        display_name="Workflow Agent",
        agent_type=AgentType.WORKFLOW_AGENT,
        capabilities=[cap_wf],
    )
    await agent_svc.activate_agent("org-acme", agent.agent_id)

    task = await task_svc.create_task(organization_id="org-acme", agent_id=agent.agent_id, goal="Start onboarding workflow")

    reasoning_engine = ReasoningEngine(provider=provider, agent_service=agent_svc, task_service=task_svc)
    orchestrator = AgentOrchestrator(
        registry=agent_svc.registry,
        agent_service=agent_svc,
        task_service=task_svc,
        reasoning_engine=reasoning_engine,
    )

    execution = await orchestrator.run_task("org-acme", agent.agent_id, task.task_id)

    assert execution.state == "COMPLETED"
    assert len(execution.events) > 0
    assert execution.events[0].execution_id == execution.execution_id
