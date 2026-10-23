"""Tests — Supervisor / Worker Agent Pattern Execution & Result Aggregation."""

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.delegation.application.supervisor_agent import SupervisorAgent
from backend.agents.domain.models import AgentCapability


@pytest.mark.asyncio
async def test_supervisor_worker_pattern():
    agent_svc = AgentService()
    sup_agent = SupervisorAgent(agent_service=agent_svc)

    cap_read = AgentCapability(capability_id="c1", name="Read Emp", resource="employee", actions=["read"])

    sup = await agent_svc.create_agent(
        organization_id="org-acme",
        name="supervisor-lead",
        display_name="Lead Supervisor",
        actor_id="act-lead",
        capabilities=[cap_read],
    )
    await agent_svc.activate_agent("org-acme", sup.agent_id)

    wrk1 = await agent_svc.create_agent(
        organization_id="org-acme",
        name="worker-data-1",
        display_name="Worker 1",
        actor_id="act-w1",
        capabilities=[cap_read],
    )
    await agent_svc.activate_agent("org-acme", wrk1.agent_id)

    # 1. Discover eligible workers
    workers = await sup_agent.discover_eligible_workers("org-acme", resource="employee", actions=["read"])
    assert len(workers) >= 2

    # 2. Delegate subtask and execute
    task = await sup_agent.delegate_subtask(
        organization_id="org-acme",
        supervisor_agent_id=sup.agent_id,
        worker_agent_id=wrk1.agent_id,
        parent_task_id="task-root-100",
        goal="Retrieve employee summary",
        requested_capabilities=[cap_read],
    )

    assert task.status == "COMPLETED"

    # 3. Aggregate results
    report = sup_agent.aggregate_results(
        task_results=[task.result or {}],
        title="Employee Summary Onboarding Report",
    )
    assert report["total_subtasks"] == 1
    assert report["title"] == "Employee Summary Onboarding Report"
