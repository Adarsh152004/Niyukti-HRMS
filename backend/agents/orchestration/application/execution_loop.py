"""
ExecutionLoop — Autonomous Bounded Loop enforcing runaway execution protections and safety limits.
Sequence: OBSERVE -> REASON -> PLAN -> VALIDATE -> EXECUTE -> OBSERVE RESULT -> UPDATE MEMORY -> REASON AGAIN
"""

import logging
import time
from datetime import UTC, datetime
from typing import Any

from backend.agents.application.execution_context import AgentExecutionContextFactory
from backend.agents.domain.enums import TaskStatus
from backend.agents.domain.models import Agent, AgentTask
from backend.agents.memory.application.memory_service import MemoryService
from backend.agents.memory.domain.enums import MemoryType
from backend.agents.orchestration.application.approval_manager import ApprovalManager
from backend.agents.orchestration.application.decision_manager import DecisionManager
from backend.agents.orchestration.application.task_manager import TaskManager
from backend.agents.orchestration.domain.enums import ExecutionState, OrchestrationEventType
from backend.agents.orchestration.domain.models import AgentExecution, AgentExecutionEvent
from backend.agents.planning.application.planner_service import PlannerService
from backend.agents.planning.domain.enums import PlanStatus
from backend.agents.reasoning.application.reasoning_engine import ReasoningEngine
from backend.agents.reasoning.domain.enums import DecisionType
from backend.agents.reasoning.domain.models import ReasoningDecision
from backend.agents.tools.application.tool_gateway import ToolExecutionGateway
from backend.hrms.domain.actor import Actor
from backend.runtime.events import EventBus

logger = logging.getLogger(__name__)


