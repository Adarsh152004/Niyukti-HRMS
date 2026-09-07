"""
Specialized Agents FastAPI Router — Endpoints for inspecting declarative blueprints and managing tenant agent instances.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.agents.specialized.application.agent_bootstrap import BootstrapResult
from backend.agents.specialized.application.specialization_service import SpecializedAgentService
from backend.agents.specialized.domain.exceptions import (
    AgentSpecializationNotFoundError,
)
from backend.agents.specialized.domain.models import (
    CapabilityProfile,
    EvaluationContract,
    KnowledgePolicy,
    MemoryPolicy,
    SpecializedAgentDefinition,
    SpecializedAgentInstance,
    ToolPolicy,
)
from backend.hrms.domain.actor import Actor
from backend.security.api.dependencies import get_current_actor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/specialized-agents", tags=["Specialized Agents"])


@router.get("", response_model=list[SpecializedAgentDefinition])
async def list_specialized_agents(
    actor: Actor = Depends(get_current_actor),
) -> list[SpecializedAgentDefinition]:
    """List all 24 declarative specialized AI HR agent definitions."""
    svc = SpecializedAgentService.get_instance()
    return svc.list_definitions()


@router.get("/instances", response_model=list[SpecializedAgentInstance])
async def list_tenant_agent_instances(
    actor: Actor = Depends(get_current_actor),
) -> list[SpecializedAgentInstance]:
    """List active specialized agent instances for the caller's organization."""
    svc = SpecializedAgentService.get_instance()
    return svc.list_tenant_instances(actor.organization_id)


@router.post("/bootstrap", response_model=BootstrapResult)
async def bootstrap_specialized_agents(
    actor: Actor = Depends(get_current_actor),
) -> BootstrapResult:
    """Idempotently bootstrap all 24 standard specialized agents for the tenant organization."""
    svc = SpecializedAgentService.get_instance()
    return svc.bootstrap_tenant(actor.organization_id)


@router.get("/{role}", response_model=SpecializedAgentDefinition)
async def get_specialized_agent(
    role: str,
    actor: Actor = Depends(get_current_actor),
) -> SpecializedAgentDefinition:
    """Get a specific specialized agent definition by role."""
    svc = SpecializedAgentService.get_instance()
    try:
        return svc.get_definition(role)
    except AgentSpecializationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{role}/capabilities", response_model=CapabilityProfile)
async def get_agent_capabilities(
    role: str,
    actor: Actor = Depends(get_current_actor),
) -> CapabilityProfile:
    """Get the capability profile for a specialized agent."""
    svc = SpecializedAgentService.get_instance()
    try:
        return svc.get_capabilities(role)
    except AgentSpecializationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{role}/tools", response_model=ToolPolicy)
async def get_agent_tool_policy(
    role: str,
    actor: Actor = Depends(get_current_actor),
) -> ToolPolicy:
    """Get the tool access policy matrix for a specialized agent."""
    svc = SpecializedAgentService.get_instance()
    try:
        return svc.get_tool_policy(role)
    except AgentSpecializationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{role}/knowledge", response_model=KnowledgePolicy)
async def get_agent_knowledge_policy(
    role: str,
    actor: Actor = Depends(get_current_actor),
) -> KnowledgePolicy:
    """Get the knowledge scope policy for a specialized agent."""
    svc = SpecializedAgentService.get_instance()
    try:
        return svc.get_knowledge_policy(role)
    except AgentSpecializationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{role}/memory-policy", response_model=MemoryPolicy)
async def get_agent_memory_policy(
    role: str,
    actor: Actor = Depends(get_current_actor),
) -> MemoryPolicy:
    """Get the memory tier access policy for a specialized agent."""
    svc = SpecializedAgentService.get_instance()
    try:
        return svc.get_memory_policy(role)
    except AgentSpecializationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{role}/evaluation-contract", response_model=EvaluationContract)
async def get_agent_evaluation_contract(
    role: str,
    actor: Actor = Depends(get_current_actor),
) -> EvaluationContract:
    """Get the evaluation SLA contract for a specialized agent."""
    svc = SpecializedAgentService.get_instance()
    try:
        return svc.get_evaluation_contract(role)
    except AgentSpecializationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
