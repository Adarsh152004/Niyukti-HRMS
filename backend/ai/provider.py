"""
AI Intelligence Layer — AI Provider adapter interface.

Abstracts the underlying AI/LLM provider so the platform is not
coupled to any specific vendor (OpenAI, Google, Anthropic, local models).

Concrete implementations are provided in later nodes.
No real API calls are made in this module.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AIMessage:
    """A message in an AI conversation."""

    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class AICompletionRequest:
    """Request to an AI provider for text completion."""

    messages: list[AIMessage]
    model: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int = 4096
    response_format: str | None = None  # e.g. "json_object"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AICompletionResponse:
    """Response from an AI provider."""

    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    finish_reason: str = "stop"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_cost_estimate(self) -> float | None:
        """Cost estimate in USD. None if pricing is unknown."""
        return None


@dataclass
class AIEmbeddingRequest:
    """Request to an AI provider for text embedding."""

    text: str
    model: str = "text-embedding-3-small"


@dataclass
class AIEmbeddingResponse:
    """Response from an AI provider for embeddings."""

    vector: list[float]
    model: str
    token_count: int = 0


class AIProvider(ABC):
    """
    Abstract AI provider interface.

    All LLM/AI calls in the HRMS platform must go through this interface.
    This enables:
    - Provider swapping without code changes
    - Cost tracking
    - Rate limiting
    - Mock providers for testing
    - Audit logging of all AI calls
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the AI provider (e.g., 'openai', 'google', 'anthropic')."""
        ...

    @abstractmethod
    async def complete(self, request: AICompletionRequest) -> AICompletionResponse:
        """
        Generate a text completion.

        Args:
            request: Structured completion request.

        Returns:
            Completion response with generated content and token usage.
        """
        ...

    @abstractmethod
    async def embed(self, request: AIEmbeddingRequest) -> AIEmbeddingResponse:
        """
        Generate a text embedding vector.

        Args:
            request: Embedding request containing the text to embed.

        Returns:
            Embedding response with the vector and token count.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider API is reachable and operational."""
        ...


class MockAIProvider(AIProvider):
    """
    Mock AI provider for testing and development.

    Returns predictable, deterministic responses.
    No real API calls are made.
    """

    @property
    def provider_name(self) -> str:
        return "mock"

    async def complete(self, request: AICompletionRequest) -> AICompletionResponse:
        return AICompletionResponse(
            content='{"result": "mock_response", "confidence": 0.85}',
            model=request.model,
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        )

    async def embed(self, request: AIEmbeddingRequest) -> AIEmbeddingResponse:
        # Return a deterministic zero vector for testing
        return AIEmbeddingResponse(
            vector=[0.0] * 1536,
            model=request.model,
            token_count=len(request.text.split()),
        )

    async def health_check(self) -> bool:
        return True
