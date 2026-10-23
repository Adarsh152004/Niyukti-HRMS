"""
Agent Reasoning — Domain Exceptions.
"""

from __future__ import annotations


class ReasoningEngineError(Exception):
    """Base exception for reasoning engine errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ReasoningLoopTimeoutError(ReasoningEngineError):
    """Raised when reasoning loop times out."""

    pass


class MaxStepsExceededError(ReasoningEngineError):
    """Raised when maximum allowed reasoning steps count is reached."""

    pass


class InvalidDecisionError(ReasoningEngineError):
    """Raised when LLM output validation fails Pydantic schema checks."""

    pass


class LLMProviderError(ReasoningEngineError):
    """Raised when an external LLM provider encounters an error or timeout."""

    pass
