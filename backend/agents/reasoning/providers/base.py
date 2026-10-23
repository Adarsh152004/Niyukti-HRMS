"""
LLM Provider Port — Abstract interface for LLM provider adapters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.agents.reasoning.domain.models import LLMRequest, LLMResponse


class LLMProviderPort(ABC):
    """
    Abstract port interface for LLM completion engines.
    Isolates reasoning engine from specific LLM vendors (OpenAI, Anthropic, Gemini, Mock).
    """

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate structured response from LLM request."""
        pass
