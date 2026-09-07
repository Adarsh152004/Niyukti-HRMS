"""
API v1 — AI Agent Management & Task Execution Endpoints (`/api/v1/agents`).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.agents.application.agent_registry import AgentRegistry
from backend.agents.application.agent_service import AgentService
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import AgentType, TaskPriority
from backend.agents.domain.models import AgentCapability
from backend.agents.infrastructure.database.repositories import InMemoryAgentRepository, InMemoryAgentTaskRepository
from backend.api.response import error_response, success_response
from backend.hrms.domain.actor import Actor
from backend.security.api.dependencies import get_current_actor

router = APIRouter(prefix="/api/v1/agents", tags=["AI Agents"])

# Singletons for API layer
_agent_repo = InMemoryAgentRepository()
_task_repo = InMemoryAgentTaskRepository()
_registry = AgentRegistry(repository=_agent_repo)
_agent_service = AgentService(registry=_registry)
_task_service = AgentTaskService(repository=_task_repo)


class CreateAgentRequest(BaseModel):
    name: str
    display_name: str
    description: str = ""
    agent_type: str = "CUSTOM_AGENT"
    capabilities: list[dict[str, Any]] = Field(default_factory=list)
    actor_id: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateTaskRequest(BaseModel):
    goal: str
    description: str = ""
    priority: str = "NORMAL"
    input_payload: dict[str, Any] = Field(default_factory=dict)


@router.post("", summary="Register AI Agent")
async def create_agent(
    req: CreateAgentRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        caps = [AgentCapability(**c) for c in req.capabilities]
        agent = await _agent_service.create_agent(
            organization_id=actor.organization_id,
            name=req.name,
            display_name=req.display_name,
            description=req.description,
            agent_type=AgentType(req.agent_type),
            capabilities=caps,
            actor_id=req.actor_id,
            metadata=req.metadata,
        )
        return success_response(data=agent.model_dump(), status_code=status.HTTP_201_CREATED)
    except Exception as e:
        return error_response(code="AGENT_CREATION_FAILED", message=str(e), status_code=400)


@router.get("", summary="List AI Agents")
async def list_agents(
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    agents = await _registry.list_agents(actor.organization_id)
    return success_response(data={"agents": [a.model_dump() for a in agents]})


@router.get("/{agent_id}", summary="Get AI Agent Details")
async def get_agent(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        agent = await _registry.get_agent(actor.organization_id, agent_id)
        return success_response(data=agent.model_dump())
    except Exception as e:
        return error_response(code="AGENT_NOT_FOUND", message=str(e), status_code=404)


@router.post("/{agent_id}/activate", summary="Activate AI Agent")
async def activate_agent(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        agent = await _agent_service.activate_agent(actor.organization_id, agent_id)
        return success_response(data=agent.model_dump())
    except Exception as e:
        return error_response(code="ACTIVATION_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/pause", summary="Pause AI Agent")
async def pause_agent(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        agent = await _agent_service.pause_agent(actor.organization_id, agent_id)
        return success_response(data=agent.model_dump())
    except Exception as e:
        return error_response(code="PAUSE_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/suspend", summary="Suspend AI Agent")
async def suspend_agent(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        agent = await _agent_service.suspend_agent(actor.organization_id, agent_id)
        return success_response(data=agent.model_dump())
    except Exception as e:
        return error_response(code="SUSPEND_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/disable", summary="Disable AI Agent")
async def disable_agent(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        agent = await _agent_service.disable_agent(actor.organization_id, agent_id)
        return success_response(data=agent.model_dump())
    except Exception as e:
        return error_response(code="DISABLE_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/terminate", summary="Terminate AI Agent")
async def terminate_agent(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        agent = await _agent_service.terminate_agent(actor.organization_id, agent_id)
        return success_response(data=agent.model_dump())
    except Exception as e:
        return error_response(code="TERMINATE_FAILED", message=str(e), status_code=400)


# Agent Task Endpoints
@router.post("/{agent_id}/tasks", summary="Create Agent Task")
async def create_task(
    agent_id: str,
    req: CreateTaskRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        task = await _task_service.create_task(
            organization_id=actor.organization_id,
            agent_id=agent_id,
            goal=req.goal,
            description=req.description,
            priority=TaskPriority(req.priority),
            input_payload=req.input_payload,
        )
        return success_response(data=task.model_dump(), status_code=status.HTTP_201_CREATED)
    except Exception as e:
        return error_response(code="TASK_CREATION_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/tasks", summary="List Agent Tasks")
async def list_tasks(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    tasks = await _task_service.list_tasks_for_agent(actor.organization_id, agent_id)
    return success_response(data={"tasks": [t.model_dump() for t in tasks]})


@router.get("/{agent_id}/tasks/{task_id}", summary="Get Agent Task Details")
async def get_task(
    agent_id: str,
    task_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    task = await _task_service.get_task(actor.organization_id, task_id)
    if not task or task.agent_id != agent_id:
        return error_response(code="TASK_NOT_FOUND", message="Agent task not found.", status_code=404)
    return success_response(data=task.model_dump())


# Intelligence Layer Endpoints
@router.get("/{agent_id}/tools", summary="Discover Discovered Tools for Agent")
async def discover_agent_tools(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.application.execution_context import AgentExecutionContextFactory
        from backend.agents.tools.application.tool_discovery import ToolDiscovery
        from backend.agents.tools.infrastructure.builtin_tools import register_builtin_tools

        register_builtin_tools()
        agent = await _registry.get_agent(actor.organization_id, agent_id)
        dummy_task = await _task_service.create_task(
            organization_id=actor.organization_id,
            agent_id=agent_id,
            goal="Tool discovery",
        )
        ctx = AgentExecutionContextFactory.create_context(agent, dummy_task, actor=actor)
        discovery = ToolDiscovery()
        tools = discovery.discover_tools(agent, ctx)
        return success_response(data={"tools": [t.model_dump() for t in tools]})
    except Exception as e:
        return error_response(code="TOOL_DISCOVERY_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/memory", summary="Get Recent Memories for Agent")
async def get_agent_memories(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.memory.application.memory_service import MemoryService

        mem_service = MemoryService()
        memories = await mem_service.get_memories_for_agent(actor.organization_id, agent_id)
        return success_response(data={"memories": [m.model_dump() for m in memories]})
    except Exception as e:
        return error_response(code="MEMORY_FETCH_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/tasks/{task_id}/reasoning", summary="Trigger Autonomous Reasoning Loop for Task")
async def run_task_reasoning(
    agent_id: str,
    task_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.reasoning.application.reasoning_engine import ReasoningEngine

        agent = await _registry.get_agent(actor.organization_id, agent_id)
        task = await _task_service.get_task(actor.organization_id, task_id)
        if not task or task.agent_id != agent_id:
            return error_response(code="TASK_NOT_FOUND", message="Task not found.", status_code=404)

        engine = ReasoningEngine(agent_service=_agent_service, task_service=_task_service)
        run = await engine.run_task_reasoning(agent=agent, task=task, actor=actor)
        return success_response(data=run.model_dump())
    except Exception as e:
        return error_response(code="REASONING_FAILED", message=str(e), status_code=400)


# Autonomous Orchestration Endpoints
@router.post("/{agent_id}/tasks/{task_id}/run", summary="Run Task Autonomous Orchestration")
async def run_task_orchestration(
    agent_id: str,
    task_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.orchestration.application.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(registry=_registry, agent_service=_agent_service, task_service=_task_service)
        execution = await orchestrator.run_task(actor.organization_id, agent_id, task_id, actor=actor)
        return success_response(data=execution.model_dump())
    except Exception as e:
        return error_response(code="ORCHESTRATION_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/tasks/{task_id}/plan", summary="Get Active Task Plan")
async def get_task_plan(
    agent_id: str,
    task_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.planning.application.planner_service import PlannerService

        planner = PlannerService(agent_registry=_registry, task_service=_task_service)
        plan = await planner.get_plan_for_task(actor.organization_id, task_id)
        if not plan:
            return error_response(code="PLAN_NOT_FOUND", message="Plan not found.", status_code=404)
        return success_response(data=plan.model_dump())
    except Exception as e:
        return error_response(code="PLAN_FETCH_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/tasks/{task_id}/execution", summary="Get Task Execution Trajectory")
async def get_task_execution(
    agent_id: str,
    task_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.orchestration.application.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(registry=_registry, agent_service=_agent_service, task_service=_task_service)
        execution = await orchestrator.get_execution(actor.organization_id, task_id)
        if not execution:
            return error_response(code="EXECUTION_NOT_FOUND", message="Execution trajectory not found.", status_code=404)
        return success_response(data=execution.model_dump())
    except Exception as e:
        return error_response(code="EXECUTION_FETCH_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/tasks/{task_id}/pause", summary="Pause Task Execution")
async def pause_task_execution(
    agent_id: str,
    task_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.orchestration.application.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(registry=_registry, agent_service=_agent_service, task_service=_task_service)
        task = await orchestrator.pause_task(actor.organization_id, task_id)
        return success_response(data=task.model_dump())
    except Exception as e:
        return error_response(code="PAUSE_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/tasks/{task_id}/resume", summary="Resume Task Execution")
async def resume_task_execution(
    agent_id: str,
    task_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.orchestration.application.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(registry=_registry, agent_service=_agent_service, task_service=_task_service)
        execution = await orchestrator.resume_task(actor.organization_id, task_id, actor=actor)
        return success_response(data=execution.model_dump())
    except Exception as e:
        return error_response(code="RESUME_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/tasks/{task_id}/cancel", summary="Cancel Task Execution")
async def cancel_task_execution(
    agent_id: str,
    task_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.orchestration.application.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator(registry=_registry, agent_service=_agent_service, task_service=_task_service)
        task = await orchestrator.cancel_task(actor.organization_id, task_id)
        return success_response(data=task.model_dump())
    except Exception as e:
        return error_response(code="CANCEL_FAILED", message=str(e), status_code=400)


# ==========================================
# MULTI-AGENT DELEGATION ENDPOINTS
# ==========================================


class CreateDelegationRequest(BaseModel):
    delegate_agent_id: str
    parent_task_id: str
    requested_capabilities: list[dict[str, Any]]
    ttl_hours: int = 2
    allow_further_delegation: bool = False
    parent_delegation_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DelegationActionRequest(BaseModel):
    reason: str = "User requested action"


@router.post("/{agent_id}/delegations", summary="Create Agent Delegation")
async def create_delegation(
    agent_id: str,
    req: CreateDelegationRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from datetime import UTC, datetime, timedelta

        from backend.agents.delegation.application.delegation_service import DelegationService

        del_service = DelegationService(agent_service=_agent_service)
        expires_at = datetime.now(tz=UTC) + timedelta(hours=req.ttl_hours)
        caps = [AgentCapability(**c) for c in req.requested_capabilities]

        delegation = await del_service.create_delegation(
            organization_id=actor.organization_id,
            delegator_agent_id=agent_id,
            delegate_agent_id=req.delegate_agent_id,
            parent_task_id=req.parent_task_id,
            requested_capabilities=caps,
            expires_at=expires_at,
            allow_further_delegation=req.allow_further_delegation,
            parent_delegation_id=req.parent_delegation_id,
            metadata=req.metadata,
        )
        return success_response(data=delegation.model_dump(), status_code=status.HTTP_201_CREATED)
    except Exception as e:
        return error_response(code="DELEGATION_CREATE_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/delegations", summary="List Agent Delegations")
async def list_agent_delegations(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.delegation.application.delegation_service import DelegationService

        del_service = DelegationService(agent_service=_agent_service)
        delegations = await del_service.list_delegations(actor.organization_id, delegator_agent_id=agent_id)
        return success_response(data={"delegations": [d.model_dump() for d in delegations]})
    except Exception as e:
        return error_response(code="DELEGATION_LIST_FAILED", message=str(e), status_code=400)


@router.get("/delegations/{delegation_id}", summary="Get Delegation Details")
async def get_delegation_details(
    delegation_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.delegation.application.delegation_service import DelegationService

        del_service = DelegationService(agent_service=_agent_service)
        delegation = await del_service.get_delegation(actor.organization_id, delegation_id)
        if not delegation:
            return error_response(code="DELEGATION_NOT_FOUND", message="Delegation not found.", status_code=404)
        return success_response(data=delegation.model_dump())
    except Exception as e:
        return error_response(code="DELEGATION_FETCH_FAILED", message=str(e), status_code=400)


@router.post("/delegations/{delegation_id}/approve", summary="Approve Delegation Request")
async def approve_delegation(
    delegation_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.delegation.application.delegation_service import DelegationService

        del_service = DelegationService(agent_service=_agent_service)
        delegation = await del_service.approve_delegation(actor.organization_id, delegation_id, approver_actor=actor)
        return success_response(data=delegation.model_dump())
    except Exception as e:
        return error_response(code="DELEGATION_APPROVE_FAILED", message=str(e), status_code=400)


@router.post("/delegations/{delegation_id}/reject", summary="Reject Delegation Request")
async def reject_delegation(
    delegation_id: str,
    req: DelegationActionRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.delegation.application.delegation_service import DelegationService

        del_service = DelegationService(agent_service=_agent_service)
        delegation = await del_service.reject_delegation(actor.organization_id, delegation_id, reason=req.reason)
        return success_response(data=delegation.model_dump())
    except Exception as e:
        return error_response(code="DELEGATION_REJECT_FAILED", message=str(e), status_code=400)


@router.post("/delegations/{delegation_id}/revoke", summary="Revoke Active Delegation")
async def revoke_delegation(
    delegation_id: str,
    req: DelegationActionRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.delegation.application.delegation_service import DelegationService

        del_service = DelegationService(agent_service=_agent_service)
        delegation = await del_service.revoke_delegation(actor.organization_id, delegation_id, reason=req.reason)
        return success_response(data=delegation.model_dump())
    except Exception as e:
        return error_response(code="DELEGATION_REVOKE_FAILED", message=str(e), status_code=400)


@router.post("/delegations/{delegation_id}/cancel", summary="Cancel Delegation")
async def cancel_delegation(
    delegation_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.delegation.application.delegation_service import DelegationService

        del_service = DelegationService(agent_service=_agent_service)
        delegation = await del_service.cancel_delegation(actor.organization_id, delegation_id)
        return success_response(data=delegation.model_dump())
    except Exception as e:
        return error_response(code="DELEGATION_CANCEL_FAILED", message=str(e), status_code=400)


# ==========================================
# AGENT GOVERNANCE & OBSERVABILITY ENDPOINTS
# ==========================================


class UpdateGovernancePolicyRequest(BaseModel):
    max_reasoning_steps: int | None = None
    max_tool_calls: int | None = None
    auto_quarantine: bool | None = None
    governance_state: str | None = None


class UpdateBudgetRequest(BaseModel):
    max_token_budget: int | None = None
    max_tool_calls: int | None = None
    max_reasoning_runs: int | None = None
    max_command_executions: int | None = None


@router.get("/{agent_id}/governance/status", summary="Get Agent Governance Status")
async def get_governance_status(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.governance_policy_service import GovernancePolicyService

        gov_service = GovernancePolicyService()
        policy = await gov_service.get_or_create_policy(actor.organization_id, agent_id)
        return success_response(data=policy.model_dump())
    except Exception as e:
        return error_response(code="GOVERNANCE_FETCH_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/governance/budget", summary="Get Agent Budget & Quotas")
async def get_agent_budget(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.budget_service import BudgetService

        budget_service = BudgetService()
        budget = await budget_service.get_or_create_budget(actor.organization_id, agent_id)
        return success_response(data=budget.model_dump())
    except Exception as e:
        return error_response(code="BUDGET_FETCH_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/governance/violations", summary="Get Agent Governance Violations")
async def get_agent_violations(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.governance_policy_service import GovernancePolicyService

        gov_service = GovernancePolicyService()
        violations = await gov_service.list_violations(actor.organization_id, agent_id)
        return success_response(data={"violations": [v.model_dump() for v in violations]})
    except Exception as e:
        return error_response(code="VIOLATIONS_FETCH_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/governance/ledger", summary="Get Agent Execution Ledger Entries")
async def get_execution_ledger(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
    task_id: str | None = None,
) -> JSONResponse:
    try:
        from backend.agents.governance.application.execution_ledger_service import ExecutionLedgerService

        ledger_service = ExecutionLedgerService()
        entries = await ledger_service.list_ledger_entries(actor.organization_id, agent_id, task_id=task_id)
        return success_response(data={"ledger_entries": [e.model_dump() for e in entries]})
    except Exception as e:
        return error_response(code="LEDGER_FETCH_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/governance/metrics", summary="Get Agent Observability Metrics")
async def get_agent_metrics(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.observability_service import AgentObservabilityService

        obs_service = AgentObservabilityService()
        metrics = await obs_service.get_agent_metrics(actor.organization_id, agent_id)
        return success_response(data=metrics)
    except Exception as e:
        return error_response(code="METRICS_FETCH_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/governance/policy", summary="Update Governance Policy (Human Admin Only)")
async def update_governance_policy(
    agent_id: str,
    req: UpdateGovernancePolicyRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.governance_policy_service import GovernancePolicyService
        from backend.agents.governance.domain.enums import GovernanceState

        gov_service = GovernancePolicyService()
        state_enum = GovernanceState(req.governance_state) if req.governance_state else None
        policy = await gov_service.update_policy(
            organization_id=actor.organization_id,
            agent_id=agent_id,
            actor=actor,
            max_reasoning_steps=req.max_reasoning_steps,
            max_tool_calls=req.max_tool_calls,
            auto_quarantine=req.auto_quarantine,
            governance_state=state_enum,
        )
        return success_response(data=policy.model_dump())
    except Exception as e:
        return error_response(code="POLICY_UPDATE_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/governance/budget", summary="Update Agent Budget (Human Admin Only)")
async def update_agent_budget(
    agent_id: str,
    req: UpdateBudgetRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.budget_service import BudgetService

        budget_service = BudgetService()
        budget = await budget_service.update_budget(
            organization_id=actor.organization_id,
            agent_id=agent_id,
            actor=actor,
            max_token_budget=req.max_token_budget,
            max_tool_calls=req.max_tool_calls,
            max_reasoning_runs=req.max_reasoning_runs,
            max_command_executions=req.max_command_executions,
        )
        return success_response(data=budget.model_dump())
    except Exception as e:
        return error_response(code="BUDGET_UPDATE_FAILED", message=str(e), status_code=400)


# ==========================================
# SAFETY CONTROL PLANE ENDPOINTS
# ==========================================


class ContainAgentRequest(BaseModel):
    action: str = Field(description="WARN, THROTTLE, PAUSE, SUSPEND, DISABLE, TERMINATE")
    reason: str = Field(default="Administrative containment action")


class EvaluateTaskRequest(BaseModel):
    task_id: str


@router.get("/{agent_id}/governance", summary="Get Full Agent Governance & Safety Status")
async def get_full_governance_status(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.governance_service import GovernanceService

        gov_service = GovernanceService()
        policy = await gov_service.get_governance_policy(actor.organization_id, agent_id)
        return success_response(data=policy.model_dump())
    except Exception as e:
        return error_response(code="GOVERNANCE_FETCH_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/audit", summary="Get Agent Audit Trail")
async def get_agent_audit_trail(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
    task_id: str | None = None,
) -> JSONResponse:
    try:
        from backend.agents.governance.application.audit_service import AuditService

        audit_service = AuditService()
        records = await audit_service.list_audit_records(actor.organization_id, agent_id, task_id=task_id)
        return success_response(data={"audit_records": [r.model_dump() for r in records]})
    except Exception as e:
        return error_response(code="AUDIT_FETCH_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/metrics", summary="Get Agent Operational Metrics")
async def get_agent_metrics_summary(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.metrics_service import MetricsService

        metrics_service = MetricsService()
        summary = await metrics_service.get_metrics_summary(actor.organization_id, agent_id=agent_id)
        return success_response(data=summary)
    except Exception as e:
        return error_response(code="METRICS_FETCH_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/evaluations", summary="Get Agent Task Trajectory Evaluations")
async def get_agent_evaluations(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
    task_id: str | None = None,
) -> JSONResponse:
    try:
        from backend.agents.governance.application.evaluation_service import EvaluationService

        eval_service = EvaluationService()
        evaluations = await eval_service.list_evaluations(actor.organization_id, agent_id, task_id=task_id)
        return success_response(data={"evaluations": [e.model_dump() for e in evaluations]})
    except Exception as e:
        return error_response(code="EVALUATIONS_FETCH_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/anomalies", summary="Get Detected Agent Anomalies")
async def get_agent_anomalies(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
    status: str | None = None,
) -> JSONResponse:
    try:
        from backend.agents.governance.application.anomaly_service import AnomalyService

        anomaly_service = AnomalyService()
        anomalies = await anomaly_service.list_anomalies(actor.organization_id, agent_id, status=status)
        return success_response(data={"anomalies": [a.model_dump() for a in anomalies]})
    except Exception as e:
        return error_response(code="ANOMALIES_FETCH_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/evaluate", summary="Evaluate Agent Task Trajectory")
async def evaluate_agent_task(
    agent_id: str,
    req: EvaluateTaskRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.governance_service import GovernanceService

        gov_service = GovernanceService()
        evaluation = await gov_service.evaluate_task(actor.organization_id, agent_id, req.task_id)
        return success_response(data=evaluation.model_dump())
    except Exception as e:
        return error_response(code="TASK_EVALUATION_FAILED", message=str(e), status_code=400)


@router.get("/{agent_id}/governance/policies", summary="List Governance Policies")
async def get_agent_governance_policies(
    agent_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.governance_service import GovernanceService

        gov_service = GovernanceService()
        policy = await gov_service.get_governance_policy(actor.organization_id, agent_id)
        return success_response(data={"policies": [policy.model_dump()]})
    except Exception as e:
        return error_response(code="POLICIES_FETCH_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/governance/policies", summary="Create or Update Governance Policy")
async def create_or_update_governance_policy(
    agent_id: str,
    req: UpdateGovernancePolicyRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.policy_service import GovernancePolicyService
        from backend.agents.governance.domain.enums import GovernanceState

        policy_service = GovernancePolicyService()
        state_enum = GovernanceState(req.governance_state) if req.governance_state else None
        policy = await policy_service.update_policy(
            organization_id=actor.organization_id,
            agent_id=agent_id,
            actor=actor,
            max_reasoning_steps=req.max_reasoning_steps,
            max_tool_calls=req.max_tool_calls,
            auto_quarantine=req.auto_quarantine,
            governance_state=state_enum,
        )
        return success_response(data=policy.model_dump())
    except Exception as e:
        return error_response(code="POLICY_CREATE_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/contain", summary="Contain Agent (Human Admin Only)")
async def contain_agent(
    agent_id: str,
    req: ContainAgentRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.containment_service import ContainmentService
        from backend.agents.governance.domain.enums import ContainmentActionType

        contain_service = ContainmentService()
        action_enum = ContainmentActionType(req.action)
        action = await contain_service.execute_containment(
            organization_id=actor.organization_id,
            agent_id=agent_id,
            action_type=action_enum,
            reason=req.reason,
            triggered_by=actor,
        )
        return success_response(data=action.model_dump())
    except Exception as e:
        return error_response(code="CONTAINMENT_EXECUTION_FAILED", message=str(e), status_code=400)


@router.post("/{agent_id}/containment/{containment_id}/resolve", summary="Resolve Containment (Human Admin Only)")
async def resolve_containment(
    agent_id: str,
    containment_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        from backend.agents.governance.application.containment_service import ContainmentService

        contain_service = ContainmentService()
        resolved = await contain_service.resolve_containment(
            organization_id=actor.organization_id,
            agent_id=agent_id,
            containment_id=containment_id,
            resolver_actor=actor,
        )
        return success_response(data=resolved.model_dump())
    except Exception as e:
        return error_response(code="CONTAINMENT_RESOLUTION_FAILED", message=str(e), status_code=400)
