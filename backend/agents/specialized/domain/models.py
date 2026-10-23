"""
Specialized Agent Domain Models — Declarative capability profiles, tool policies, knowledge policies, memory policies, and agent definitions.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.memory.hierarchy.enums import MemoryTier
from backend.agents.specialized.domain.enums import AutonomyMode, SpecializedAgentRole, ToolAccessLevel
from backend.ai.gateway.router import RoutingTier
from backend.knowledge.domain.enums import AccessScopeType, KnowledgeClassification


class CapabilityProfile(BaseModel):
    """Declarative capability contract specifying what an agent is permitted and prohibited from doing."""

    capabilities: list[str] = Field(
        default_factory=list,
        description="Explicit capability tokens granted e.g. ['employee:read', 'recruitment:screen']",
    )
    prohibited_capabilities: list[str] = Field(
        default_factory=list,
        description="Explicitly prohibited capability tokens e.g. ['employee:terminate', 'payroll:modify']",
    )

    def has_capability(self, capability: str) -> bool:
        """Check if capability is explicitly granted and not prohibited."""
        if capability in self.prohibited_capabilities:
            return False
        return capability in self.capabilities


class ToolPolicy(BaseModel):
    """Matrix of tool access levels for an agent. Undeclared tools default to DENY."""

    tool_access: dict[str, ToolAccessLevel] = Field(
        default_factory=dict,
        description="Map of tool_id -> ToolAccessLevel (ALLOW, DENY, REQUIRES_APPROVAL)",
    )

    def get_access_level(self, tool_id: str) -> ToolAccessLevel:
        """Resolve access level for tool. Default is DENY."""
        return self.tool_access.get(tool_id, ToolAccessLevel.DENY)

    def is_allowed(self, tool_id: str) -> bool:
        """Check if tool is directly permitted without per-action human approval."""
        return self.get_access_level(tool_id) == ToolAccessLevel.ALLOW

    def requires_approval(self, tool_id: str) -> bool:
        """Check if tool requires human approval prior to execution."""
        return self.get_access_level(tool_id) == ToolAccessLevel.REQUIRES_APPROVAL

    def is_prohibited(self, tool_id: str) -> bool:
        """Check if tool is denied."""
        return self.get_access_level(tool_id) == ToolAccessLevel.DENY


class KnowledgePolicy(BaseModel):
    """Declares permitted knowledge document scopes and max classification levels."""

    allowed_scopes: list[AccessScopeType] = Field(
        default_factory=list,
        description="Permitted AccessScopeTypes (e.g. PUBLIC, ORGANIZATION, DEPARTMENT, EMPLOYEE)",
    )
    max_classification: KnowledgeClassification = Field(
        default=KnowledgeClassification.INTERNAL,
        description="Highest confidentiality tier readable by this agent",
    )
    prohibited_scopes: list[AccessScopeType] = Field(
        default_factory=list,
        description="Explicitly prohibited scopes",
    )


class MemoryPolicy(BaseModel):
    """Declares permitted memory hierarchy tiers for an agent."""

    allowed_tiers: list[MemoryTier] = Field(
        default_factory=lambda: [MemoryTier.AGENT],
        description="Permitted tiers (AGENT, TEAM, ORGANIZATION, EMPLOYEE)",
    )
    primary_team_id: str | None = Field(
        default=None,
        description="Team ID boundary if TEAM tier is permitted",
    )

    def is_tier_allowed(self, tier: MemoryTier) -> bool:
        """Check if memory tier is permitted."""
        return tier in self.allowed_tiers


class EvaluationContract(BaseModel):
    """Auditing and quality SLA contract for evaluating agent trajectories."""

    accuracy_metric: str = Field(default="task_completion_rate")
    min_accuracy_score: float = Field(default=0.85)
    max_hallucination_rate: float = Field(default=0.02)
    unauthorized_retrieval_limit: int = Field(default=0)
    target_sla_seconds: int = Field(default=30)
    evaluation_criteria: list[str] = Field(
        default_factory=list,
        description="Domain specific evaluation criteria strings",
    )


class ModelRoutingPolicy(BaseModel):
    """Policy for AI Gateway LLM routing, token limits, and system instructions."""

    routing_tier: RoutingTier = Field(default=RoutingTier.BALANCED)
    temperature: float = Field(default=0.2)
    max_tokens: int = Field(default=2048)
    system_prompt_template: str = Field(default="")
    use_local_only: bool = Field(default=False)


class SpecializedAgentDefinition(BaseModel):
    """
    Declarative blueprint defining one of the 24 specialized AI HR agents.
    Inspectable without runtime execution.
    """

    role: SpecializedAgentRole
    display_name: str
    purpose: str
    responsibilities: list[str] = Field(default_factory=list)
    supervisor_role: SpecializedAgentRole | None = Field(default=None)
    capability_profile: CapabilityProfile
    tool_policy: ToolPolicy
    knowledge_policy: KnowledgePolicy
    memory_policy: MemoryPolicy
    evaluation_contract: EvaluationContract
    model_policy: ModelRoutingPolicy
    autonomy_mode: AutonomyMode = Field(default=AutonomyMode.SUPERVISED)
    max_execution_time_seconds: int = Field(default=120)
    max_tool_calls_per_task: int = Field(default=15)
    max_delegation_depth: int = Field(default=2)
    daily_budget_usd: float = Field(default=5.0)
    version: str = Field(default="1.0.0")
    is_active: bool = Field(default=True)


class SpecializedAgentInstance(BaseModel):
    """
    Runtime instantiation of a SpecializedAgentDefinition bound to a specific tenant Organization and Actor.
    """

    instance_id: str = Field(default_factory=lambda: f"sp-inst-{uuid.uuid4()}")
    organization_id: str
    role: SpecializedAgentRole
    agent_id: str
    actor_id: str
    definition_version: str
    autonomy_mode: AutonomyMode
    is_enabled: bool = Field(default=True)
    custom_parameters: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
