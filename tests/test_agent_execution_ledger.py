"""Tests — Immutable Execution Ledger Recording & Immutability Enforcement."""

import pytest

from backend.agents.governance.application.execution_ledger_service import ExecutionLedgerService
from backend.agents.governance.domain.enums import LedgerEventType
from backend.agents.governance.domain.exceptions import LedgerImmutabilityError
from backend.agents.governance.domain.models import ExecutionLedgerEntry
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_ledger_record_and_retrieval():
    ledger_svc = ExecutionLedgerService()

    entry = ExecutionLedgerEntry(
        organization_id="org-acme",
        agent_id="agent-audit",
        actor_id="act-1",
        task_id="task-100",
        event_type=LedgerEventType.TOOL_EXECUTION,
        action="read",
        resource="employee",
    )

    recorded = await ledger_svc.record_execution(entry)
    assert recorded.ledger_id == entry.ledger_id

    entries = await ledger_svc.list_ledger_entries("org-acme", "agent-audit", task_id="task-100")
    assert len(entries) == 1
    assert entries[0].resource == "employee"


@pytest.mark.asyncio
async def test_ledger_immutability_delete_attempt():
    ledger_svc = ExecutionLedgerService()
    admin = Actor(actor_id="adm", actor_type=ActorType.HUMAN, organization_id="org-acme", permissions=set())

    with pytest.raises(LedgerImmutabilityError, match="immutable"):
        await ledger_svc.attempt_delete_ledger(admin)
