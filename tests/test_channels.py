"""Tests — Channel Abstraction."""

import pytest

from backend.commands.channels import Channel


def test_all_six_channels():
    assert len(Channel) == 6


def test_autonomous_agent_not_human():
    assert not Channel.AUTONOMOUS_AGENT.is_human_channel


def test_rich_media_support():
    assert Channel.WEB.supports_rich_media
    assert Channel.CHAT.supports_rich_media
    assert not Channel.CLI.supports_rich_media
    assert not Channel.API.supports_rich_media


def test_async_channels():
    assert Channel.WEB.is_async_friendly
    assert Channel.WHATSAPP.is_async_friendly
    assert Channel.CHAT.is_async_friendly
    assert Channel.API.is_async_friendly


def test_channel_adapter_is_interface():
    """ChannelAdapter must be abstract — cannot be instantiated directly."""
    import inspect

    from backend.commands.channels import ChannelAdapter

    assert inspect.isabstract(ChannelAdapter)


@pytest.mark.asyncio
async def test_whatsapp_adapter_no_business_logic():
    """WhatsApp adapter must not have business logic — only transport contract."""
    from backend.commands.channels import WhatsAppChannelAdapter

    adapter = WhatsAppChannelAdapter()
    assert adapter.channel == Channel.WHATSAPP
    # Calling receive must raise NotImplementedError (no business logic implemented)
    with pytest.raises(NotImplementedError):
        await adapter.receive({})


def test_cli_adapter_channel():
    from backend.commands.channels import CLIChannelAdapter

    cli = CLIChannelAdapter()
    assert cli.channel == Channel.CLI
