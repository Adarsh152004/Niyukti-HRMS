"""
AgentOrchestrator — Central Orchestrator for Autonomous AI Agents.
Coordinating Task, Context, Memory, Reasoning, Planning, Validation, Execution, HITL, Recovery, and Event emission.
"""

from __future__ import annotations

import logging

from backend.agents.application.agent_registry import AgentRegistry
from backend.agents.application.agent_service import AgentService
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.exceptions import AgentSecurityError, AgentTaskError
from backend.agents.domain.models import AgentTask
from backend.agents.memory.application.memory_service import MemoryService
from backend.agents.orchestration.application.approval_manager import ApprovalManager
from backend.agents.orchestration.application.execution_loop import ExecutionLoop
from backend.agents.orchestration.application.recovery_manager import RecoveryManager
from backend.agents.orchestration.application.task_manager import TaskManager
from backend.agents.orchestration.domain.enums import ExecutionState
from backend.agents.orchestration.domain.models import AgentExecution
from backend.agents.planning.application.planner_service import PlannerService
from backend.agents.reasoning.application.reasoning_engine import ReasoningEngine
from backend.agents.tools.application.tool_gateway import ToolExecutionGateway
from backend.hrms.domain.actor import Actor
from backend.runtime.events import Event, EventBus

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Production-grade Autonomous Agent Orchestrator.
    """

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        agent_service: AgentService | None = None,
        task_service: AgentTaskService | None = None,
        planner_service: PlannerService | None = None,
        reasoning_engine: ReasoningEngine | None = None,
        tool_gateway: ToolExecutionGateway | None = None,
        memory_service: MemoryService | None = None,
        task_manager: TaskManager | None = None,
        approval_manager: ApprovalManager | None = None,
        recovery_manager: RecoveryManager | None = None,
        execution_loop: ExecutionLoop | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.registry = registry or AgentRegistry()
        self.agent_service = agent_service or AgentService(registry=self.registry)
        self.task_service = task_service or AgentTaskService()
        self.planner_service = planner_service or PlannerService(agent_registry=self.registry, task_service=self.task_service)
        self.reasoning_engine = reasoning_engine or ReasoningEngine(
            agent_service=self.agent_service, task_service=self.task_service
        )
        self.tool_gateway = tool_gateway or ToolExecutionGateway()
        self.memory_service = memory_service or MemoryService()
        self.task_manager = task_manager or TaskManager(task_service=self.task_service)
        self.approval_manager = approval_manager or ApprovalManager()
        self.recovery_manager = recovery_manager or RecoveryManager(plan_repo=self.planner_service.plan_repo)
        self.event_bus = event_bus or EventBus.get_instance()

        self.execution_loop = execution_loop or ExecutionLoop(
            reasoning_engine=self.reasoning_engine,
            planner_service=self.planner_service,
            tool_gateway=self.tool_gateway,
            memory_service=self.memory_service,
            task_manager=self.task_manager,
            approval_manager=self.approval_manager,
            event_bus=self.event_bus,
        )

        self._executions: dict[str, AgentExecution] = {}

    async def run_task(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str,
        actor: Actor | None = None,
    ) -> AgentExecution:
        """
        Run an autonomous agent task trajectory.
        """
        agent = await self.registry.get_agent(organization_id, agent_id)
        if agent.status != AgentStatus.ACTIVE:
            raise AgentSecurityError(f"Cannot run plan for inactive agent '{agent_id}' (status: {agent.status}).")

        task = await self.task_service.get_task(organization_id, task_id)
        if not task or task.agent_id != agent_id:
            raise AgentTaskError(f"Task '{task_id}' not found or assigned to different agent.")

        # Create or fetch execution record
        execution = AgentExecution(
            organization_id=organization_id,
            agent_id=agent_id,
            task_id=task_id,
        )
        self._executions[execution.execution_id] = execution

        # Execute loop
        res_exec = await self.execution_loop.run(
            execution=execution,
            agent=agent,
            task=task,
            actor=actor,
        )

        await self._publish_orchestration_events(res_exec)
        return res_exec

    async def pause_task(self, organization_id: str, task_id: str) -> AgentTask:
        """Pause agent task execution."""
        task = await self.task_manager.pause_task(organization_id, task_id)
        exec_item = self._get_execution_by_task(organization_id, task_id)
        if exec_item:
            exec_item.state = ExecutionState.PAUSED
        return task

    async def resume_task(self, organization_id: str, task_id: str, actor: Actor | None = None) -> AgentExecution:
        """Resume paused task execution."""
        task = await self.task_manager.resume_task(organization_id, task_id)
        return await self.run_task(organization_id, task.agent_id, task_id, actor=actor)

    async def cancel_task(self, organization_id: str, task_id: str) -> AgentTask:
        """Cancel task execution."""
        task = await self.task_manager.cancel_task(organization_id, task_id)
        exec_item = self._get_execution_by_task(organization_id, task_id)
        if exec_item:
            exec_item.state = ExecutionState.CANCELLED
        return task

    async def replan_task(self, organization_id: str, task_id: str, reason: str) -> AgentExecution:
        """Replan task following transient failure."""
        task = await self.task_service.get_task(organization_id, task_id)
        if not task:
            raise AgentTaskError(f"Task '{task_id}' not found.")

        plan = await self.planner_service.get_plan_for_task(organization_id, task_id)
        if not plan:
            raise AgentTaskError(f"No active plan found for task '{task_id}'.")

        await self.planner_service.replan(organization_id, plan.plan_id, failure_reason=reason)
        return await self.run_task(organization_id, task.agent_id, task_id)

    async def get_execution(self, organization_id: str, task_id: str) -> AgentExecution | None:
        """Get execution record for task."""
        return self._get_execution_by_task(organization_id, task_id)

    async def recover_interrupted_tasks(self, organization_id: str) -> list[AgentExecution]:
        """Recover crash-interrupted tasks on startup."""
        interrupted = await self.recovery_manager.find_interrupted_executions(list(self._executions.values()))
        recovered = []
        for item in interrupted:
            rec = await self.recovery_manager.recover_execution(item, self.planner_service.plan_repo)
            recovered.append(rec)
        return recovered

    def _get_execution_by_task(self, organization_id: str, task_id: str) -> AgentExecution | None:
        for item in self._executions.values():
            if item.organization_id == organization_id and item.task_id == task_id:
                return item
        return None

    async def _publish_orchestration_events(self, execution: AgentExecution) -> None:
        for evt in execution.events:
            await self.event_bus.publish(
                Event(
                    event_type=evt.event_type.value,
                    source="agent_orchestrator",
                    payload={
                        "execution_id": evt.execution_id,
                        "organization_id": evt.organization_id,
                        "agent_id": evt.agent_id,
                        "task_id": evt.task_id,
                        "details": evt.payload,
                    },
                )
            )
