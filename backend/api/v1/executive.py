"""
Executive Control Plane Router — Cockpit, Autonomy Matrix, Emergency Kill Switch, and Agent Quarantine.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.agents.specialized.domain.enums import AutonomyMode, SpecializedAgentRole
from backend.api.dependencies import get_executive_control_service, get_tenant_context
from backend.api.response import success_response
from backend.hrms.application.executive_control_service import ExecutiveControlService
from backend.hrms.application.tenant_context import TenantContext

router = APIRouter(prefix="/api/v1/executive", tags=["CEO / Handler Control Plane"])


class UpdateAutonomyRequest(BaseModel):
    agent_role: SpecializedAgentRole
    autonomy_mode: AutonomyMode


class KillSwitchRequest(BaseModel):
    reason: str


class QuarantineRequest(BaseModel):
    agent_role: SpecializedAgentRole
    reason: str


# 1. Executive Cockpit Summary
@router.get("/cockpit")
async def get_cockpit_summary(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ExecutiveControlService, Depends(get_executive_control_service)],
) -> JSONResponse:
    summary = await service.get_cockpit_summary(ctx.organization_id)
    return success_response(data=summary.model_dump())


# 2. Autonomy Matrix
@router.get("/autonomy-matrix")
async def get_autonomy_matrix(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ExecutiveControlService, Depends(get_executive_control_service)],
) -> JSONResponse:
    matrix = await service.get_autonomy_matrix(ctx.organization_id)
    return success_response(data=[m.model_dump() for m in matrix])


@router.put("/autonomy-matrix")
async def update_agent_autonomy(
    body: UpdateAutonomyRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ExecutiveControlService, Depends(get_executive_control_service)],
) -> JSONResponse:
    updated = await service.update_agent_autonomy(
        organization_id=ctx.organization_id,
        agent_role=body.agent_role,
        new_mode=body.autonomy_mode,
        updated_by=ctx.actor_id or "ceo-operator",
    )
    return success_response(data=updated.model_dump())


# 3. Emergency Kill Switch
@router.post("/kill-switch/activate")
async def activate_kill_switch(
    body: KillSwitchRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ExecutiveControlService, Depends(get_executive_control_service)],
) -> JSONResponse:
    state = await service.activate_kill_switch(
        organization_id=ctx.organization_id,
        reason=body.reason,
        triggered_by=ctx.actor_id or "ceo-operator",
    )
    return success_response(
        data={
            "is_active": state.is_active,
            "reason": state.reason,
            "activated_at": state.activated_at.isoformat() if state.activated_at else None,
        }
    )


@router.post("/kill-switch/deactivate")
async def deactivate_kill_switch(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ExecutiveControlService, Depends(get_executive_control_service)],
) -> JSONResponse:
    state = await service.deactivate_kill_switch(
        organization_id=ctx.organization_id,
        triggered_by=ctx.actor_id or "ceo-operator",
    )
    return success_response(data={"is_active": state.is_active})


# 4. Agent Quarantine
@router.post("/quarantine/freeze")
async def freeze_agent(
    body: QuarantineRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ExecutiveControlService, Depends(get_executive_control_service)],
) -> JSONResponse:
    record = await service.quarantine_agent(
        organization_id=ctx.organization_id,
        agent_role=body.agent_role,
        reason=body.reason,
        triggered_by=ctx.actor_id or "ceo-operator",
    )
    return success_response(
        data={"agent_role": record.agent_role.value, "reason": record.reason, "quarantined_at": record.quarantined_at.isoformat()}
    )


@router.post("/quarantine/unfreeze")
async def unfreeze_agent(
    agent_role: SpecializedAgentRole,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ExecutiveControlService, Depends(get_executive_control_service)],
) -> JSONResponse:
    success = await service.unquarantine_agent(
        organization_id=ctx.organization_id,
        agent_role=agent_role,
        triggered_by=ctx.actor_id or "ceo-operator",
    )
    return success_response(data={"unfrozen": success, "agent_role": agent_role.value})


# 5. System Health Telemetry
@router.get("/health")
async def get_system_health(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ExecutiveControlService, Depends(get_executive_control_service)],
) -> JSONResponse:
    health = await service.get_system_health(ctx.organization_id)
    return success_response(data=health)
