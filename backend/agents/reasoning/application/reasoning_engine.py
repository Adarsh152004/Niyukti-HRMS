"""
Reasoning Engine — Core Bounded Autonomous Reasoning Loop.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime

from backend.agents.application.agent_service import AgentService
from backend.agents.application.execution_context import AgentExecutionContextFactory
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import AgentStatus, TaskStatus
from backend.agents.domain.exceptions import AgentSecurityError
from backend.agents.domain.models import Agent, AgentExecutionContext, AgentTask
from backend.agents.memory.application.context_builder import ContextBuilder
from backend.agents.memory.application.memory_service import MemoryService
from backend.agents.memory.domain.enums import MemoryType
from backend.agents.reasoning.application.decision_parser import DecisionParser
from backend.agents.reasoning.application.prompt_builder import PromptBuilder
from backend.agents.reasoning.domain.enums import DecisionType
from backend.agents.reasoning.domain.models import (
    LLMRequest,
    ReasoningDecision,
    ReasoningRun,
)
from backend.agents.reasoning.exceptions import ReasoningEngineError
from backend.agents.reasoning.providers.base import LLMProviderPort
from backend.agents.reasoning.providers.mock import MockLLMProvider
from backend.agents.tools.application.tool_gateway import ToolExecutionGateway
from backend.agents.tools.domain.models import ToolExecutionResult, ToolProposal
from backend.hrms.domain.actor import Actor
from backend.runtime.events import Event, EventBus


class ReasoningEngine:
    """
    Bounded Reasoning Engine executing autonomous loops for AI Agent Tasks.
    """

    def __init__(
        self,
        provider: LLMProviderPort | None = None,
        context_builder: ContextBuilder | None = None,
        tool_gateway: ToolExecutionGateway | None = None,
        memory_service: MemoryService | None = None,
        agent_service: AgentService | None = None,
        task_service: AgentTaskService | None = None,
        event_bus: EventBus | None = None,
        max_steps: int = 10,
    ) -> None:
        self.provider = provider or MockLLMProvider()
        self.context_builder = context_builder or ContextBuilder()
        self.tool_gateway = tool_gateway or ToolExecutionGateway()
        self.memory_service = memory_service or MemoryService()
        self.agent_service = agent_service or AgentService()
        self.task_service = task_service or AgentTaskService()
        self.event_bus = event_bus or EventBus.get_instance()
        self.max_steps = max_steps

    async def run_task_reasoning(
        self,
        agent: Agent,
        task: AgentTask,
        actor: Actor | None = None,
        context: AgentExecutionContext | None = None,
    ) -> ReasoningRun:
        """
        Execute bounded autonomous reasoning loop for an active AgentTask.
        """
        # 1. Enforce active Agent status
        if agent.status != AgentStatus.ACTIVE:
            raise AgentSecurityError(f"Agent '{agent.agent_id}' is not ACTIVE (status={agent.status.value}).")

        # 2. Enforce Tenant Isolation
        if agent.organization_id != task.organization_id:
            raise AgentSecurityError("Cross-tenant task reasoning rejected.")

        # 3. Create Execution Context
        ctx: AgentExecutionContext = context or AgentExecutionContextFactory.create_context(agent, task, actor=actor)

        # Mark task running
        if task.status == TaskStatus.QUEUED:
            task = await self.task_service.start_task(agent.organization_id, task.task_id)

        start_time = time.time()
        run = ReasoningRun(
            organization_id=agent.organization_id,
            agent_id=agent.agent_id,
            task_id=task.task_id,
            status="RUNNING",
        )

        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.reasoning.started",
                source=agent.actor_id,
                payload={"run_id": run.run_id, "task_id": task.task_id},
                correlation_id=task.correlation_id,
            )
        )

        tool_results_history: list[ToolExecutionResult] = []
        recent_proposals: set[tuple[str, str]] = set()  # (tool_id, json_args_str)

        step = 0
        while step < self.max_steps:
            step += 1
            run.step_count = step

            # Build bounded context
            bounded_ctx = await self.context_builder.build_context(
                agent=agent,
                task=task,
                context=ctx,
                tool_results=tool_results_history,
                step_number=step,
            )

            # Generate prompts
            sys_prompt = PromptBuilder.build_system_prompt(bounded_ctx)
            user_prompt = PromptBuilder.build_user_prompt(bounded_ctx)

            # Invoke provider
            request = LLMRequest(
                system_prompt=sys_prompt,
                user_prompt=user_prompt,
                tools=bounded_ctx.allowed_tools,
                step_number=step,
            )
            llm_response = await self.provider.generate(request)
            decision: ReasoningDecision = DecisionParser.parse_decision(llm_response)

            # Handle Decision Types
            if decision.decision_type in (DecisionType.ANSWER, DecisionType.COMPLETE):
                output_text = decision.final_response or decision.explanation or "Task completed."
                await self.task_service.complete_task(
                    organization_id=agent.organization_id,
                    task_id=task.task_id,
                    output={"final_response": output_text, "steps": step},
                )
                await self.memory_service.record_memory(
                    organization_id=agent.organization_id,
                    agent_id=agent.agent_id,
                    task_id=task.task_id,
                    memory_type=MemoryType.DECISION,
                    content=f"Task {task.task_id} completed: {output_text}",
                )
                run.status = "COMPLETED"
                break

            if decision.decision_type == DecisionType.FAIL:
                reason = decision.explanation or "LLM reported task failure."
                await self.task_service.fail_task(agent.organization_id, task.task_id, reason=reason)
                run.status = "FAILED"
                break

            if decision.decision_type == DecisionType.TOOL_CALL:
                if not decision.selected_tool:
                    raise ReasoningEngineError("TOOL_CALL decision omitted selected_tool.")

                # Check for repeated tool proposals (infinite loop prevention)
                prop_key = (decision.selected_tool, str(sorted(decision.tool_arguments.items())))
                if prop_key in recent_proposals:
                    # Repeated tool call detected - fail safely
                    await self.task_service.fail_task(
                        agent.organization_id,
                        task.task_id,
                        reason=f"Repeated tool call loop detected for '{decision.selected_tool}'.",
                    )
                    run.status = "FAILED"
                    break
                recent_proposals.add(prop_key)

                # Create and execute proposal
                proposal = ToolProposal(
                    tool_id=decision.selected_tool,
                    arguments=decision.tool_arguments,
                    reasoning_step_id=str(step),
                    correlation_id=task.correlation_id,
                )

                exec_result = await self.tool_gateway.execute_proposal(
                    agent=agent,
                    context=ctx,
                    proposal=proposal,
                    actor=actor,
                )
                tool_results_history.append(exec_result)

                # Check if tool resulted in HITL WAITING_APPROVAL
                if exec_result.status == "WAITING_APPROVAL":
                    task.transition_to(TaskStatus.WAITING_APPROVAL)
                    await self.task_service.repository.save(task)
                    run.status = "WAITING_APPROVAL"
                    break

                continue

            if decision.decision_type == DecisionType.REQUEST_APPROVAL:
                task.transition_to(TaskStatus.WAITING_APPROVAL)
                await self.task_service.repository.save(task)
                run.status = "WAITING_APPROVAL"
                break

        else:
            # Reached max_steps without completion
            reason = f"Exceeded maximum reasoning steps ({self.max_steps})."
            await self.task_service.fail_task(agent.organization_id, task.task_id, reason=reason)
            run.status = "FAILED"
            run.metadata["error"] = reason

        run.duration_ms = int((time.time() - start_time) * 1000)
        run.completed_at = datetime.now(tz=UTC)

        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.reasoning.completed",
                source=agent.actor_id,
                payload={"run_id": run.run_id, "status": run.status, "steps": run.step_count},
                correlation_id=task.correlation_id,
            )
        )
        return run
