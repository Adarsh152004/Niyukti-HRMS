"""
Agent Message Bus — Asynchronous message broker and mailbox router for specialized AI HR agents.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine

from backend.agents.operations.messaging.models import AgentMessage
from backend.agents.specialized.domain.enums import SpecializedAgentRole

logger = logging.getLogger(__name__)


class AgentMessageBus:
    """
    In-memory asynchronous message broker delivering typed messages to specialized agents with tenant isolation.
    """

    _instance: AgentMessageBus | None = None

    def __init__(self) -> None:
        # Mailboxes: dict[(org_id, agent_role), asyncio.Queue[AgentMessage]]
        self._mailboxes: dict[tuple[str, SpecializedAgentRole], asyncio.Queue[AgentMessage]] = defaultdict(asyncio.Queue)
        self._subscribers: dict[tuple[str, SpecializedAgentRole], list[Callable[[AgentMessage], Coroutine[None, None, None]]]] = (
            defaultdict(list)
        )
        self._message_journal: list[AgentMessage] = []
        self._lock = asyncio.Lock()

    @classmethod
    def get_instance(cls) -> AgentMessageBus:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def send(self, message: AgentMessage) -> None:
        """Deliver a message to recipient's mailbox and notify subscribers."""
        async with self._lock:
            self._message_journal.append(message)

        key = (message.organization_id, message.recipient_role)
        await self._mailboxes[key].put(message)
        logger.debug(f"Message [{message.message_id}] from {message.sender_role} -> {message.recipient_role} queued")

        # Invoke real-time subscribers
        handlers = self._subscribers.get(key, [])
        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Error executing message subscriber for {key}: {e}", exc_info=True)

    def subscribe(
        self,
        organization_id: str,
        role: SpecializedAgentRole,
        handler: Callable[[AgentMessage], Coroutine[None, None, None]],
    ) -> None:
        """Register a handler for incoming messages directed to a role."""
        key = (organization_id, role)
        self._subscribers[key].append(handler)

    async def receive(
        self,
        organization_id: str,
        role: SpecializedAgentRole,
        timeout: float = 1.0,
    ) -> AgentMessage | None:
        """Retrieve next pending message from agent's mailbox."""
        key = (organization_id, role)
        queue = self._mailboxes[key]
        try:
            return await asyncio.wait_for(queue.get(), timeout=timeout)
        except TimeoutError:
            return None

    def get_journal(self, organization_id: str | None = None) -> list[AgentMessage]:
        """Get history of routed messages, optionally filtered by tenant."""
        if organization_id:
            return [m for m in self._message_journal if m.organization_id == organization_id]
        return list(self._message_journal)
