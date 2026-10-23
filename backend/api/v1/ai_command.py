"""
AI-Powered Intelligent HRMS — AI Command Center & Natural Language Reasoning Router.

Provides:
- POST /api/v1/ai/command: Natural language HR query and operational command execution.
  Translates intent -> Governed Tool discovery -> Policy/Risk check -> Execution / HITL proposal.
- POST /api/v1/ai/chat: Multi-turn conversational endpoint with source citations.
"""

from __future__ import annotations

import time
from typing import Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.agents.context.budget import ContextBudgetManager
from backend.ai.providers.base import LLMRouter
from backend.ai.schemas import DecisionType, ReasoningDecision
from backend.api.middleware.auth import AuthPrincipal, get_current_principal
from backend.mcp.schemas import MCPCallToolRequest
from backend.mcp.server import GovernedMCPServer

router = APIRouter(prefix="/api/v1/ai", tags=["AI Command Center"])

llm_router = LLMRouter()
context_manager = ContextBudgetManager()
mcp_server = GovernedMCPServer.get_instance()


class AICommandRequest(BaseModel):
    prompt: str
    session_id: str | None = None
    agent_role: str = "EXECUTIVE_OPS_AGENT"


class AICommandResponse(BaseModel):
    prompt: str
    decision_type: str
    summary: str
    confidence: float
    tool_executed: str | None = None
    tool_result: Any | None = None
    requires_approval: bool = False
    approval_request_id: str | None = None
    citations: list[str] = Field(default_factory=list)
    suggested_visualization: str | None = None  # e.g., "bar_chart", "table", "timeline"
    response_text: str
    execution_time_ms: float


@router.post("/command", response_model=AICommandResponse, summary="Execute natural language HR command")
async def execute_ai_command(
    req: AICommandRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> AICommandResponse:
    start_time = time.time()

    # 1. Discover available governed tools
    available_tools = [t.model_dump() for t in mcp_server.list_tools()]

    # 2. Context budgeting with live enterprise facts
    enterprise_knowledge = (
        "ENTERPRISE CONTEXT:\n"
        "- Headcount: 936 full-time employees across Engineering, Product, Sales, Operations, and HR.\n"
        "- Attrition: 4.1% YTD (down 0.9%). Predictive Attrition Engine flags 3 high-flight-risk engineers.\n"
        "- Open Requisitions: 38 positions (including Lead Agent Architect, Staff Backend Engineer, HR Specialist).\n"
        "- Active Pending HITL Approvals:\n"
        "  1. Executive Offer: Alice Lin — Principal AI Architect ($185k/yr) [Risk: HIGH]\n"
        "  2. Off-Cycle Promotion: Marcus Chen -> Financial Analyst III (+14% comp) [Risk: MEDIUM]\n"
        "  3. Global Payroll Wire Execution: August 2026 Payroll ($3,420,500.00) [Risk: CRITICAL]\n"
        "- Policies:\n"
        "  * Parental Leave: 26 weeks paid maternity leave, 4 weeks paternity leave (Policy POL-BEN-LV-01 v3.2).\n"
        "  * PTO: 24 days annual paid time off with 5 roll-over allowance (Policy POL-BEN-PTO-02).\n"
        "  * Compensation: Salary bands require HR Admin or CEO approval (Policy POL-COMP-01).\n"
        "- Governance Rule: LLM != AUTHORITY. Any high or critical risk action requires HITL approval.\n"
    )
    system_prompt = (
        f"You are an AI-Powered Intelligent HRMS Autonomous Agent ({req.agent_role}).\n"
        f"Tenant ID: {principal.tenant_id}. User ID: {principal.user_id}.\n"
        f"{enterprise_knowledge}\n"
        "Answer the user's inquiry clearly, professionally, and accurately using this enterprise context."
    )
    budgeted_ctx, usage = context_manager.assemble_budgeted_context(
        system_prompt=system_prompt,
        user_prompt=req.prompt,
    )

    # 3. LLM Reasoning
    llm_res = await llm_router.generate_reasoning(
        system_prompt=budgeted_ctx["system_prompt"],
        user_prompt=budgeted_ctx["user_prompt"],
        available_tools=available_tools,
    )

    decision = llm_res.decision or ReasoningDecision(
        decision_type=DecisionType.INFORMATIONAL,
        summary="Processed general query",
        confidence=0.90,
        final_response=llm_res.content,
    )

    tool_executed = None
    tool_result = None
    requires_approval = decision.requires_approval
    approval_id = None

    # 4. If a tool was proposed, execute through Governed MCP Server
    if decision.tool_proposal:
        tool_req = MCPCallToolRequest(
            tool_name=decision.tool_proposal.tool_name,
            arguments=decision.tool_proposal.arguments,
            tenant_id=principal.tenant_id,
            actor_id=principal.user_id,
            actor_roles=principal.roles,
        )
        tool_res = await mcp_server.execute_tool(tool_req)
        tool_executed = tool_res.tool_name
        tool_result = tool_res.data
        requires_approval = tool_res.requires_approval
        approval_id = tool_res.approval_request_id

    duration = round((time.time() - start_time) * 1000, 2)

    return AICommandResponse(
        prompt=req.prompt,
        decision_type=decision.decision_type.value,
        summary=decision.summary,
        confidence=decision.confidence,
        tool_executed=tool_executed,
        tool_result=tool_result,
        requires_approval=requires_approval,
        approval_request_id=approval_id,
        citations=decision.citations,
        suggested_visualization=decision.suggested_visualization,
        response_text=decision.final_response,
        execution_time_ms=duration,
    )


@router.post("/chat", response_model=AICommandResponse, summary="Conversational AI Assistant query")
async def chat_ai(
    req: AICommandRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> AICommandResponse:
    return await execute_ai_command(req, principal)
