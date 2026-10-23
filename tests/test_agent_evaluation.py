"""Tests — Trajectory Evaluation & Compliance Criteria."""

import pytest

from backend.agents.evaluation.application.trace_evaluator import TraceEvaluator
from backend.agents.governance.application.execution_ledger_service import ExecutionLedgerService
from backend.agents.governance.domain.enums import LedgerEventType
from backend.agents.governance.domain.models import ExecutionLedgerEntry


@pytest.mark.asyncio
async def test_trace_evaluation_clean_trajectory():
    ledger_svc = ExecutionLedgerService()
    evaluator = TraceEvaluator(ledger_service=ledger_svc)

    await ledger_svc.record_execution(
        ExecutionLedgerEntry(
            organization_id="org-acme",
            agent_id="agent-eval",
            actor_id="act-1",
            task_id="task-eval-1",
            event_type=LedgerEventType.TOOL_EXECUTION,
            action="read",
            resource="employee",
            authorization_result="AUTHORIZED",
            policy_result="SUCCESS",
        )
    )

    res = await evaluator.evaluate_task_trajectory("org-acme", "agent-eval", "task-eval-1")
    assert res.passed is True
    assert res.score == 1.0
    assert len(res.failures) == 0


@pytest.mark.asyncio
async def test_trace_evaluation_detects_unauthorized_attempt():
    ledger_svc = ExecutionLedgerService()
    evaluator = TraceEvaluator(ledger_service=ledger_svc)

    await ledger_svc.record_execution(
        ExecutionLedgerEntry(
            organization_id="org-acme",
            agent_id="agent-eval",
            actor_id="act-1",
            task_id="task-eval-2",
            event_type=LedgerEventType.COMMAND_DISPATCH,
            action="delete",
            resource="employee",
            authorization_result="UNAUTHORIZED",
            policy_result="DENIED",
        )
    )

    res = await evaluator.evaluate_task_trajectory("org-acme", "agent-eval", "task-eval-2")
    assert res.passed is False
    assert res.score < 1.0
    assert len(res.failures) > 0
