"""Tests — Delegation Capability Subsetting Invariants."""

from datetime import UTC, datetime, timedelta

import pytest

from backend.agents.delegation.application.delegation_policy import DelegationPolicy
from backend.agents.delegation.domain.exceptions import PrivilegeEscalationError
from backend.agents.domain.models import AgentCapability


def test_capability_intersection_allowed_subset():
    policy = DelegationPolicy()

    cap_full = AgentCapability(
        capability_id="cap-full",
        name="Employee Admin",
        resource="employee",
        actions=["read", "create", "update"],
    )

    cap_requested = AgentCapability(
        capability_id="cap-read-only",
        name="Employee Reader",
        resource="employee",
        actions=["read"],
    )

    from backend.agents.domain.models import Agent

    sup = Agent(
        agent_id="sup-1",
        organization_id="org-acme",
        name="sup",
        display_name="sup",
        actor_id="act-sup",
        capabilities=[cap_full],
    )
    sup.status = sup.status.ACTIVE

    wrk = Agent(
        agent_id="wrk-1",
        organization_id="org-acme",
        name="wrk",
        display_name="wrk",
        actor_id="act-wrk",
        capabilities=[],
    )
    wrk.status = wrk.status.ACTIVE

    expires_at = datetime.now(tz=UTC) + timedelta(hours=1)

    effective = policy.validate_delegation(
        delegator=sup,
        delegate=wrk,
        requested_capabilities=[cap_requested],
        organization_id="org-acme",
        expires_at=expires_at,
    )

    assert len(effective) == 1
    assert effective[0].resource == "employee"
    assert effective[0].actions == ["read"]


def test_capability_intersection_denies_superset():
    policy = DelegationPolicy()

    cap_read_only = AgentCapability(
        capability_id="cap-read",
        name="Employee Reader",
        resource="employee",
        actions=["read"],
    )

    cap_requested = AgentCapability(
        capability_id="cap-read-write",
        name="Employee Writer",
        resource="employee",
        actions=["read", "create"],  # Delegator lacks create!
    )

    from backend.agents.domain.models import Agent

    sup = Agent(
        agent_id="sup-1",
        organization_id="org-acme",
        name="sup",
        display_name="sup",
        actor_id="act-sup",
        capabilities=[cap_read_only],
    )
    sup.status = sup.status.ACTIVE

    wrk = Agent(
        agent_id="wrk-1",
        organization_id="org-acme",
        name="wrk",
        display_name="wrk",
        actor_id="act-wrk",
        capabilities=[],
    )
    wrk.status = wrk.status.ACTIVE

    expires_at = datetime.now(tz=UTC) + timedelta(hours=1)

    with pytest.raises(PrivilegeEscalationError, match="attempts privilege escalation"):
        policy.validate_delegation(
            delegator=sup,
            delegate=wrk,
            requested_capabilities=[cap_requested],
            organization_id="org-acme",
            expires_at=expires_at,
        )
