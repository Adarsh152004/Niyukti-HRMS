"""
Enterprise Runtime — Enterprise Kernel.

The kernel is the central lifecycle controller for the HRMS platform.
It owns the service registry, event bus, and orchestrates startup/shutdown
of all registered components.

Usage::

    kernel = EnterpriseKernel.get_instance()
    await kernel.start()
    ...
    await kernel.stop()
"""

from __future__ import annotations

import asyncio
from enum import StrEnum
from typing import Any

from backend.runtime.config import HRMSConfig, get_config
from backend.runtime.events import EventBus, InMemoryEventBus
from backend.runtime.logging import configure_logging, get_logger
from backend.runtime.memory import InMemoryKVStore
from backend.runtime.registry import ServiceRegistry

logger = get_logger("kernel")


class KernelState(StrEnum):
    """Lifecycle states of the enterprise kernel."""

    CREATED = "CREATED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


class EnterpriseKernel:
    """
    Singleton enterprise kernel for the AI-Powered Intelligent HRMS.

    Responsibilities:
    - Owns and exposes the ServiceRegistry
    - Manages startup / shutdown lifecycle
    - Configures logging
    - Bootstraps default services (event bus, KV store)
    - Exposes health status for monitoring

    Only one instance exists per process. Use ``get_instance()`` to obtain it.
    """

    _instance: EnterpriseKernel | None = None
    _lock: asyncio.Lock | None = None

    def __init__(self, config: HRMSConfig | None = None) -> None:
        if EnterpriseKernel._instance is not None:
            raise RuntimeError("EnterpriseKernel is a singleton. Use EnterpriseKernel.get_instance().")
        self._config: HRMSConfig = config or get_config()
        self._registry: ServiceRegistry = ServiceRegistry()
        self._state: KernelState = KernelState.CREATED
        self._metadata: dict[str, Any] = {}

    @classmethod
    def get_instance(cls, config: HRMSConfig | None = None) -> EnterpriseKernel:
        """
        Return the singleton kernel instance, creating it on first call.

        Args:
            config: Optional config override (only used on first call).
        """
        if cls._instance is None:
            cls._instance = cls(config=config)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """
        Destroy the singleton instance.

        Intended for testing only. Never call in production.
        """
        cls._instance = None

    # ── Properties ──────────────────────────────────────────────────────────

    @property
    def config(self) -> HRMSConfig:
        return self._config

    @property
    def registry(self) -> ServiceRegistry:
        return self._registry

    @property
    def state(self) -> KernelState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._state == KernelState.RUNNING

    # ── Lifecycle ────────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the enterprise kernel and all registered services."""
        if self._state not in (KernelState.CREATED, KernelState.STOPPED):
            raise RuntimeError(f"Cannot start kernel in state: {self._state}")

        self._state = KernelState.STARTING
        logger.info("HRMS Enterprise Kernel starting — %s v%s", self._config.app_name, self._config.app_version)

        try:
            # Configure structured logging
            configure_logging(
                level=self._config.log_level,
                log_format=self._config.log_format,
                pii_masking=self._config.log_pii_masking,
            )

            # Register core services
            self._bootstrap_core_services()

            # Start the event bus
            event_bus: EventBus = self._registry.resolve("event_bus", EventBus)
            await event_bus.start()

            self._state = KernelState.RUNNING
            logger.info("HRMS Enterprise Kernel RUNNING in %s environment.", self._config.environment)

        except Exception as exc:
            self._state = KernelState.ERROR
            logger.error("Kernel startup failed: %s", exc)
            raise

    async def stop(self) -> None:
        """Stop the enterprise kernel gracefully."""
        if self._state != KernelState.RUNNING:
            return

        self._state = KernelState.STOPPING
        logger.info("HRMS Enterprise Kernel stopping…")

        try:
            event_bus: EventBus = self._registry.resolve("event_bus", EventBus)
            await event_bus.stop()
        except Exception:
            pass  # Best effort

        self._state = KernelState.STOPPED
        logger.info("HRMS Enterprise Kernel stopped.")

    def health(self) -> dict[str, Any]:
        """Return a health status snapshot suitable for monitoring endpoints."""
        return {
            "status": "healthy" if self.is_running else self._state.value.lower(),
            "state": self._state.value,
            "app_name": self._config.app_name,
            "version": self._config.app_version,
            "environment": self._config.environment,
            "services": self._registry.registered_names(),
        }

    # ── Bootstrap ────────────────────────────────────────────────────────────

    def _bootstrap_core_services(self) -> None:
        """Register default service implementations."""
        # Event bus
        if not self._registry.has("event_bus"):
            self._registry.register("event_bus", InMemoryEventBus())

        # KV store
        if not self._registry.has("kv_store"):
            self._registry.register("kv_store", InMemoryKVStore())

        logger.info(
            "Core services registered: %s",
            self._registry.registered_names(),
        )
