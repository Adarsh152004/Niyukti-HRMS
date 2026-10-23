"""
External Integration — Email adapter interface.

Provides the contract for email delivery.
Used by the Notification Agent for alerts, reports, and HITL notifications.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class EmailMessage:
    """An outbound email message."""

    to_addresses: list[str]
    subject: str
    body_html: str
    body_text: str | None = None
    cc_addresses: list[str] = field(default_factory=list)
    bcc_addresses: list[str] = field(default_factory=list)
    from_address: str | None = None
    reply_to: str | None = None
    attachments: list[dict[str, str]] = field(default_factory=list)  # {"filename": ..., "content": ...}


class EmailAdapter(ABC):
    """Abstract email adapter. Concrete implementations: SMTP, SendGrid, SES, etc."""

    @abstractmethod
    async def send(self, message: EmailMessage) -> str:
        """Send an email. Returns provider message ID."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the email provider is reachable."""
        ...


"""
External Integration — Calendar adapter interface.

Used by the Interview Coordination Agent and HR workflows for
scheduling interviews, reviews, and meetings.
"""


@dataclass
class CalendarEvent:
    """A calendar event to create or update."""

    title: str
    description: str
    start_datetime: str  # ISO 8601
    end_datetime: str  # ISO 8601
    organizer_email: str
    attendee_emails: list[str] = field(default_factory=list)
    location: str | None = None
    meeting_link: str | None = None
    event_id: str | None = None  # Populated after creation


class CalendarAdapter(ABC):
    """Abstract calendar adapter. Concrete: Google Calendar, Outlook, CalDAV."""

    @abstractmethod
    async def create_event(self, event: CalendarEvent) -> str:
        """Create a calendar event. Returns event ID."""
        ...

    @abstractmethod
    async def update_event(self, event_id: str, event: CalendarEvent) -> None:
        """Update an existing calendar event."""
        ...

    @abstractmethod
    async def cancel_event(self, event_id: str, reason: str = "") -> None:
        """Cancel/delete a calendar event."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the calendar service is reachable."""
        ...
