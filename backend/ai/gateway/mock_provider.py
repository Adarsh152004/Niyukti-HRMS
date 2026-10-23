"""
Mock LLM Provider — Deterministic zero-network testing provider with Tool Calling support.
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


class MockLLMProvider(LLMProvider):
    """Deterministic in-memory mock provider for automated tests and offline execution."""

    def __init__(self, default_model: str = "mock-gpt-4o-mini") -> None:
        self.default_model = default_model
        self.fixed_responses: dict[str, Any] = {}
        self.fixed_tool_calls: dict[str, list[ToolCallProposal]] = {}
        self.call_history: list[dict[str, Any]] = []

    @property
    def provider_name(self) -> str:
        return "mock"

    def set_mock_response(self, prompt_substring: str, response: Any) -> None:
        """Register specific mock response for prompt matching."""
        self.fixed_responses[prompt_substring] = response

    def set_mock_tool_call(self, prompt_substring: str, tool_calls: list[ToolCallProposal]) -> None:
        """Register specific tool call proposal response for prompt matching."""
        self.fixed_tool_calls[prompt_substring] = tool_calls

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        self.call_history.append({"prompt": prompt, "system": system_instruction, "model": model})

        for key, resp in self.fixed_responses.items():
            if key in prompt:
                content = str(resp)
                break
        else:
            content = f"Mock LLM completion for prompt: {prompt[:60]}..."

        usage = TokenUsage(
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(content.split()),
            total_tokens=len(prompt.split()) + len(content.split()),
            estimated_cost_usd=0.0001,
        )

        return ModelResponse(
            content=content,
            model_name=model or self.default_model,
            provider=self.provider_name,
            usage=usage,
            latency_ms=10,
        )

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> StructuredModelResponse[T]:
        self.call_history.append({"prompt": prompt, "schema": response_schema.__name__, "model": model})

        for key, resp in self.fixed_responses.items():
            if key in prompt:
                if isinstance(resp, response_schema):
                    data = resp
                elif isinstance(resp, dict):
                    data = response_schema.model_validate(resp)
                elif isinstance(resp, str):
                    data = response_schema.model_validate_json(resp)
                else:
                    data = response_schema.model_validate({})
                break
        else:
            # Generate default instance of schema
            try:
                data = response_schema.model_validate({})
            except Exception:
                fields: dict[str, Any] = {}
                for name, field_info in response_schema.model_fields.items():
                    if field_info.annotation is str:
                        fields[name] = "Mock String"
                    elif field_info.annotation is int:
                        fields[name] = 1
                    elif field_info.annotation is float:
                        fields[name] = 1.0
                    elif field_info.annotation is bool:
                        fields[name] = True
                    elif field_info.annotation == list[str]:
                        fields[name] = ["mock_item"]
                    else:
                        fields[name] = None
                data = response_schema.model_validate(fields)

        raw_content = data.model_dump_json()
        usage = TokenUsage(
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(raw_content.split()),
            total_tokens=len(prompt.split()) + len(raw_content.split()),
            estimated_cost_usd=0.0002,
        )

        return StructuredModelResponse(
            data=data,
            raw_content=raw_content,
            model_name=model or self.default_model,
            provider=self.provider_name,
            usage=usage,
            latency_ms=15,
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
        self.call_history.append({"prompt": prompt, "tools_count": len(tools), "model": model})

        for key, tool_list in self.fixed_tool_calls.items():
            if key in prompt:
                return ToolCallResponse(
                    content="",
                    tool_calls=tool_list,
                    model_name=model or self.default_model,
                    provider=self.provider_name,
                    usage=TokenUsage(
                        prompt_tokens=len(prompt.split()),
                        completion_tokens=10,
                        total_tokens=len(prompt.split()) + 10,
                        estimated_cost_usd=0.0001,
                    ),
                    latency_ms=12,
                )

        # If tools provided and tool_choice is forced or matched in prompt, invoke first available tool
        selected_tool = None
        if tools:
            for t in tools:
                t_name = t.get("name") or t.get("tool_id", "")
                if t_name.lower() in prompt.lower():
                    selected_tool = t
                    break
            if not selected_tool and tool_choice != "none":
                selected_tool = tools[0]

        tool_calls: list[ToolCallProposal] = []
        if selected_tool:
            t_id = selected_tool.get("tool_id") or selected_tool.get("name", "tool.default")
            tool_calls.append(
                ToolCallProposal(
                    call_id=f"call_{uuid.uuid4().hex[:8]}",
                    tool_id=t_id,
                    tool_name=selected_tool.get("name", t_id),
                    arguments=selected_tool.get("default_args", {"query": "test"}),
                )
            )

        return ToolCallResponse(
            content="Mock tool execution proposal." if not tool_calls else "",
            tool_calls=tool_calls,
            model_name=model or self.default_model,
            provider=self.provider_name,
            usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=15,
                total_tokens=len(prompt.split()) + 15,
                estimated_cost_usd=0.0001,
            ),
            latency_ms=10,
        )

    async def embed_text(self, text: str, model: str | None = None) -> Sequence[float]:
        """Generate deterministic 128-dimensional pseudo-embedding vector."""
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        vec = [(int(sha[i % len(sha)], 16) / 15.0) for i in range(128)]
        return vec
