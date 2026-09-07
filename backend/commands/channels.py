"""
Command Architecture — Channel definitions and adapter contracts.

The same command-processing architecture serves all channels.
Business logic lives only in the application layer — channel adapters
are purely responsible for transport, serialization, and response formatting.

Channels:
    WEB              — Web dashboard / browser application
    CLI              — Command-line interface (asi-hr commands)
    CHAT             — Conversational chat interface
    WHATSAPP         — WhatsApp interface for CEO/authorized handlers
    API              — Programmatic REST/GraphQL API
    AUTONOMOUS_AGENT — Commands issued by autonomous agents
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any


class Channel(StrEnum):
    """
    Communication channels through which HRMS commands are received.

    All channels call the same application/command layer.
    No business logic may reside in channel adapters.
    """

    WEB = "WEB"
    CLI = "CLI"
    CHAT = "CHAT"
    WHATSAPP = "WHATSAPP"
    API = "API"
    AUTONOMOUS_AGENT = "AUTONOMOUS_AGENT"

    @property
    def is_human_channel(self) -> bool:
        """Return True if the channel represents a human actor."""
        return self != Channel.AUTONOMOUS_AGENT

    @property
    def supports_rich_media(self) -> bool:
        """Return True if the channel can render rich media (tables, charts)."""
        return self in (Channel.WEB, Channel.CHAT)

    @property
    def is_async_friendly(self) -> bool:
        """Return True if the channel supports async / push notifications."""
        return self in (Channel.WEB, Channel.WHATSAPP, Channel.CHAT, Channel.API)


class ChannelAdapter(ABC):
    """
    Abstract channel adapter.

    Each channel has one adapter that handles:
    - Receiving incoming requests from the transport layer
    - Parsing into a channel-agnostic Command object
    - Sending results back in the channel's native format

    Adapters MUST NOT contain business logic.
    All business logic lives in the application/command layer.
    """

    @property
    @abstractmethod
    def channel(self) -> Channel:
        """The channel this adapter handles."""
        ...

    @abstractmethod
    async def receive(self, raw_input: Any) -> dict[str, Any]:
        """
        Parse raw channel input into a normalized command dictionary.

        Returns a dict suitable for constructing a Command object.
        Must never execute business logic.
        """
        ...

    @abstractmethod
    async def respond(self, result: dict[str, Any], context: dict[str, Any]) -> Any:
        """
        Format and send the application result back to the channel.

        Must never modify the result — only format for the channel's UI.
        """
        ...

    @abstractmethod
    async def send_notification(self, message: str, recipient_id: str) -> None:
        """Push an unsolicited notification to a recipient on this channel."""
        ...


class CLIChannelAdapter(ChannelAdapter):
    """Stub CLI adapter — full implementation in a later node."""

    @property
    def channel(self) -> Channel:
        return Channel.CLI

    async def receive(self, raw_input: Any) -> dict[str, Any]:
        raise NotImplementedError("CLI adapter not yet implemented.")

    async def respond(self, result: dict[str, Any], context: dict[str, Any]) -> Any:
        raise NotImplementedError("CLI adapter not yet implemented.")

    async def send_notification(self, message: str, recipient_id: str) -> None:
        raise NotImplementedError("CLI adapter not yet implemented.")


class WhatsAppChannelAdapter(ChannelAdapter):
    """
    Stub WhatsApp adapter — full integration in a later node.

    IMPORTANT: The WhatsApp adapter must never contain business logic.
    CEO commands received on WhatsApp are routed through the same
    command/application layer as all other channels.
    """

    @property
    def channel(self) -> Channel:
        return Channel.WHATSAPP

    async def receive(self, raw_input: Any) -> dict[str, Any]:
        raise NotImplementedError("WhatsApp adapter not yet implemented.")

    async def respond(self, result: dict[str, Any], context: dict[str, Any]) -> Any:
        raise NotImplementedError("WhatsApp adapter not yet implemented.")

    async def send_notification(self, message: str, recipient_id: str) -> None:
        raise NotImplementedError("WhatsApp adapter not yet implemented.")
