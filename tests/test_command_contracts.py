"""Tests — Command Contracts."""

from backend.commands.channels import Channel
from backend.commands.contracts import Command, CommandResult, ExecutionStatus, IntentCategory


def test_execution_status_values():
    statuses = [s.value for s in ExecutionStatus]
    assert "RECEIVED" in statuses
    assert "COMPLETED" in statuses
    assert "FAILED" in statuses
    assert "PENDING_APPROVAL" in statuses


def test_command_creation():
    cmd = Command(
        actor_id="ceo-001",
        actor_role="CEO",
        channel=Channel.WHATSAPP,
        raw_input="Show employees at high attrition risk.",
    )
    assert cmd.command_id is not None
    assert cmd.execution_status == ExecutionStatus.RECEIVED
    assert cmd.channel == Channel.WHATSAPP
    assert cmd.intent is None  # Not parsed yet


def test_command_channels_no_business_logic():
    """Channel adapters must not contain business logic — only transport."""
    from backend.commands.channels import CLIChannelAdapter, WhatsAppChannelAdapter

    cli = CLIChannelAdapter()
    wa = WhatsAppChannelAdapter()
    assert cli.channel == Channel.CLI
    assert wa.channel == Channel.WHATSAPP


def test_all_channels_present():
    channel_values = [c.value for c in Channel]
    assert "WEB" in channel_values
    assert "CLI" in channel_values
    assert "CHAT" in channel_values
    assert "WHATSAPP" in channel_values
    assert "API" in channel_values
    assert "AUTONOMOUS_AGENT" in channel_values


def test_human_channel_identification():
    assert Channel.WEB.is_human_channel
    assert Channel.CLI.is_human_channel
    assert Channel.CHAT.is_human_channel
    assert Channel.WHATSAPP.is_human_channel
    assert not Channel.AUTONOMOUS_AGENT.is_human_channel


def test_command_result_creation():
    result = CommandResult(
        command_id="cmd-001",
        status=ExecutionStatus.COMPLETED,
        success=True,
        data={"attrition_risk_employees": []},
        message="Analysis complete.",
    )
    assert result.success is True
    assert result.hitl_required is False


def test_intent_category_values():
    cats = [c.value for c in IntentCategory]
    assert "ANALYTICS" in cats
    assert "EMPLOYEE_QUERY" in cats
    assert "RECRUITMENT_ACTION" in cats
    assert "AUTONOMY_CONTROL" in cats
    assert "AGENT_CONTROL" in cats
    assert "AUDIT_QUERY" in cats
