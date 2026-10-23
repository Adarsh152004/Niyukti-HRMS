"""
Agent Domain — Domain Exceptions.
"""

from __future__ import annotations


class AgentException(Exception):
    """Base exception for all agent domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class AgentLifecycleError(AgentException):
    """Raised when an invalid status transition is attempted on an Agent."""

    pass


class AgentSecurityError(AgentException):
    """Raised when an agent attempts unauthorized security actions or impersonation."""

    pass


class AgentCapabilityError(AgentException):
    """Raised when an agent attempts an action outside its declared capabilities."""

    pass


class AgentNotFoundError(AgentException):
    """Raised when an agent entity is not found."""

    pass


class AgentTaskError(AgentException):
    """Raised when an agent task execution fails or violates state transition rules."""

    pass
