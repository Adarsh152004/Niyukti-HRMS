"""Tests — Agent domain models, capability matching, and execution context."""

from backend.agents.domain.enums import AgentStatus, AgentType, TaskPriority, TaskStatus
from backend.agents.domain.models import Agent, AgentCapability, AgentTask


def test_agent_model_instantiation_and_capability_check():
    cap_read = AgentCapability(
        capability_id="cap-emp-read",
        name="Read Employees",
        resource="employee",
        actions=["read"],
        risk_level="LOW",
        enabled=True,
    )
    cap_write = AgentCapability(
        capability_id="cap-emp-create",
        name="Create Employees",
        resource="employee",
        actions=["create"],
        risk_level="MEDIUM",
        enabled=False,
    )

    agent = Agent(
        organization_id="org-acme",
        name="recruiter-agent-1",
        display_name="Recruiter Agent",
        agent_type=AgentType.RECRUITMENT_AGENT,
        actor_id="actor-agent-1",
        capabilities=[cap_read, cap_write],
    )

    assert agent.status == AgentStatus.CREATED
    assert agent.has_capability("employee", "read") is True
    # Disabled capability returns False
    assert agent.has_capability("employee", "create") is False
    assert agent.has_capability("employee", "terminate") is False


def test_agent_task_instantiation():
    task = AgentTask(
        organization_id="org-acme",
        agent_id="agent-1",
        goal="Screen resume #99",
        priority=TaskPriority.HIGH,
    )

    assert task.status == TaskStatus.CREATED
    task.transition_to(TaskStatus.QUEUED)
    assert task.status == TaskStatus.QUEUED
    task.transition_to(TaskStatus.RUNNING)
    assert task.status == TaskStatus.RUNNING
