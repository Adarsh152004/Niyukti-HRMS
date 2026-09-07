"""
External Integration — WhatsApp adapter interface.

Defines the contract for the WhatsApp integration.
The CEO and authorized HR handlers will eventually use WhatsApp
to issue commands and receive alerts.

CRITICAL RULES:
- This adapter must NEVER contain business logic.
- Commands received via WhatsApp route through the same
  command/application layer as all other channels.
- The adapter only handles transport, authentication, and formatting.

Implementation is deferred to a later node.
Real WhatsApp Business API credentials are NOT configured here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class WhatsAppMessage:
    """An incoming or outgoing WhatsApp message."""

    message_id: str
    from_number: str
    to_number: str
    body: str
    media_url: str | None = None
    timestamp: str | None = None


@dataclass
class WhatsAppOutboundMessage:
    """A message to be sent via WhatsApp."""

    to_number: str
    body: str
    media_url: str | None = None
    template_name: str | None = None
    template_params: dict[str, Any] | None = None


class WhatsAppAdapter(ABC):
    """
    Abstract WhatsApp adapter interface.

    Future implementation will integrate with:
    - WhatsApp Business API (Meta)
    - Twilio WhatsApp API
    or equivalent provider.

    Supported future use cases:
    - CEO command issuance
    - HR admin commands
    - HITL approval responses
    - Alerts and notifications
    - Agent status reports
    - Emergency stop commands
    """

    @abstractmethod
    async def receive_message(self, webhook_payload: dict[str, Any]) -> WhatsAppMessage:
        """Parse an incoming webhook payload into a WhatsAppMessage."""
        ...

    @abstractmethod
    async def send_message(self, message: WhatsAppOutboundMessage) -> str:
        """
        Send a WhatsApp message.

        Returns:
            Message ID assigned by the WhatsApp provider.
        """
        ...

    @abstractmethod
    async def send_approval_request(
        self,
        to_number: str,
        approval_id: str,
        description: str,
        risk_level: str,
    ) -> str:
        """
        Send an interactive approval request message.

        The recipient can reply with APPROVE or REJECT.
        This must be routed through the HITL layer — not executed directly.
        """
        ...

    @abstractmethod
    async def verify_webhook(self, payload: dict[str, Any], signature: str) -> bool:
        """Verify that a webhook payload came from the official WhatsApp provider."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the WhatsApp API is reachable."""
        ...
