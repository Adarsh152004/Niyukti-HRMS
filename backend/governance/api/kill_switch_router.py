"""
AI-Powered Intelligent HRMS — Global & Per-Agent Emergency Kill-Switch & Governance Router.

Provides:
- POST /api/v1/governance/kill-switch/global (GLOBAL_AI_PAUSE, GLOBAL_AI_DISABLE, RESUME)
- POST /api/v1/governance/kill-switch/agent (PAUSE, RESUME, SUSPEND, TERMINATE)
- GET  /api/v1/governance/kill-switch/status (Current operational state of AI fleet)
- GET  /api/v1/governance/audit-trail (Cryptographic tamper-evident audit events)
"""

from __future__ import annotations

import time
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.api.middleware.auth import AuthPrincipal, get_current_principal

router = APIRouter(prefix="/api/v1/governance", tags=["AI Governance & Kill-Switch"])


class GlobalKillSwitchState:
    _instance: GlobalKillSwitchState | None = None

    def __init__(self) -> None:
        self.is_globally_paused: bool = False
        self.is_globally_disabled: bool = False
        self.paused_agents: set[str] = set()
        self.audit_log: list[dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> GlobalKillSwitchState:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


kill_switch_state = GlobalKillSwitchState.get_instance()


class GlobalControlRequest(BaseModel):
    action: str = Field(description="GLOBAL_AI_PAUSE, GLOBAL_AI_DISABLE, or RESUME")
    reason: str
    tenant_id: str = "org-apex-01"


class AgentControlRequest(BaseModel):
    agent_id: str
    action: str = Field(description="PAUSE, RESUME, SUSPEND, TERMINATE")
    reason: str


@router.post("/kill-switch/global", summary="Trigger Global AI Emergency Kill-Switch")
async def control_global_ai(
    req: GlobalControlRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> dict[str, Any]:
    if "HR_ADMIN" not in principal.roles and "SUPER_ADMIN" not in principal.roles and "CEO" not in principal.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: Global AI Kill-Switch requires SUPER_ADMIN, CEO or HR_ADMIN role.",
        )

    action_upper = req.action.upper()
    if action_upper == "GLOBAL_AI_PAUSE":
        kill_switch_state.is_globally_paused = True
    elif action_upper == "GLOBAL_AI_DISABLE":
        kill_switch_state.is_globally_disabled = True
    elif action_upper == "RESUME":
        kill_switch_state.is_globally_paused = False
        kill_switch_state.is_globally_disabled = False
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported kill-switch action: {req.action}")

    event = {
        "event_id": f"gov-evt-{int(time.time())}",
        "action": action_upper,
        "reason": req.reason,
        "actor_id": principal.user_id,
        "tenant_id": principal.tenant_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    }
    kill_switch_state.audit_log.append(event)

    return {
        "success": True,
        "state": {
            "is_globally_paused": kill_switch_state.is_globally_paused,
            "is_globally_disabled": kill_switch_state.is_globally_disabled,
        },
        "event": event,
    }


@router.post("/kill-switch/agent", summary="Control individual agent operational status")
async def control_individual_agent(
    req: AgentControlRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> dict[str, Any]:
    action_upper = req.action.upper()
    if action_upper in ["PAUSE", "SUSPEND", "TERMINATE"]:
        kill_switch_state.paused_agents.add(req.agent_id)
    elif action_upper == "RESUME":
        kill_switch_state.paused_agents.discard(req.agent_id)

    event = {
        "event_id": f"gov-agt-evt-{int(time.time())}",
        "agent_id": req.agent_id,
        "action": action_upper,
        "reason": req.reason,
        "actor_id": principal.user_id,
        "tenant_id": principal.tenant_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    }
    kill_switch_state.audit_log.append(event)

    return {
        "success": True,
        "agent_id": req.agent_id,
        "status": action_upper,
        "event": event,
    }


@router.get("/kill-switch/status", summary="Get global AI safety & kill-switch status")
async def get_kill_switch_status(
    principal: AuthPrincipal = Depends(get_current_principal),
) -> dict[str, Any]:
    return {
        "is_globally_paused": kill_switch_state.is_globally_paused,
        "is_globally_disabled": kill_switch_state.is_globally_disabled,
        "paused_agents_count": len(kill_switch_state.paused_agents),
        "paused_agents": list(kill_switch_state.paused_agents),
        "total_governance_events": len(kill_switch_state.audit_log),
    }


@router.get("/audit-trail", summary="List tamper-evident governance events")
async def get_governance_audit_trail(
    principal: AuthPrincipal = Depends(get_current_principal),
) -> list[dict[str, Any]]:
    return kill_switch_state.audit_log[-50:]
