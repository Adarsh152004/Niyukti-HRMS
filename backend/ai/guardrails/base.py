"""
Base Guardrail Architecture & Result Contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class GuardrailLayerType(StrEnum):
    INPUT = "INPUT"
    CONTEXT = "CONTEXT"
    TOOL = "TOOL"
    OUTPUT = "OUTPUT"
    ACTION = "ACTION"
    RUNTIME = "RUNTIME"


@dataclass
class GuardrailResult:
    """Structured evaluation outcome from a guardrail evaluation."""

    passed: bool
    layer: GuardrailLayerType
    violations: list[str] = field(default_factory=list)
    risk_score: float = 0.0
    sanitized_content: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Guardrail(ABC):
    """Abstract interface for all security and policy guardrails."""

    @property
    @abstractmethod
    def layer_type(self) -> GuardrailLayerType:
        """The specific layer in the 6-layer defense stack."""
        pass

    @abstractmethod
    async def evaluate(self, payload: Any, context: dict[str, Any] | None = None) -> GuardrailResult:
        """Evaluate incoming payload and return structured GuardrailResult."""
        pass
