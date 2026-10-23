"""
Specialized Agent Domain Exceptions.
"""

from __future__ import annotations


class SpecializedAgentError(Exception):
    """Base exception for all specialized agent domain errors."""


class AgentSpecializationNotFoundError(SpecializedAgentError):
    """Raised when a requested specialized agent definition or instance cannot be resolved."""


class UnauthorizedCapabilityError(SpecializedAgentError):
    """Raised when an agent attempts an action outside its declared capability profile."""


class ProhibitedToolExecutionError(SpecializedAgentError):
    """Raised when an agent attempts to invoke a tool that is denied by its tool policy."""


class InvalidSupervisorHierarchyError(SpecializedAgentError):
    """Raised when an invalid supervisor relationship or circular dependency is detected."""


class AgentPolicyViolationError(SpecializedAgentError):
    """Raised when an agent violates its knowledge, memory, or governance policy."""
