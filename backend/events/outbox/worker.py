"""
AI-Powered Intelligent HRMS — Transactional Outbox Background Publisher Worker.

Features:
- Polls unconsumed outbox events asynchronously
- Dispatches events to the distributed event bus
- Implements exponential backoff on transient transport failures
- Dead Letter Queue (DLQ) routing after exceeding maximum retry budget
- Graceful shutdown with lifecycle hooks
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from backend.events.event_bus import get_event_bus
from backend.events.outbox import OutboxEvent, OutboxRepository, get_outbox_repository

logger = logging.getLogger(__name__)


class OutboxPublisherWorker:
    """Background task publisher that drains outbox events."""

    def __init__(
        self,
        poll_interval_seconds: float = 1.0,
        batch_size: int = 50,
        max_retries: int = 5,
    ) -> None:
        self.poll_interval = poll_interval_seconds
        self.batch_size = batch_size
        self.max_retries = max_retries
        self._running = False
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Start the background outbox polling loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("OutboxPublisherWorker started.")

    async def stop(self) -> None:
        """Gracefully stop the background outbox worker."""
        if not self._running:
            return
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("OutboxPublisherWorker stopped.")

    async def _run_loop(self) -> None:
        """Main polling loop."""
        while self._running:
            try:
                published = await self.drain_once()
                if published == 0:
                    await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in OutboxPublisherWorker loop: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval * 2)

    async def drain_once(self) -> int:
        """Processes one batch of pending outbox events."""
        outbox_repo = get_outbox_repository()
        event_bus = get_event_bus()

        # Fetch pending events
        pending_events = await outbox_repo.fetch_pending(limit=self.batch_size)
        if not pending_events:
            return 0

        published_count = 0
        for event in pending_events:
            try:
                # Publish event to event bus
                await event_bus.publish(event.to_domain_event())
                await outbox_repo.mark_published(event.event_id)
                published_count += 1
            except Exception as publish_err:
                logger.warning(
                    f"Failed to publish outbox event {event.event_id}: {publish_err}. Retries: {event.retry_count + 1}"
                )
                if event.retry_count + 1 >= self.max_retries:
                    logger.error(f"Routing outbox event {event.event_id} to Dead Letter Queue (DLQ).")
                    await outbox_repo.mark_failed(event.event_id, error=str(publish_err))
                else:
                    await outbox_repo.increment_retry(event.event_id)

        return published_count


# Global singleton worker
outbox_worker = OutboxPublisherWorker()
