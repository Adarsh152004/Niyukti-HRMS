"""
Circuit Breaker — Protects platform from third-party LLM and integration outages.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from enum import StrEnum
from typing import TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


class CircuitState(StrEnum):
    CLOSED = "CLOSED"  # Normal healthy state
    OPEN = "OPEN"  # Tripped, immediately failing fast
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


class CircuitBreakerOpenError(Exception):
    """Raised when request is blocked due to open circuit breaker."""

    pass


class CircuitBreaker:
    """Manages failure rates and trips automatically when threshold exceeded."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: int = 30,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_state_change = datetime.now(tz=UTC)
        self._lock = asyncio.Lock()

    async def can_execute(self) -> bool:
        """Check if execution is permissible."""
        now = datetime.now(tz=UTC)
        async with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                if (now - self.last_state_change).total_seconds() > self.recovery_timeout_seconds:
                    logger.info(f"Circuit breaker '{self.name}' transitioning from OPEN to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.last_state_change = now
                    return True
                return False
            elif self.state == CircuitState.HALF_OPEN:
                return True
            return False

    async def record_success(self) -> None:
        """Record successful execution."""
        async with self._lock:
            if self.state in [CircuitState.HALF_OPEN, CircuitState.OPEN]:
                logger.info(f"Circuit breaker '{self.name}' successfully recovered -> CLOSED")
            self.state = CircuitState.CLOSED
            self.consecutive_failures = 0
            self.last_state_change = datetime.now(tz=UTC)

    async def record_failure(self, error: Exception | None = None) -> None:
        """Record failed execution and trip if threshold reached."""
        now = datetime.now(tz=UTC)
        async with self._lock:
            self.consecutive_failures += 1
            logger.warning(
                f"Circuit breaker '{self.name}' recorded failure ({self.consecutive_failures}/{self.failure_threshold}): {error}"
            )

            if self.consecutive_failures >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.last_state_change = now
                logger.error(
                    f"Circuit breaker '{self.name}' TRIPPED -> OPEN. Blocking requests for {self.recovery_timeout_seconds}s."
                )
