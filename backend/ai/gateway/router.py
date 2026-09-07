"""
AI Gateway Router — Governed routing across model tiers with fallback cascades, circuit breaking, and native tool calling.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from enum import StrEnum
from typing import Any, TypeVar

from pydantic import BaseModel

from backend.ai.gateway.base import (
    LLMProvider,
    ModelResponse,
    StructuredModelResponse,
    ToolCallResponse,
)
from backend.ai.gateway.circuit_breaker import CircuitBreaker
from backend.ai.gateway.mock_provider import MockLLMProvider
from backend.ai.gateway.providers import (
    AnthropicProvider,
    GeminiProvider,
    LocalProvider,
    OpenAIProvider,
)
from backend.ai.gateway.telemetry import AITelemetryService

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class RoutingTier(StrEnum):
    FAST_ECONOMY = "FAST_ECONOMY"  # Simple queries, HR FAQ, summaries (small/cheap model)
    BALANCED = "BALANCED"  # Routine tasks, screening, leave drafting (medium model)
    HIGH_REASONING = "HIGH_REASONING"  # Complex planning, policy audits, strategy (top-tier model)
    EMBEDDING = "EMBEDDING"  # Embedding generation


class AIGatewayRouter:
    """Master AI Gateway router orchestrating multi-provider dispatch, tool calling, circuit breakers, and telemetry."""

    _instance: AIGatewayRouter | None = None

    def __init__(self) -> None:
        self.providers: dict[str, LLMProvider] = {
            "mock": MockLLMProvider(),
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "gemini": GeminiProvider(),
            "local": LocalProvider(),
        }
        self.circuit_breakers: dict[str, CircuitBreaker] = {name: CircuitBreaker(name) for name in self.providers}
        self.telemetry = AITelemetryService.get_instance()
        self.default_provider_name = "mock"
        self.fallback_chain = ["mock", "local", "gemini", "openai", "anthropic"]

    @classmethod
    def get_instance(cls) -> AIGatewayRouter:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_provider(self, provider: LLMProvider, is_default: bool = False) -> None:
        """Register an LLM provider adapter into the gateway."""
        name = provider.provider_name
        self.providers[name] = provider
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name)
        if is_default:
            self.default_provider_name = name
            if name in self.fallback_chain:
                self.fallback_chain.remove(name)
            self.fallback_chain.insert(0, name)

    async def generate_text(
        self,
        prompt: str,
        organization_id: str,
        tier: RoutingTier = RoutingTier.BALANCED,
        system_instruction: str | None = None,
        department_id: str | None = None,
        agent_id: str | None = None,
        task_id: str | None = None,
    ) -> ModelResponse:
        """Route text completion through healthy providers with fallback cascade."""
        errors: list[str] = []

        for provider_name in self.fallback_chain:
            provider = self.providers.get(provider_name)
            cb = self.circuit_breakers.get(provider_name)
            if not provider or not cb:
                continue

            if not await cb.can_execute():
                logger.warning(f"Circuit breaker for provider '{provider_name}' is OPEN. Trying next fallback.")
                continue

            try:
                resp = await provider.generate_text(prompt=prompt, system_instruction=system_instruction)
                await cb.record_success()

                await self.telemetry.record_usage(
                    organization_id=organization_id,
                    provider=provider_name,
                    model_name=resp.model_name,
                    prompt_tokens=resp.usage.prompt_tokens,
                    completion_tokens=resp.usage.completion_tokens,
                    cost_usd=resp.usage.estimated_cost_usd,
                    latency_ms=resp.latency_ms,
                    department_id=department_id,
                    agent_id=agent_id,
                    task_id=task_id,
                )
                return resp

            except Exception as e:
                await cb.record_failure(e)
                logger.error(f"Provider '{provider_name}' failed: {e}")
                errors.append(f"{provider_name}: {e!s}")

        raise RuntimeError(f"All AI Gateway providers failed in cascade: {', '.join(errors)}")

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        organization_id: str,
        tier: RoutingTier = RoutingTier.BALANCED,
        system_instruction: str | None = None,
        department_id: str | None = None,
        agent_id: str | None = None,
        task_id: str | None = None,
    ) -> StructuredModelResponse[T]:
        """Route structured completion with schema validation and fallback cascade."""
        errors: list[str] = []

        for provider_name in self.fallback_chain:
            provider = self.providers.get(provider_name)
            cb = self.circuit_breakers.get(provider_name)
            if not provider or not cb:
                continue

            if not await cb.can_execute():
                continue

            try:
                resp = await provider.generate_structured(
                    prompt=prompt,
                    response_schema=response_schema,
                    system_instruction=system_instruction,
                )
                await cb.record_success()

                await self.telemetry.record_usage(
                    organization_id=organization_id,
                    provider=provider_name,
                    model_name=resp.model_name,
                    prompt_tokens=resp.usage.prompt_tokens,
                    completion_tokens=resp.usage.completion_tokens,
                    cost_usd=resp.usage.estimated_cost_usd,
                    latency_ms=resp.latency_ms,
                    department_id=department_id,
                    agent_id=agent_id,
                    task_id=task_id,
                )
                return resp

            except Exception as e:
                await cb.record_failure(e)
                logger.error(f"Provider '{provider_name}' structured output failed: {e}")
                errors.append(f"{provider_name}: {e!s}")

        raise RuntimeError(f"All AI Gateway providers failed structured output cascade: {', '.join(errors)}")

    async def generate_tool_calls(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        organization_id: str,
        tier: RoutingTier = RoutingTier.BALANCED,
        system_instruction: str | None = None,
        tool_choice: str | dict[str, Any] = "auto",
        department_id: str | None = None,
        agent_id: str | None = None,
        task_id: str | None = None,
    ) -> ToolCallResponse:
        """Route native tool calling with schema binding and fallback cascade."""
        errors: list[str] = []

        for provider_name in self.fallback_chain:
            provider = self.providers.get(provider_name)
            cb = self.circuit_breakers.get(provider_name)
            if not provider or not cb:
                continue

            if not await cb.can_execute():
                continue

            try:
                resp = await provider.generate_tool_calls(
                    prompt=prompt,
                    tools=tools,
                    system_instruction=system_instruction,
                    tool_choice=tool_choice,
                )
                await cb.record_success()

                await self.telemetry.record_usage(
                    organization_id=organization_id,
                    provider=provider_name,
                    model_name=resp.model_name,
                    prompt_tokens=resp.usage.prompt_tokens,
                    completion_tokens=resp.usage.completion_tokens,
                    cost_usd=resp.usage.estimated_cost_usd,
                    latency_ms=resp.latency_ms,
                    department_id=department_id,
                    agent_id=agent_id,
                    task_id=task_id,
                )
                return resp

            except Exception as e:
                await cb.record_failure(e)
                logger.error(f"Provider '{provider_name}' tool calling failed: {e}")
                errors.append(f"{provider_name}: {e!s}")

        raise RuntimeError(f"All AI Gateway providers failed tool calling cascade: {', '.join(errors)}")

    async def embed_text(self, text: str, organization_id: str) -> Sequence[float]:
        """Generate text embedding through active embedding provider."""
        provider = self.providers.get(self.default_provider_name) or self.providers["mock"]
        return await provider.embed_text(text)
