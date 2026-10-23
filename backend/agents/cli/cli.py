"""
Agent CLI Foundation — Command Line Interface for AI Agent Management and Tasks.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from backend.agents.application.agent_registry import AgentRegistry
from backend.agents.application.agent_service import AgentService
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.models import Agent, AgentTask


class AgentCLI:
    """
    CLI interface managing AI Agents and Tasks.
    """

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        agent_service: AgentService | None = None,
        task_service: AgentTaskService | None = None,
    ) -> None:
        self.registry = registry or AgentRegistry()
        self.agent_service = agent_service or AgentService(registry=self.registry)
        self.task_service = task_service or AgentTaskService()

    async def list_agents(self, organization_id: str) -> Sequence[Agent]:
        """List all AI agents for tenant."""
        return await self.registry.list_agents(organization_id)

    async def inspect_agent(self, organization_id: str, agent_id: str) -> Agent:
        """Inspect agent details."""
        return await self.registry.get_agent(organization_id, agent_id)

    async def activate_agent(self, organization_id: str, agent_id: str) -> Agent:
        """Activate agent."""
        return await self.agent_service.activate_agent(organization_id, agent_id)

    async def pause_agent(self, organization_id: str, agent_id: str) -> Agent:
        """Pause agent."""
        return await self.agent_service.pause_agent(organization_id, agent_id)

    async def list_tasks(self, organization_id: str, agent_id: str) -> Sequence[AgentTask]:
        """List tasks assigned to an agent."""
        return await self.task_service.list_tasks_for_agent(organization_id, agent_id)

    async def discover_tools(self, organization_id: str, agent_id: str) -> Sequence[Any]:
        """Discover tools available to agent based on capabilities."""
        from backend.agents.application.execution_context import AgentExecutionContextFactory
        from backend.agents.tools.application.tool_discovery import ToolDiscovery
        from backend.agents.tools.infrastructure.builtin_tools import register_builtin_tools

        register_builtin_tools()
        agent = await self.registry.get_agent(organization_id, agent_id)
        dummy_task = await self.task_service.create_task(organization_id=organization_id, agent_id=agent_id, goal="CLI Discovery")
        ctx = AgentExecutionContextFactory.create_context(agent, dummy_task)
        discovery = ToolDiscovery()
        return discovery.discover_tools(agent, ctx)

    async def list_memories(self, organization_id: str, agent_id: str) -> Sequence[Any]:
        """List memories recorded for an agent."""
        from backend.agents.memory.application.memory_service import MemoryService

        mem_service = MemoryService()
        return await mem_service.get_memories_for_agent(organization_id, agent_id)

    async def run_task(self, organization_id: str, agent_id: str, task_id: str) -> Any:
        """Run task orchestration."""
        from backend.agents.orchestration.application.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(registry=self.registry, agent_service=self.agent_service, task_service=self.task_service)
        return await orchestrator.run_task(organization_id, agent_id, task_id)

    async def get_plan(self, organization_id: str, task_id: str) -> Any:
        """Get plan for task."""
        from backend.agents.planning.application.planner_service import PlannerService

        planner = PlannerService(agent_registry=self.registry, task_service=self.task_service)
        return await planner.get_plan_for_task(organization_id, task_id)

    async def get_execution(self, organization_id: str, task_id: str) -> Any:
        """Get task execution trajectory."""
        from backend.agents.orchestration.application.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(registry=self.registry, agent_service=self.agent_service, task_service=self.task_service)
        return await orchestrator.get_execution(organization_id, task_id)

    async def list_delegations(self, organization_id: str, delegator_agent_id: str | None = None) -> Sequence[Any]:
        """List delegations for tenant or agent."""
        from backend.agents.delegation.application.delegation_service import DelegationService

        del_svc = DelegationService(agent_service=self.agent_service)
        return await del_svc.list_delegations(organization_id, delegator_agent_id=delegator_agent_id)

    async def inspect_delegation(self, organization_id: str, delegation_id: str) -> Any:
        """Inspect delegation details."""
        from backend.agents.delegation.application.delegation_service import DelegationService

        del_svc = DelegationService(agent_service=self.agent_service)
        return await del_svc.get_delegation(organization_id, delegation_id)

    async def cancel_delegation(self, organization_id: str, delegation_id: str) -> Any:
        """Cancel delegation."""
        from backend.agents.delegation.application.delegation_service import DelegationService

        del_svc = DelegationService(agent_service=self.agent_service)
        return await del_svc.cancel_delegation(organization_id, delegation_id)

    async def get_governance(self, organization_id: str, agent_id: str) -> Any:
        """Get agent governance policy."""
        from backend.agents.governance.application.governance_policy_service import GovernancePolicyService

        gov_svc = GovernancePolicyService()
        return await gov_svc.get_or_create_policy(organization_id, agent_id)

    async def get_usage(self, organization_id: str, agent_id: str) -> Any:
        """Get agent budget and usage counters."""
        from backend.agents.governance.application.budget_service import BudgetService

        budget_svc = BudgetService()
        return await budget_svc.get_or_create_budget(organization_id, agent_id)

    async def get_executions(self, organization_id: str, agent_id: str, task_id: str | None = None) -> Sequence[Any]:
        """Get agent execution ledger entries."""
        from backend.agents.governance.application.execution_ledger_service import ExecutionLedgerService

        ledger_svc = ExecutionLedgerService()
        return await ledger_svc.list_ledger_entries(organization_id, agent_id, task_id=task_id)

    async def get_violations(self, organization_id: str, agent_id: str) -> Sequence[Any]:
        """Get agent governance policy violations."""
        from backend.agents.governance.application.governance_policy_service import GovernancePolicyService

        gov_svc = GovernancePolicyService()
        return await gov_svc.list_violations(organization_id, agent_id)

    async def get_evaluations(self, organization_id: str, agent_id: str, task_id: str) -> Any:
        """Evaluate agent task trajectory."""
        from backend.agents.evaluation.application.trace_evaluator import TraceEvaluator

        evaluator = TraceEvaluator()
        return await evaluator.evaluate_task_trajectory(organization_id, agent_id, task_id)

    async def get_metrics(self, organization_id: str, agent_id: str) -> Any:
        """Get agent observability metrics."""
        from backend.agents.governance.application.observability_service import AgentObservabilityService

        obs_svc = AgentObservabilityService()
        return await obs_svc.get_agent_metrics(organization_id, agent_id)

    async def get_audit(self, organization_id: str, agent_id: str, task_id: str | None = None) -> Sequence[Any]:
        """Get agent governance audit trail."""
        from backend.agents.governance.application.audit_service import AuditService

        audit_svc = AuditService()
        return await audit_svc.list_audit_records(organization_id, agent_id, task_id=task_id)

    async def get_anomalies(self, organization_id: str, agent_id: str, status: str | None = None) -> Sequence[Any]:
        """Get agent anomalies."""
        from backend.agents.governance.application.anomaly_service import AnomalyService

        anomaly_svc = AnomalyService()
        return await anomaly_svc.list_anomalies(organization_id, agent_id, status=status)

    async def contain_agent(
        self,
        organization_id: str,
        agent_id: str,
        action: str,
        reason: str,
        actor: Any,
    ) -> Any:
        """Execute containment action on agent."""
        from backend.agents.governance.application.containment_service import ContainmentService
        from backend.agents.governance.domain.enums import ContainmentActionType

        contain_svc = ContainmentService()
        return await contain_svc.execute_containment(
            organization_id=organization_id,
            agent_id=agent_id,
            action_type=ContainmentActionType(action),
            reason=reason,
            triggered_by=actor,
        )
