"""
Orchestration Exceptions — Domain exceptions for agent orchestration and execution loops.
"""

from __future__ import annotations


class OrchestrationError(Exception):
    """Base exception for agent orchestration errors."""

    pass


class RunawayExecutionError(OrchestrationError):
    """Raised when an autonomous execution loop exceeds step, tool call, or retry safety limits."""

    pass


class ExecutionTimeoutError(OrchestrationError):
    """Raised when autonomous agent execution exceeds maximum time allocation."""

    pass
