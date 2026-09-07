"""
Workflow Domain — Domain Exceptions.
"""

from __future__ import annotations


class WorkflowException(Exception):
    """Base exception for all workflow domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class WorkflowValidationError(WorkflowException):
    """Raised when a workflow definition or DAG fails validation."""

    pass


class WorkflowStateTransitionError(WorkflowException):
    """Raised when an invalid status transition is attempted on a workflow or step."""

    pass


class StepExecutionError(WorkflowException):
    """Raised when an error occurs during step execution."""

    pass


class LeaseAcquisitionError(WorkflowException):
    """Raised when acquiring a worker lease on a job fails due to concurrency lock."""

    pass
