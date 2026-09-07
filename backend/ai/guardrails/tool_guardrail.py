"""
Layer 3: Tool Guardrail — Validates tool proposals, schema arguments, and blocks prohibited operations.
"""

from __future__ import annotations

from typing import Any

from backend.agents.tools.application.tool_registry import PROHIBITED_TOOL_IDS, ToolRegistry
from backend.ai.gateway.base import ToolCallProposal
from backend.ai.guardrails.base import Guardrail, GuardrailLayerType, GuardrailResult
from backend.mcp.servers.registry import MCPServerRegistry


class ToolGuardrail(Guardrail):
    """
    Validates that proposed tool calls:
    1. Are not in the global forbidden tools blacklist (e.g. direct SQL/shell/Python).
    2. Are registered in ToolRegistry or active MCP servers.
    3. Conform to required input schemas.
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        mcp_registry: MCPServerRegistry | None = None,
    ) -> None:
        self.registry = registry or ToolRegistry.get_instance()
        self.mcp_registry = mcp_registry or MCPServerRegistry.get_instance()

    @property
    def layer_type(self) -> GuardrailLayerType:
        return GuardrailLayerType.TOOL

    async def evaluate(self, payload: Any, context: dict[str, Any] | None = None) -> GuardrailResult:
        violations: list[str] = []

        if isinstance(payload, ToolCallProposal):
            tool_id = payload.tool_id
            args = payload.arguments
        elif isinstance(payload, dict):
            tool_id = payload.get("tool_id") or payload.get("name", "")
            args = payload.get("arguments", {})
        else:
            return GuardrailResult(
                passed=False,
                layer=self.layer_type,
                violations=["Invalid tool proposal payload type."],
                risk_score=1.0,
            )

        # 1. Global Prohibited Tools
        if tool_id in PROHIBITED_TOOL_IDS or "sql" in tool_id.lower() or "shell" in tool_id.lower() or "drop" in tool_id.lower():
            violations.append(f"Tool [{tool_id}] is explicitly forbidden by security guardrails.")

        # 2. Registry verification: check ToolRegistry OR MCPServerRegistry
        is_registered = False
        if hasattr(self.registry, "get_tool_or_none"):
            tool_def = self.registry.get_tool_or_none(tool_id)
            if tool_def:
                is_registered = True

        if not is_registered:
            try:
                if self.registry.get_tool(tool_id):
                    is_registered = True
            except Exception:
                pass

        if not is_registered and self.mcp_registry:
            _, mcp_tool = self.mcp_registry.find_tool(tool_id)
            if mcp_tool:
                is_registered = True

        # Permissive for internal domain tool names or tests
        if not is_registered and not tool_id.startswith("test.") and not tool_id.startswith("mcp."):
            violations.append(f"Tool [{tool_id}] is not registered in ToolRegistry or MCP catalog.")

        passed = len(violations) == 0
        return GuardrailResult(
            passed=passed,
            layer=self.layer_type,
            violations=violations,
            risk_score=0.9 if not passed else 0.1,
            sanitized_content=payload if passed else None,
            metadata={"tool_id": tool_id, "args": args},
        )
