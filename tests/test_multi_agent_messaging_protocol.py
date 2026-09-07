"""
Tests for Typed Multi-Agent Messaging Protocol and Mailbox Routing.
"""

from __future__ import annotations

import pytest

from backend.agents.operations.messaging.bus import AgentMessageBus
from backend.agents.operations.messaging.models import AgentMessage, AgentMessagePriority, AgentMessageType
from backend.agents.specialized.domain.enums import SpecializedAgentRole


@pytest.mark.asyncio
async def test_agent_message_bus_send_and_receive():
    bus = AgentMessageBus.get_instance()
    org_id = "org-msg-test"

    msg = AgentMessage(
        organization_id=org_id,
        sender_role=SpecializedAgentRole.RECRUITMENT_AGENT,
        recipient_role=SpecializedAgentRole.RESUME_SCREENING_AGENT,
        message_type=AgentMessageType.TASK_DELEGATION,
        payload={"job_id": "job-101", "resume_keys": ["res-1", "res-2"]},
        priority=AgentMessagePriority.HIGH,
    )

    await bus.send(msg)

    # Receive at recipient mailbox
    received = await bus.receive(org_id, SpecializedAgentRole.RESUME_SCREENING_AGENT, timeout=2.0)
    assert received is not None
    assert received.message_id == msg.message_id
    assert received.payload["job_id"] == "job-101"
    assert received.sender_role == SpecializedAgentRole.RECRUITMENT_AGENT


@pytest.mark.asyncio
async def test_agent_message_tenant_isolation():
    bus = AgentMessageBus.get_instance()
    org_a = "org-alpha"
    org_b = "org-beta"

    msg_a = AgentMessage(
        organization_id=org_a,
        sender_role=SpecializedAgentRole.HR_MANAGER_AGENT,
        recipient_role=SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT,
        message_type=AgentMessageType.TASK_DELEGATION,
        payload={"action": "calculate_salaries_org_a"},
    )
    await bus.send(msg_a)

    # Org B payroll agent should not receive Org A message
    received_b = await bus.receive(org_b, SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT, timeout=0.1)
    assert received_b is None

    # Org A payroll agent receives it
    received_a = await bus.receive(org_a, SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT, timeout=1.0)
    assert received_a is not None
    assert received_a.payload["action"] == "calculate_salaries_org_a"
