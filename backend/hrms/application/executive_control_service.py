"""
Executive Control Service — Core Handler Plane for CEO / Executive Cockpit, Autonomy Matrix, Emergency Kill Switch, and Quarantine.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.specialized.domain.enums import AutonomyMode, SpecializedAgentRole
from backend.runtime.events import Event, EventBus

logger = logging.getLogger(__name__)


@dataclass
class KillSwitchState:
    is_active: bool = False
    reason: str | None = None
    triggered_by: str | None = None
    activated_at: datetime | None = None


@dataclass
class QuarantineRecord:
    agent_role: SpecializedAgentRole
    reason: str
    quarantined_by: str
    quarantined_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class AutonomySetting(BaseModel):
    agent_role: SpecializedAgentRole
    autonomy_mode: AutonomyMode
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str = "system"


class ExecutiveCockpitSummary(BaseModel):
    organization_id: str
    total_employees: int = 150
    active_specialized_agents: int = 24
    pending_executive_approvals: int = 3
    critical_risks_count: int = 0
    kill_switch_active: bool = False
    quarantined_agents: list[str] = Field(default_factory=list)
    system_health_status: str = "HEALTHY"
    health_score: float = 0.99


class ExecutiveControlService:
    """
    Control Plane Service empowering the CEO and executive operators with ultimate oversight and intervention authority.
    """

    _instance: ExecutiveControlService | None = None

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self.event_bus = event_bus or EventBus.get_instance()
        # dict[org_id, KillSwitchState]
        self._kill_switches: dict[str, KillSwitchState] = {}
        # dict[org_id, dict[SpecializedAgentRole, QuarantineRecord]]
        self._quarantined_agents: dict[str, dict[SpecializedAgentRole, QuarantineRecord]] = {}
        # dict[org_id, dict[SpecializedAgentRole, AutonomySetting]]
        self._autonomy_matrices: dict[str, dict[SpecializedAgentRole, AutonomySetting]] = {}

    @classmethod
    def get_instance(cls) -> ExecutiveControlService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # 1. Cockpit Overview
    async def get_cockpit_summary(self, organization_id: str) -> ExecutiveCockpitSummary:
        kill_state = self._kill_switches.get(organization_id, KillSwitchState())
        quarantined = list(self._quarantined_agents.get(organization_id, {}).keys())
        return ExecutiveCockpitSummary(
            organization_id=organization_id,
            kill_switch_active=kill_state.is_active,
            quarantined_agents=[r.value for r in quarantined],
            system_health_status="DEGRADED" if kill_state.is_active else "HEALTHY",
            health_score=0.50 if kill_state.is_active else 0.99,
        )

    # 2. Autonomy Matrix
    async def get_autonomy_matrix(self, organization_id: str) -> list[AutonomySetting]:
        if organization_id not in self._autonomy_matrices:
            # Default matrix for all 24 agents
            self._autonomy_matrices[organization_id] = {
                role: AutonomySetting(
                    agent_role=role,
                    autonomy_mode=(
                        AutonomyMode.AUTONOMOUS_LOW_RISK
                        if "ASSISTANT" in role.value or "NOTIFICATION" in role.value
                        else AutonomyMode.AUTONOMOUS_WITH_APPROVAL
                    ),
                )
                for role in SpecializedAgentRole
            }
        return list(self._autonomy_matrices[organization_id].values())

    async def update_agent_autonomy(
        self,
        organization_id: str,
        agent_role: SpecializedAgentRole,
        new_mode: AutonomyMode,
        updated_by: str,
    ) -> AutonomySetting:
        if organization_id not in self._autonomy_matrices:
            await self.get_autonomy_matrix(organization_id)

        setting = AutonomySetting(
            agent_role=agent_role,
            autonomy_mode=new_mode,
            updated_at=datetime.now(UTC),
            updated_by=updated_by,
        )
        self._autonomy_matrices[organization_id][agent_role] = setting

        await self.event_bus.publish(
            Event(
                event_type="hrms.executive.autonomy_updated",
                source=updated_by,
                payload={
                    "organization_id": organization_id,
                    "agent_role": agent_role.value,
                    "new_mode": new_mode.value,
                },
            )
        )
        return setting

    # 3. Emergency Kill Switch
    async def activate_kill_switch(self, organization_id: str, reason: str, triggered_by: str) -> KillSwitchState:
        state = KillSwitchState(
            is_active=True,
            reason=reason,
            triggered_by=triggered_by,
            activated_at=datetime.now(UTC),
        )
        self._kill_switches[organization_id] = state
        logger.critical(f"EMERGENCY KILL SWITCH ACTIVATED for [{organization_id}] by {triggered_by}: {reason}")

        await self.event_bus.publish(
            Event(
                event_type="hrms.executive.kill_switch_activated",
                source=triggered_by,
                payload={
                    "organization_id": organization_id,
                    "reason": reason,
                    "activated_at": state.activated_at.isoformat() if state.activated_at else None,
                },
            )
        )
        return state

    async def deactivate_kill_switch(self, organization_id: str, triggered_by: str) -> KillSwitchState:
        state = KillSwitchState(is_active=False)
        self._kill_switches[organization_id] = state
        logger.info(f"Kill switch resumed for [{organization_id}] by {triggered_by}")

        await self.event_bus.publish(
            Event(
                event_type="hrms.executive.kill_switch_deactivated",
                source=triggered_by,
                payload={"organization_id": organization_id},
            )
        )
        return state

    def is_kill_switch_active(self, organization_id: str) -> bool:
        return self._kill_switches.get(organization_id, KillSwitchState()).is_active

    # 4. Agent Quarantine
    async def quarantine_agent(
        self,
        organization_id: str,
        agent_role: SpecializedAgentRole,
        reason: str,
        triggered_by: str,
    ) -> QuarantineRecord:
        if organization_id not in self._quarantined_agents:
            self._quarantined_agents[organization_id] = {}

        record = QuarantineRecord(
            agent_role=agent_role,
            reason=reason,
            quarantined_by=triggered_by,
            quarantined_at=datetime.now(UTC),
        )
        self._quarantined_agents[organization_id][agent_role] = record
        logger.warning(f"Agent [{agent_role.value}] QUARANTINED in [{organization_id}] by {triggered_by}: {reason}")

        await self.event_bus.publish(
            Event(
                event_type="hrms.executive.agent_quarantined",
                source=triggered_by,
                payload={
                    "organization_id": organization_id,
                    "agent_role": agent_role.value,
                    "reason": reason,
                },
            )
        )
        return record

    async def unquarantine_agent(
        self,
        organization_id: str,
        agent_role: SpecializedAgentRole,
        triggered_by: str,
    ) -> bool:
        if organization_id in self._quarantined_agents:
            removed = self._quarantined_agents[organization_id].pop(agent_role, None)
            if removed:
                logger.info(f"Agent [{agent_role.value}] UNQUARANTINED in [{organization_id}] by {triggered_by}")
                return True
        return False

    def is_agent_quarantined(self, organization_id: str, agent_role: SpecializedAgentRole) -> bool:
        return agent_role in self._quarantined_agents.get(organization_id, {})

    # 5. System Health Telemetry
    async def get_system_health(self, organization_id: str) -> dict[str, Any]:
        kill_active = self.is_kill_switch_active(organization_id)
        return {
            "organization_id": organization_id,
            "overall_status": "DEGRADED" if kill_active else "HEALTHY",
            "layers": {
                "platform_core": "OPERATIONAL",
                "ai_gateway": "OPERATIONAL",
                "knowledge_brain": "OPERATIONAL",
                "predictive_ml_platform": "OPERATIONAL",
                "agent_runtime": "SUSPENDED" if kill_active else "OPERATIONAL",
                "workflow_engine": "SUSPENDED" if kill_active else "OPERATIONAL",
            },
            "kill_switch_active": kill_active,
            "timestamp": datetime.now(UTC).isoformat(),
        }
