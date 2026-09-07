"""Tests — Agent Observability Metrics Aggregation."""

import pytest

from backend.agents.governance.application.budget_service import BudgetService
from backend.agents.governance.application.execution_ledger_service import ExecutionLedgerService
from backend.agents.governance.application.observability_service import AgentObservabilityService
from backend.agents.governance.domain.enums import LedgerEventType
from backend.agents.governance.domain.models import ExecutionLedgerEntry


@pytest.mark.asyncio
async def test_agent_observability_metrics():
    ledger_svc = ExecutionLedgerService()
    budget_svc = BudgetService()
    obs_svc = AgentObservabilityService(ledger_service=ledger_svc, budget_service=budget_svc)

    # Append sample executions
    await ledger_svc.record_execution(
        ExecutionLedgerEntry(
            organization_id="org-acme",
            agent_id="agent-obs",
            actor_id="act-1",
            task_id="task-1",
            event_type=LedgerEventType.TOOL_EXECUTION,
            action="read",
            resource="employee",
            duration_ms=120,
        )
    )

    metrics = await obs_svc.get_agent_metrics("org-acme", "agent-obs")
    assert metrics["agent_id"] == "agent-obs"
    assert metrics["total_actions"] == 1
    assert metrics["tool_calls_count"] == 1
    assert metrics["average_duration_ms"] == 120.0
