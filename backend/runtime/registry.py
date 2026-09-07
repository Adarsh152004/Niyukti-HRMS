"""
Enterprise Runtime — Service Registry.

Provides named service registration, resolution, and lifecycle management.
Acts as the central dependency container for the HRMS platform.
"""

from __future__ import annotations

from typing import Any, TypeVar

T = TypeVar("T")


class ServiceNotFoundError(Exception):
    """Raised when a requested service has not been registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Service not registered: {name!r}")
        self.name = name


class ServiceAlreadyRegisteredError(Exception):
    """Raised when attempting to register a service name that is already in use."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Service already registered: {name!r}. Use overwrite=True to replace.")
        self.name = name


class ServiceRegistry:
    """
    Named service container for the HRMS enterprise runtime.

    Services are registered by string name and resolved on demand.
    Supports singleton and factory registration patterns.

    Usage::

        registry = ServiceRegistry()
        registry.register("event_bus", InMemoryEventBus())
        bus = registry.resolve("event_bus", EventBus)
    """

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}

    def register(self, name: str, instance: Any, overwrite: bool = False) -> None:
        """
        Register a service instance under a given name.

        Args:
            name: Unique service name.
            instance: The service object to register.
            overwrite: If True, replace an existing registration silently.

        Raises:
            ServiceAlreadyRegisteredError: If the name is taken and overwrite=False.
        """
        if name in self._services and not overwrite:
            raise ServiceAlreadyRegisteredError(name)
        self._services[name] = instance

    def resolve(self, name: str, expected_type: type[T] | None = None) -> Any:
        """
        Resolve a registered service by name.

        Args:
            name: The registered service name.
            expected_type: Optional type for runtime type checking.

        Returns:
            The registered service instance.

        Raises:
            ServiceNotFoundError: If no service is registered under the name.
            TypeError: If expected_type is given and the instance does not match.
        """
        if name not in self._services:
            raise ServiceNotFoundError(name)
        instance = self._services[name]
        if expected_type is not None and not isinstance(instance, expected_type):
            raise TypeError(f"Service {name!r} is {type(instance).__name__!r}, " f"expected {expected_type.__name__!r}")
        return instance

    def has(self, name: str) -> bool:
        """Return True if a service is registered under the given name."""
        return name in self._services

    def unregister(self, name: str) -> None:
        """Remove a service registration. No-op if not registered."""
        self._services.pop(name, None)

    def registered_names(self) -> list[str]:
        """Return a sorted list of all registered service names."""
        return sorted(self._services.keys())

    def __repr__(self) -> str:
        return f"ServiceRegistry(services={self.registered_names()})"
