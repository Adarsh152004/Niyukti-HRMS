"""
Agent Tool Registry — Domain Exceptions.
"""

from __future__ import annotations


class ToolRegistryError(Exception):
    """Base exception for tool registry errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ToolNotFoundError(ToolRegistryError):
    """Raised when a tool is not registered."""

    pass


class ToolAccessDeniedError(ToolRegistryError):
    """Raised when an agent attempts to access a tool without required capabilities."""

    pass


class ToolValidationError(ToolRegistryError):
    """Raised when tool input schema validation fails."""

    pass


class ToolExecutionError(ToolRegistryError):
    """Raised when tool execution fails."""

    pass
