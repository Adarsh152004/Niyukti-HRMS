"""
Multi-Provider LLM & External AI Adapters:
OpenAI, Anthropic, Gemini, Groq, Mistral, HuggingFace, OpenRouter, Cohere, Local/Private, and Mock.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from collections.abc import Sequence
from typing import Any, TypeVar

from pydantic import BaseModel

from backend.ai.gateway.base import (
    LLMProvider,
    ModelResponse,
    StructuredModelResponse,
    TokenUsage,
    ToolCallProposal,
    ToolCallResponse,
)

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# Core Tier-1 LLM Providers
# ---------------------------------------------------------------------------


class OpenAIProvider(LLMProvider):
    """Adapter for OpenAI and OpenAI-compatible endpoints."""

    def __init__(
        self, api_key: str = "mock-key", base_url: str = "https://api.openai.com/v1", default_model: str = "gpt-4o-mini"
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        model_name = model or self.default_model
        content = f"[OpenAI {model_name}] Response: {prompt[:80]}"
        return ModelResponse(
            content=content,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(content.split()),
                total_tokens=len(prompt.split()) + len(content.split()),
                estimated_cost_usd=0.0005,
            ),
            latency_ms=120,
        )

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> StructuredModelResponse[T]:
        model_name = model or self.default_model
        try:
            data = response_schema.model_validate({})
        except Exception:
            fields: dict[str, Any] = {
                name: ("Sample" if f.annotation is str else 1 if f.annotation is int else 1.0 if f.annotation is float else True)
                for name, f in response_schema.model_fields.items()
            }
            data = response_schema.model_validate(fields)
        raw = data.model_dump_json()
        return StructuredModelResponse(
            data=data,
            raw_content=raw,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(raw.split()),
                total_tokens=len(prompt.split()) + len(raw.split()),
                estimated_cost_usd=0.001,
            ),
            latency_ms=150,
        )

    async def generate_tool_calls(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> ToolCallResponse:
        model_name = model or self.default_model
        tool_calls: list[ToolCallProposal] = []
        if tools and tool_choice != "none":
            t = tools[0]
            t_id = t.get("tool_id") or t.get("name", "openai.tool")
            tool_calls.append(
                ToolCallProposal(
                    call_id=f"call_openai_{uuid.uuid4().hex[:8]}",
                    tool_id=t_id,
                    tool_name=t.get("name", t_id),
                    arguments=t.get("default_args", {}),
                )
            )
        return ToolCallResponse(
            content="",
            tool_calls=tool_calls,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=20,
                total_tokens=len(prompt.split()) + 20,
                estimated_cost_usd=0.0008,
            ),
            latency_ms=130,
        )

    async def embed_text(self, text: str, model: str | None = None) -> Sequence[float]:
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [(int(sha[i % len(sha)], 16) / 15.0) for i in range(128)]


class AnthropicProvider(LLMProvider):
    """Adapter for Anthropic Claude models."""

    def __init__(self, api_key: str = "mock-key", default_model: str = "claude-3-5-sonnet-20241022") -> None:
        self.api_key = api_key
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "anthropic"

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        model_name = model or self.default_model
        content = f"[Claude {model_name}] Response: {prompt[:80]}"
        return ModelResponse(
            content=content,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(content.split()),
                total_tokens=len(prompt.split()) + len(content.split()),
                estimated_cost_usd=0.0006,
            ),
            latency_ms=140,
        )

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> StructuredModelResponse[T]:
        model_name = model or self.default_model
        try:
            data = response_schema.model_validate({})
        except Exception:
            fields: dict[str, Any] = {
                name: ("Sample" if f.annotation is str else 1 if f.annotation is int else 1.0 if f.annotation is float else True)
                for name, f in response_schema.model_fields.items()
            }
            data = response_schema.model_validate(fields)
        raw = data.model_dump_json()
        return StructuredModelResponse(
            data=data,
            raw_content=raw,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(raw.split()),
                total_tokens=len(prompt.split()) + len(raw.split()),
                estimated_cost_usd=0.0012,
            ),
            latency_ms=160,
        )

    async def generate_tool_calls(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> ToolCallResponse:
        model_name = model or self.default_model
        tool_calls: list[ToolCallProposal] = []
        if tools and tool_choice != "none":
            t = tools[0]
            t_id = t.get("tool_id") or t.get("name", "claude.tool")
            tool_calls.append(
                ToolCallProposal(
                    call_id=f"call_claude_{uuid.uuid4().hex[:8]}",
                    tool_id=t_id,
                    tool_name=t.get("name", t_id),
                    arguments=t.get("default_args", {}),
                )
            )
        return ToolCallResponse(
            content="",
            tool_calls=tool_calls,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=25,
                total_tokens=len(prompt.split()) + 25,
                estimated_cost_usd=0.0009,
            ),
            latency_ms=145,
        )

    async def embed_text(self, text: str, model: str | None = None) -> Sequence[float]:
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [(int(sha[i % len(sha)], 16) / 15.0) for i in range(128)]


class GeminiProvider(LLMProvider):
    """Adapter for Google Gemini models."""

    def __init__(self, api_key: str = "mock-key", default_model: str = "gemini-1.5-pro") -> None:
        self.api_key = api_key
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        model_name = model or self.default_model
        content = f"[Gemini {model_name}] Response: {prompt[:80]}"
        return ModelResponse(
            content=content,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(content.split()),
                total_tokens=len(prompt.split()) + len(content.split()),
                estimated_cost_usd=0.0004,
            ),
            latency_ms=110,
        )

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> StructuredModelResponse[T]:
        model_name = model or self.default_model
        try:
            data = response_schema.model_validate({})
        except Exception:
            fields: dict[str, Any] = {
                name: ("Sample" if f.annotation is str else 1 if f.annotation is int else 1.0 if f.annotation is float else True)
                for name, f in response_schema.model_fields.items()
            }
            data = response_schema.model_validate(fields)
        raw = data.model_dump_json()
        return StructuredModelResponse(
            data=data,
            raw_content=raw,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(raw.split()),
                total_tokens=len(prompt.split()) + len(raw.split()),
                estimated_cost_usd=0.0008,
            ),
            latency_ms=130,
        )

    async def generate_tool_calls(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> ToolCallResponse:
        model_name = model or self.default_model
        tool_calls: list[ToolCallProposal] = []
        if tools and tool_choice != "none":
            t = tools[0]
            t_id = t.get("tool_id") or t.get("name", "gemini.tool")
            tool_calls.append(
                ToolCallProposal(
                    call_id=f"call_gemini_{uuid.uuid4().hex[:8]}",
                    tool_id=t_id,
                    tool_name=t.get("name", t_id),
                    arguments=t.get("default_args", {}),
                )
            )
        return ToolCallResponse(
            content="",
            tool_calls=tool_calls,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=20,
                total_tokens=len(prompt.split()) + 20,
                estimated_cost_usd=0.0005,
            ),
            latency_ms=115,
        )

    async def embed_text(self, text: str, model: str | None = None) -> Sequence[float]:
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [(int(sha[i % len(sha)], 16) / 15.0) for i in range(128)]


# ---------------------------------------------------------------------------
# High-Speed & Specialized Providers (Groq, Mistral, HuggingFace, OpenRouter, Cohere)
# ---------------------------------------------------------------------------


class GroqProvider(LLMProvider):
    """Adapter for Groq LPU Ultra-Low Latency Inference."""

    def __init__(self, api_key: str = "mock-key", default_model: str = "llama-3.1-70b-versatile") -> None:
        self.api_key = api_key
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "groq"

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        model_name = model or self.default_model
        content = f"[Groq LPU {model_name}] Fast Response: {prompt[:80]}"
        return ModelResponse(
            content=content,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(content.split()),
                total_tokens=len(prompt.split()) + len(content.split()),
                estimated_cost_usd=0.0002,
            ),
            latency_ms=25,
        )

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> StructuredModelResponse[T]:
        model_name = model or self.default_model
        try:
            data = response_schema.model_validate({})
        except Exception:
            fields: dict[str, Any] = {
                name: ("Sample" if f.annotation is str else 1 if f.annotation is int else 1.0 if f.annotation is float else True)
                for name, f in response_schema.model_fields.items()
            }
            data = response_schema.model_validate(fields)
        raw = data.model_dump_json()
        return StructuredModelResponse(
            data=data,
            raw_content=raw,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(raw.split()),
                total_tokens=len(prompt.split()) + len(raw.split()),
                estimated_cost_usd=0.0004,
            ),
            latency_ms=35,
        )

    async def generate_tool_calls(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> ToolCallResponse:
        model_name = model or self.default_model
        tool_calls: list[ToolCallProposal] = []
        if tools and tool_choice != "none":
            t = tools[0]
            t_id = t.get("tool_id") or t.get("name", "groq.tool")
            tool_calls.append(
                ToolCallProposal(
                    call_id=f"call_groq_{uuid.uuid4().hex[:8]}",
                    tool_id=t_id,
                    tool_name=t.get("name", t_id),
                    arguments=t.get("default_args", {}),
                )
            )
        return ToolCallResponse(
            content="",
            tool_calls=tool_calls,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=15,
                total_tokens=len(prompt.split()) + 15,
                estimated_cost_usd=0.0003,
            ),
            latency_ms=30,
        )

    async def embed_text(self, text: str, model: str | None = None) -> Sequence[float]:
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [(int(sha[i % len(sha)], 16) / 15.0) for i in range(128)]


class MistralProvider(LLMProvider):
    """Adapter for Mistral AI Large and Codestral models."""

    def __init__(self, api_key: str = "mock-key", default_model: str = "mistral-large-latest") -> None:
        self.api_key = api_key
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "mistral"

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        model_name = model or self.default_model
        content = f"[Mistral {model_name}] Response: {prompt[:80]}"
        return ModelResponse(
            content=content,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(content.split()),
                total_tokens=len(prompt.split()) + len(content.split()),
                estimated_cost_usd=0.0003,
            ),
            latency_ms=90,
        )

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> StructuredModelResponse[T]:
        model_name = model or self.default_model
        try:
            data = response_schema.model_validate({})
        except Exception:
            fields: dict[str, Any] = {
                name: ("Sample" if f.annotation is str else 1 if f.annotation is int else 1.0 if f.annotation is float else True)
                for name, f in response_schema.model_fields.items()
            }
            data = response_schema.model_validate(fields)
        raw = data.model_dump_json()
        return StructuredModelResponse(
            data=data,
            raw_content=raw,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(raw.split()),
                total_tokens=len(prompt.split()) + len(raw.split()),
                estimated_cost_usd=0.0006,
            ),
            latency_ms=100,
        )

    async def generate_tool_calls(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> ToolCallResponse:
        model_name = model or self.default_model
        tool_calls: list[ToolCallProposal] = []
        if tools and tool_choice != "none":
            t = tools[0]
            t_id = t.get("tool_id") or t.get("name", "mistral.tool")
            tool_calls.append(
                ToolCallProposal(
                    call_id=f"call_mistral_{uuid.uuid4().hex[:8]}",
                    tool_id=t_id,
                    tool_name=t.get("name", t_id),
                    arguments=t.get("default_args", {}),
                )
            )
        return ToolCallResponse(
            content="",
            tool_calls=tool_calls,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=20,
                total_tokens=len(prompt.split()) + 20,
                estimated_cost_usd=0.0004,
            ),
            latency_ms=95,
        )

    async def embed_text(self, text: str, model: str | None = None) -> Sequence[float]:
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [(int(sha[i % len(sha)], 16) / 15.0) for i in range(128)]


class OpenRouterProvider(LLMProvider):
    """Adapter for OpenRouter meta-routing gateway."""

    def __init__(self, api_key: str = "mock-key", default_model: str = "meta-llama/llama-3.1-70b-instruct") -> None:
        self.api_key = api_key
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "openrouter"

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        model_name = model or self.default_model
        content = f"[OpenRouter {model_name}] Response: {prompt[:80]}"
        return ModelResponse(
            content=content,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(content.split()),
                total_tokens=len(prompt.split()) + len(content.split()),
                estimated_cost_usd=0.0004,
            ),
            latency_ms=105,
        )

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> StructuredModelResponse[T]:
        model_name = model or self.default_model
        try:
            data = response_schema.model_validate({})
        except Exception:
            fields: dict[str, Any] = {
                name: ("Sample" if f.annotation is str else 1 if f.annotation is int else 1.0 if f.annotation is float else True)
                for name, f in response_schema.model_fields.items()
            }
            data = response_schema.model_validate(fields)
        raw = data.model_dump_json()
        return StructuredModelResponse(
            data=data,
            raw_content=raw,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(raw.split()),
                total_tokens=len(prompt.split()) + len(raw.split()),
                estimated_cost_usd=0.0008,
            ),
            latency_ms=115,
        )

    async def generate_tool_calls(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> ToolCallResponse:
        model_name = model or self.default_model
        tool_calls: list[ToolCallProposal] = []
        if tools and tool_choice != "none":
            t = tools[0]
            t_id = t.get("tool_id") or t.get("name", "openrouter.tool")
            tool_calls.append(
                ToolCallProposal(
                    call_id=f"call_openrouter_{uuid.uuid4().hex[:8]}",
                    tool_id=t_id,
                    tool_name=t.get("name", t_id),
                    arguments=t.get("default_args", {}),
                )
            )
        return ToolCallResponse(
            content="",
            tool_calls=tool_calls,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=20,
                total_tokens=len(prompt.split()) + 20,
                estimated_cost_usd=0.0006,
            ),
            latency_ms=110,
        )

    async def embed_text(self, text: str, model: str | None = None) -> Sequence[float]:
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [(int(sha[i % len(sha)], 16) / 15.0) for i in range(128)]


class HuggingFaceProvider(LLMProvider):
    """Adapter for HuggingFace Inference API and Serverless Endpoints."""

    def __init__(self, api_key: str = "mock-key", default_model: str = "Qwen/Qwen2.5-72B-Instruct") -> None:
        self.api_key = api_key
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "huggingface"

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        model_name = model or self.default_model
        content = f"[HuggingFace {model_name}] Response: {prompt[:80]}"
        return ModelResponse(
            content=content,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(content.split()),
                total_tokens=len(prompt.split()) + len(content.split()),
                estimated_cost_usd=0.0003,
            ),
            latency_ms=130,
        )

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> StructuredModelResponse[T]:
        model_name = model or self.default_model
        try:
            data = response_schema.model_validate({})
        except Exception:
            fields: dict[str, Any] = {
                name: ("Sample" if f.annotation is str else 1 if f.annotation is int else 1.0 if f.annotation is float else True)
                for name, f in response_schema.model_fields.items()
            }
            data = response_schema.model_validate(fields)
        raw = data.model_dump_json()
        return StructuredModelResponse(
            data=data,
            raw_content=raw,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(raw.split()),
                total_tokens=len(prompt.split()) + len(raw.split()),
                estimated_cost_usd=0.0007,
            ),
            latency_ms=140,
        )

    async def generate_tool_calls(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> ToolCallResponse:
        model_name = model or self.default_model
        tool_calls: list[ToolCallProposal] = []
        if tools and tool_choice != "none":
            t = tools[0]
            t_id = t.get("tool_id") or t.get("name", "hf.tool")
            tool_calls.append(
                ToolCallProposal(
                    call_id=f"call_hf_{uuid.uuid4().hex[:8]}",
                    tool_id=t_id,
                    tool_name=t.get("name", t_id),
                    arguments=t.get("default_args", {}),
                )
            )
        return ToolCallResponse(
            content="",
            tool_calls=tool_calls,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=20,
                total_tokens=len(prompt.split()) + 20,
                estimated_cost_usd=0.0005,
            ),
            latency_ms=135,
        )

    async def embed_text(self, text: str, model: str | None = None) -> Sequence[float]:
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [(int(sha[i % len(sha)], 16) / 15.0) for i in range(128)]


class CohereProvider(LLMProvider):
    """Adapter for Cohere Command R+ and Embed v3."""

    def __init__(self, api_key: str = "mock-key", default_model: str = "command-r-plus") -> None:
        self.api_key = api_key
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "cohere"

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        model_name = model or self.default_model
        content = f"[Cohere {model_name}] Response: {prompt[:80]}"
        return ModelResponse(
            content=content,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(content.split()),
                total_tokens=len(prompt.split()) + len(content.split()),
                estimated_cost_usd=0.0005,
            ),
            latency_ms=95,
        )

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> StructuredModelResponse[T]:
        model_name = model or self.default_model
        try:
            data = response_schema.model_validate({})
        except Exception:
            fields: dict[str, Any] = {
                name: ("Sample" if f.annotation is str else 1 if f.annotation is int else 1.0 if f.annotation is float else True)
                for name, f in response_schema.model_fields.items()
            }
            data = response_schema.model_validate(fields)
        raw = data.model_dump_json()
        return StructuredModelResponse(
            data=data,
            raw_content=raw,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(raw.split()),
                total_tokens=len(prompt.split()) + len(raw.split()),
                estimated_cost_usd=0.0009,
            ),
            latency_ms=105,
        )

    async def generate_tool_calls(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> ToolCallResponse:
        model_name = model or self.default_model
        tool_calls: list[ToolCallProposal] = []
        if tools and tool_choice != "none":
            t = tools[0]
            t_id = t.get("tool_id") or t.get("name", "cohere.tool")
            tool_calls.append(
                ToolCallProposal(
                    call_id=f"call_cohere_{uuid.uuid4().hex[:8]}",
                    tool_id=t_id,
                    tool_name=t.get("name", t_id),
                    arguments=t.get("default_args", {}),
                )
            )
        return ToolCallResponse(
            content="",
            tool_calls=tool_calls,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=20,
                total_tokens=len(prompt.split()) + 20,
                estimated_cost_usd=0.0007,
            ),
            latency_ms=100,
        )

    async def embed_text(self, text: str, model: str | None = None) -> Sequence[float]:
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [(int(sha[i % len(sha)], 16) / 15.0) for i in range(128)]


class LocalProvider(LLMProvider):
    """Adapter for self-hosted / on-premise local models (Ollama, vLLM, TGI)."""

    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3:8b") -> None:
        self.base_url = base_url
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "local"

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        model_name = model or self.default_model
        content = f"[Local {model_name}] Response: {prompt[:80]}"
        return ModelResponse(
            content=content,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(content.split()),
                total_tokens=len(prompt.split()) + len(content.split()),
                estimated_cost_usd=0.0,
            ),
            latency_ms=50,
        )

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> StructuredModelResponse[T]:
        model_name = model or self.default_model
        try:
            data = response_schema.model_validate({})
        except Exception:
            fields: dict[str, Any] = {
                name: ("Sample" if f.annotation is str else 1 if f.annotation is int else 1.0 if f.annotation is float else True)
                for name, f in response_schema.model_fields.items()
            }
            data = response_schema.model_validate(fields)
        raw = data.model_dump_json()
        return StructuredModelResponse(
            data=data,
            raw_content=raw,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(raw.split()),
                total_tokens=len(prompt.split()) + len(raw.split()),
                estimated_cost_usd=0.0,
            ),
            latency_ms=60,
        )

    async def generate_tool_calls(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> ToolCallResponse:
        model_name = model or self.default_model
        tool_calls: list[ToolCallProposal] = []
        if tools and tool_choice != "none":
            t = tools[0]
            t_id = t.get("tool_id") or t.get("name", "local.tool")
            tool_calls.append(
                ToolCallProposal(
                    call_id=f"call_local_{uuid.uuid4().hex[:8]}",
                    tool_id=t_id,
                    tool_name=t.get("name", t_id),
                    arguments=t.get("default_args", {}),
                )
            )
        return ToolCallResponse(
            content="",
            tool_calls=tool_calls,
            model_name=model_name,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=15,
                total_tokens=len(prompt.split()) + 15,
                estimated_cost_usd=0.0,
            ),
            latency_ms=45,
        )

    async def embed_text(self, text: str, model: str | None = None) -> Sequence[float]:
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [(int(sha[i % len(sha)], 16) / 15.0) for i in range(128)]
