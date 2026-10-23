"""
Agent Observability Service — Aggregates metrics, latencies, success rates, and budget consumption.
Ensures sensitive tokens, passwords, and raw prompts are NEVER exposed.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.agents.governance.application.budget_service import BudgetService
from backend.agents.governance.application.execution_ledger_service import ExecutionLedgerService
from backend.agents.governance.domain.enums import LedgerEventType

logger = logging.getLogger(__name__)


class AgentObservabilityService:
    """
    Computes tenant-isolated observability metrics for agents, tools, commands, and delegations.
    """

    def __init__(
        self,
        ledger_service: ExecutionLedgerService | None = None,
        budget_service: BudgetService | None = None,
    ) -> None:
        self.ledger_service = ledger_service or ExecutionLedgerService()
        self.budget_service = budget_service or BudgetService()

    async def get_agent_metrics(self, organization_id: str, agent_id: str) -> dict[str, Any]:
        """Compute top-level agent execution metrics."""
        entries = await self.ledger_service.list_ledger_entries(organization_id, agent_id)
        budget = await self.budget_service.get_or_create_budget(organization_id, agent_id)

        total_actions = len(entries)
        successful_actions = sum(1 for e in entries if e.policy_result == "SUCCESS" and e.decision == "ALLOWED")
        failed_actions = sum(1 for e in entries if e.failure_reason is not None)
        denied_actions = sum(1 for e in entries if e.decision == "DENIED")

        tool_calls = sum(1 for e in entries if e.event_type == LedgerEventType.TOOL_EXECUTION)
        command_executions = sum(1 for e in entries if e.event_type == LedgerEventType.COMMAND_DISPATCH)
        hitl_requests = sum(1 for e in entries if e.event_type == LedgerEventType.HITL_REQUEST)
        delegations = sum(1 for e in entries if e.event_type == LedgerEventType.DELEGATION_GRANT)

        avg_duration = sum(e.duration_ms for e in entries) / total_actions if total_actions > 0 else 0.0

        return {
            "agent_id": agent_id,
            "organization_id": organization_id,
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "denied_actions": denied_actions,
            "tool_calls_count": tool_calls,
            "command_executions_count": command_executions,
            "hitl_requests_count": hitl_requests,
            "delegations_count": delegations,
            "average_duration_ms": round(avg_duration, 2),
            "tokens_consumed": budget.tokens_consumed,
            "budget_exhausted": budget.is_exhausted(),
        }

    async def get_tool_metrics(self, organization_id: str, agent_id: str) -> list[dict[str, Any]]:
        """Compute tool invocation metrics."""
        entries = await self.ledger_service.list_ledger_entries(organization_id, agent_id)
        tool_entries = [e for e in entries if e.event_type == LedgerEventType.TOOL_EXECUTION]

        tool_stats: dict[str, dict[str, Any]] = {}
        for entry in tool_entries:
            tool = entry.resource
            if tool not in tool_stats:
                tool_stats[tool] = {"tool_name": tool, "invocations": 0, "successes": 0, "failures": 0, "total_duration_ms": 0}
            tool_stats[tool]["invocations"] += 1
            if entry.failure_reason:
                tool_stats[tool]["failures"] += 1
            else:
                tool_stats[tool]["successes"] += 1
            tool_stats[tool]["total_duration_ms"] += entry.duration_ms

        results: list[dict[str, Any]] = []
        for tool, stat in tool_stats.items():
            inv = stat["invocations"]
            results.append(
                {
                    "tool_name": tool,
                    "invocations": inv,
                    "success_rate": round(stat["successes"] / inv, 2) if inv > 0 else 0.0,
                    "failure_rate": round(stat["failures"] / inv, 2) if inv > 0 else 0.0,
                    "average_latency_ms": round(stat["total_duration_ms"] / inv, 2) if inv > 0 else 0.0,
                }
            )
        return results
