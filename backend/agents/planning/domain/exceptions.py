"""
Agent Planning Exceptions — Domain exception hierarchy for planning and execution errors.
"""

from __future__ import annotations


class PlanError(Exception):
    """Base exception for planning domain errors."""

    pass


class PlanValidationError(PlanError):
    """Raised when a plan fails safety, capability, schema, or security validation."""

    pass


class PlanExecutionError(PlanError):
    """Raised when a step or plan execution encounters an unrecoverable error."""

    pass


class ReplanningError(PlanError):
    """Raised when plan revision or replanning fails."""

    pass


class CircularDependencyError(PlanValidationError):
    """Raised when step dependencies form a cycle in the DAG."""

    pass