class ExecutionLoop:
    """
    Autonomous bounded execution loop with strict runaway protection guards.
    """

    def __init__(
        self,
        reasoning_engine: ReasoningEngine | None = None,
        planner_service: PlannerService | None = None,
        tool_gateway: ToolExecutionGateway | None = None,
        memory_service: MemoryService | None = None,
        task_manager: TaskManager | None = None,
        approval_manager: ApprovalManager | None = None,
        event_bus: EventBus | None = None,
        max_iterations: int = 10,
        max_plan_steps: int = 20,
        max_tool_calls: int = 30,
        max_execution_seconds: float = 300.0,
    ) -> None:
        self.reasoning_engine = reasoning_engine or ReasoningEngine()
        self.planner_service = planner_service or PlannerService()
        self.tool_gateway = tool_gateway or ToolExecutionGateway()
        self.memory_service = memory_service or MemoryService()
        self.task_manager = task_manager or TaskManager()
        self.approval_manager = approval_manager or ApprovalManager()
        self.decision_manager = DecisionManager()
        self.event_bus = event_bus or EventBus.get_instance()

        self.max_iterations = max_iterations
        self.max_plan_steps = max_plan_steps
        self.max_tool_calls = max_tool_calls
        self.max_execution_seconds = max_execution_seconds

    async def run(
        self,
        execution: AgentExecution,
        agent: Agent,
        task: AgentTask,
        actor: Actor | None = None,
    ) -> AgentExecution:
        """
        Execute autonomous loop until task completion, HITL pause, failure, or limit breach.
        """
        start_time = time.time()

        ctx = AgentExecutionContextFactory.create_context(agent, task, actor=actor)
        execution.state = ExecutionState.EXECUTING
        await self.task_manager.start_task(agent.organization_id, task.task_id)

        while execution.iteration_count < self.max_iterations:
            # Check maximum execution duration
            elapsed = time.time() - start_time
            if elapsed > self.max_execution_seconds:
                return await self._fail_execution(
                    execution,
                    task,
                    f"Execution exceeded maximum duration limit ({self.max_execution_seconds}s).",
                    OrchestrationEventType.LIMIT_REACHED,
                )

            execution.iteration_count += 1

            # 1. OBSERVE & REASON
            self._add_event(execution, OrchestrationEventType.REASONING_STARTED, {"iteration": execution.iteration_count})
            run = await self.reasoning_engine.run_task_reasoning(
                agent=agent,
                task=task,
                actor=actor,
                context=ctx,
            )
            self._add_event(execution, OrchestrationEventType.REASONING_COMPLETED, {"run_id": run.run_id, "status": run.status})

            if run.status == "FAILED":
                return await self._fail_execution(
                    execution,
                    task,
                    f"Reasoning engine failed: {run.metadata.get('error', 'unknown error')}",
                    OrchestrationEventType.EXECUTION_FAILED,
                )

            # Extract reasoning decision
            final_resp = task.output.get("final_response") if task.output else None
            if task.status == TaskStatus.COMPLETED or final_resp:
                execution.state = ExecutionState.COMPLETED
                execution.completed_at = datetime.now(tz=UTC)
                execution.result_data = {"final_response": final_resp or "Task completed."}
                self._add_event(execution, OrchestrationEventType.EXECUTION_COMPLETED, execution.result_data)
                return execution

            # If task paused for approval in reasoning step
            if task.status == TaskStatus.WAITING_APPROVAL:
                execution.state = ExecutionState.WAITING_APPROVAL
                self._add_event(execution, OrchestrationEventType.WAITING_APPROVAL, {"task_id": task.task_id})
                return execution

            # 2. PLAN & VALIDATE
            # Build Plan from latest task goal
            active_plan = await self.planner_service.get_plan_for_task(agent.organization_id, task.task_id)
            if not active_plan or active_plan.status in [PlanStatus.COMPLETED, PlanStatus.FAILED]:
                # Build dummy step if tool was selected
                decision = ReasoningDecision(
                    decision_type=DecisionType.ANSWER if final_resp else DecisionType.COMPLETE,
                    final_response=final_resp,
                )
                active_plan = self.decision_manager.create_plan_from_decision(
                    organization_id=agent.organization_id,
                    agent_id=agent.agent_id,
                    task_id=task.task_id,
                    objective=task.goal,
                    decision=decision,
                )

            # Check max plan steps
            if len(active_plan.steps) > self.max_plan_steps:
                return await self._fail_execution(
                    execution,
                    task,
                    f"Plan step count ({len(active_plan.steps)}) exceeded maximum limit ({self.max_plan_steps}).",
                    OrchestrationEventType.LIMIT_REACHED,
                )

            # Validate Plan
            report = await self.planner_service.validator.validate_plan(active_plan, agent=agent, task=task)
            self._add_event(
                execution, OrchestrationEventType.PLAN_VALIDATED, {"valid": report.valid, "plan_id": active_plan.plan_id}
            )

            if not report.valid:
                return await self._fail_execution(
                    execution,
                    task,
                    f"Plan validation failed: {'; '.join(report.errors[:2])}",
                    OrchestrationEventType.EXECUTION_FAILED,
                )

            execution.plan_id = active_plan.plan_id
            await self.planner_service.plan_repo.save_plan(active_plan)

            # 3. EXECUTE PLAN STEPS
            self._add_event(execution, OrchestrationEventType.PLAN_STARTED, {"plan_id": active_plan.plan_id})
            executed_plan = await self.planner_service.executor.execute_plan(
                plan=active_plan,
                agent=agent,
                task=task,
                actor=actor,
                context=ctx,
            )

            execution.tool_call_count += len(executed_plan.steps)
            if execution.tool_call_count > self.max_tool_calls:
                return await self._fail_execution(
                    execution,
                    task,
                    f"Tool call count ({execution.tool_call_count}) exceeded safety limit ({self.max_tool_calls}).",
                    OrchestrationEventType.LIMIT_REACHED,
                )

            # Handle step outcome status
            if executed_plan.status == PlanStatus.WAITING_APPROVAL:
                execution.state = ExecutionState.WAITING_APPROVAL
                await self.task_manager.task_service.repository.save(task)
                self._add_event(execution, OrchestrationEventType.WAITING_APPROVAL, {"plan_id": executed_plan.plan_id})
                return execution

            if executed_plan.status == PlanStatus.FAILED:
                return await self._fail_execution(
                    execution,
                    task,
                    executed_plan.failure_reason or "Plan execution failed.",
                    OrchestrationEventType.EXECUTION_FAILED,
                )

            # 4. UPDATE MEMORY
            if executed_plan.status == PlanStatus.COMPLETED:
                await self.memory_service.record_memory(
                    organization_id=agent.organization_id,
                    agent_id=agent.agent_id,
                    task_id=task.task_id,
                    content=f"Successfully executed plan '{executed_plan.plan_id}' for goal: {task.goal}",
                    memory_type=MemoryType.DECISION,
                )

                await self.task_manager.complete_task(
                    agent.organization_id,
                    task.task_id,
                    result={"final_response": f"Plan '{executed_plan.plan_id}' executed successfully."},
                )

                execution.state = ExecutionState.COMPLETED
                execution.completed_at = datetime.now(tz=UTC)
                self._add_event(execution, OrchestrationEventType.EXECUTION_COMPLETED, {"plan_id": executed_plan.plan_id})
                return execution

        # Exceeded iteration limit
        return await self._fail_execution(
            execution,
            task,
            f"Exceeded maximum reasoning iterations ({self.max_iterations}).",
            OrchestrationEventType.LIMIT_REACHED,
        )

    async def _fail_execution(
        self,
        execution: AgentExecution,
        task: AgentTask,
        reason: str,
        event_type: OrchestrationEventType,
    ) -> AgentExecution:
        execution.state = ExecutionState.FAILED
        execution.failure_reason = reason
        await self.task_manager.fail_task(task.organization_id, task.task_id, reason=reason)
        self._add_event(execution, event_type, {"reason": reason})
        return execution

    def _add_event(
        self,
        execution: AgentExecution,
        event_type: OrchestrationEventType,
        payload: dict[str, Any],
    ) -> None:
        evt = AgentExecutionEvent(
            execution_id=execution.execution_id,
            organization_id=execution.organization_id,
            agent_id=execution.agent_id,
            task_id=execution.task_id,
            event_type=event_type,
            payload=payload,
        )
        execution.events.append(evt)
