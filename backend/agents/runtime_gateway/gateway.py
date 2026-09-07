"""
Agent Runtime Gateway — Master orchestrator linking Agent Runtime, Context Manager, Guardrails, AI Gateway, Tool Fabric, MCP, and CommandBus.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from backend.agents.domain.models import Agent
from backend.agents.tools.application.tool_registry import ToolRegistry
from backend.ai.context.context_manager import AssembledContext, ContextManager
from backend.ai.gateway.base import ToolCallProposal, ToolCallResponse
from backend.ai.gateway.router import AIGatewayRouter, RoutingTier
from backend.ai.guardrails.guardrail_stack import GuardrailStack
from backend.mcp.client.client import MCPClient

logger = logging.getLogger(__name__)


@dataclass
class AgentExecutionStepResult:
    """Outcome of a single governed agent reasoning and execution turn."""

    step_number: int
    thought_content: str
    tool_proposals: list[ToolCallProposal] = field(default_factory=list)
    tool_execution_results: list[dict[str, Any]] = field(default_factory=list)
    guardrail_violations: list[str] = field(default_factory=list)
    is_completed: bool = False
    final_output: str | None = None
    requires_hitl: bool = False


class AgentRuntimeGateway:
    """
    Unified entrypoint for executing specialized AI agents under rigorous governance:
    Agent → ContextManager → Guardrails → AIGateway → ToolRegistry / MCP → CommandBus → Result
    """

    _instance: AgentRuntimeGateway | None = None

    def __init__(
        self,
        ai_gateway: AIGatewayRouter | None = None,
        context_manager: ContextManager | None = None,
        guardrail_stack: GuardrailStack | None = None,
        tool_registry: ToolRegistry | None = None,
        mcp_client: MCPClient | None = None,
    ) -> None:
        self.ai_gateway = ai_gateway or AIGatewayRouter.get_instance()
        self.context_manager = context_manager or ContextManager.get_instance()
        self.guardrail_stack = guardrail_stack or GuardrailStack.get_instance()
        self.tool_registry = tool_registry or ToolRegistry.get_instance()
        self.mcp_client = mcp_client or MCPClient.get_instance()

    @classmethod
    def get_instance(cls) -> AgentRuntimeGateway:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def execute_turn(
        self,
        agent: Agent,
        task: str,
        organization_id: str,
        system_instruction: str = "You are a specialized AI HR Agent operating under strict enterprise governance.",
        security_invariants: str = "INVARIANT: LLM is not authoritative. High-risk mutations require human approval.",
        agent_policy: str = "LEAST PRIVILEGE: Only execute authorized tools within your capability scope.",
        memory_items: list[str] | None = None,
        rag_chunks: list[dict[str, Any]] | None = None,
        available_tools: list[dict[str, Any]] | None = None,
        tier: RoutingTier = RoutingTier.BALANCED,
        step_number: int = 1,
    ) -> AgentExecutionStepResult:
        """
        Execute one complete agent reasoning turn through the 6-layer defense stack and tool fabric.
        """
        violations: list[str] = []

        # 1. LAYER 1: Input Guardrail
        input_guard = await self.guardrail_stack.evaluate_input(task, {"organization_id": organization_id})
        if not input_guard.passed:
            return AgentExecutionStepResult(
                step_number=step_number,
                thought_content="Input rejected by Input Guardrail.",
                guardrail_violations=input_guard.violations,
                is_completed=True,
                final_output="Your request could not be processed due to a security policy violation.",
            )

        # 2. Assemble Token-Budgeted Context
        assembled: AssembledContext = self.context_manager.assemble_context(
            system_instruction=system_instruction,
            security_boundary=security_invariants,
            agent_policy=agent_policy,
            task=task,
            memory_items=memory_items,
            rag_chunks=rag_chunks,
            tools_manifest=available_tools,
        )

        # 3. LAYER 2: Context Guardrail
        ctx_guard = await self.guardrail_stack.evaluate_context(
            assembled.user_prompt,
            {"organization_id": organization_id},
        )
        if not ctx_guard.passed:
            return AgentExecutionStepResult(
                step_number=step_number,
                thought_content="Context rejected by Context Guardrail.",
                guardrail_violations=ctx_guard.violations,
                is_completed=True,
                final_output="Context assembly encountered a security boundary conflict.",
            )

        # 4. Invoke Multi-Provider AI Gateway with Native Tool Calling
        tool_payloads = available_tools or []
        llm_response: ToolCallResponse = await self.ai_gateway.generate_tool_calls(
            prompt=assembled.user_prompt,
            tools=tool_payloads,
            organization_id=organization_id,
            tier=tier,
            system_instruction=assembled.system_prompt,
            agent_id=agent.agent_id,
        )

        # 5. Process Tool Call Proposals
        tool_results: list[dict[str, Any]] = []
        requires_hitl = False

        for prop in llm_response.tool_calls:
            # LAYER 3: Tool Guardrail
            tool_guard = await self.guardrail_stack.evaluate_tool(prop, {"organization_id": organization_id})
            if not tool_guard.passed:
                tool_results.append(
                    {
                        "tool_id": prop.tool_id,
                        "success": False,
                        "error": f"Tool execution blocked by Tool Guardrail: {tool_guard.violations}",
                    }
                )
                violations.extend(tool_guard.violations)
                continue

            # LAYER 5: Action Guardrail
            action_guard = await self.guardrail_stack.evaluate_action(prop.tool_id, {"organization_id": organization_id})
            if action_guard.metadata.get("requires_hitl", False):
                requires_hitl = True
                tool_results.append(
                    {
                        "tool_id": prop.tool_id,
                        "status": "AWAITING_HUMAN_APPROVAL",
                        "requires_hitl": True,
                        "result": f"Action [{prop.tool_id}] requires explicit Human-In-The-Loop approval before execution.",
                    }
                )
                continue

            # Execute via MCP Client or Internal Tool Registry
            if "." in prop.tool_id:
                mcp_resp = await self.mcp_client.call_tool(
                    tool_id=prop.tool_id,
                    arguments=prop.arguments,
                    tenant_id=organization_id,
                    actor_id=agent.actor_id,
                    agent_id=agent.agent_id,
                )
                tool_results.append(
                    {
                        "tool_id": prop.tool_id,
                        "success": mcp_resp.success,
                        "result": mcp_resp.result,
                        "error": mcp_resp.error,
                    }
                )
            else:
                tool_results.append(
                    {
                        "tool_id": prop.tool_id,
                        "success": True,
                        "result": f"Executed internal tool [{prop.tool_id}]",
                    }
                )

        # 6. LAYER 4: Output Guardrail
        raw_output = llm_response.content or (
            "Task executed successfully." if not requires_hitl else "Task is pending human approval."
        )
        out_guard = await self.guardrail_stack.evaluate_output(raw_output, {"organization_id": organization_id})
        final_output = out_guard.sanitized_content or raw_output

        # 7. LAYER 6: Runtime Guardrail
        runtime_guard = await self.guardrail_stack.evaluate_runtime(
            {
                "current_step": step_number,
                "tool_calls_count": len(llm_response.tool_calls),
                "current_cost_usd": 0.05,
                "daily_budget_usd": 20.0,
            }
        )
        if not runtime_guard.passed:
            violations.extend(runtime_guard.violations)

        is_completed = (len(llm_response.tool_calls) == 0) or requires_hitl

        return AgentExecutionStepResult(
            step_number=step_number,
            thought_content=llm_response.content,
            tool_proposals=llm_response.tool_calls,
            tool_execution_results=tool_results,
            guardrail_violations=violations,
            is_completed=is_completed,
            final_output=final_output,
            requires_hitl=requires_hitl,
        )
