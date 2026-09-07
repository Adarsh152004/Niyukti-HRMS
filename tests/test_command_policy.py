"""Tests — Policy Engine rules (ALLOW, DENY, REQUIRE_APPROVAL)."""

import pytest

from backend.commands.application.bus import CommandBus, CommandBusExecutionError
from backend.commands.application.handlers import CreateEmployeeCommandHandler
from backend.commands.application.policy_engine import PolicyEngine
from backend.commands.domain.enums import CommandStatus, PolicyDecision, RiskLevel
from backend.commands.domain.models import Command, CommandMetadata
from backend.hrms.domain.actor import Actor, ActorType


def test_policy_engine_allow():
    engine = PolicyEngine()
    actor = Actor(
        actor_id="user-1",
        actor_type=ActorType.HUMAN,
        organization_id="org-acme",
    )
    cmd = Command(
        command_type="employee.create",
        actor_id=actor.actor_id,
        organization_id=actor.organization_id,
    )

    ctx = CommandBus().build_context(actor)
    res = engine.evaluate(cmd, ctx, risk_level=RiskLevel.LOW)
    assert res.decision == PolicyDecision.ALLOW


def test_policy_engine_deny_rule_for_ai_agent_roles():
    engine = PolicyEngine()
    agent_actor = Actor(
        actor_id="agent-1",
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
    )
    cmd = Command(
        command_type="security.update_role",
        actor_id=agent_actor.actor_id,
        organization_id=agent_actor.organization_id,
    )

    ctx = CommandBus().build_context(agent_actor)
    res = engine.evaluate(cmd, ctx, risk_level=RiskLevel.HIGH)
    # Default policy rule blocks AI Agents from updating security roles
    assert res.decision == PolicyDecision.DENY


@pytest.mark.asyncio
async def test_policy_engine_denial_blocks_command_execution():
    bus = CommandBus()
    handler = CreateEmployeeCommandHandler()
    meta = CommandMetadata(
        command_type="security.update_role",
        description="Update role",
        required_permissions=["ROLE_UPDATE"],
    )
    bus.registry.register("security.update_role", handler, meta)

    agent_actor = Actor(
        actor_id="agent-1",
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
        permissions={"ROLE_UPDATE"},
    )
    cmd = Command(
        command_type="security.update_role",
        actor_id=agent_actor.actor_id,
        organization_id=agent_actor.organization_id,
    )
    ctx = bus.build_context(agent_actor)

    with pytest.raises(CommandBusExecutionError, match="Policy denied execution"):
        await bus.dispatch(cmd, ctx)

    assert cmd.status == CommandStatus.DENIED
