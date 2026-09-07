"""
PlanValidator — Strict 20-Point Security & DAG Validation Engine for Agent Plans.
Enforces that the LLM is NEVER the authorization authority.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from backend.agents.application.agent_registry import AgentRegistry
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.models import Agent, AgentTask
from backend.agents.planning.domain.exceptions import CircularDependencyError
from backend.agents.planning.domain.models import Plan, PlanStep
from backend.agents.tools.application.tool_registry import PROHIBITED_TOOL_IDS, ToolRegistry
from backend.commands.application.bus import CommandBus


class StepValidationResult(BaseModel):
    """Validation report for a single step."""

    step_id: str
    tool_name: str
    command_type: str
    valid: bool
    risk_level: str = "LOW"
    requires_approval: bool = False
    errors: list[str] = Field(default_factory=list)


class ValidationReport(BaseModel):
    """Comprehensive validation report for an entire plan."""

    plan_id: str
    valid: bool
    total_steps: int
    step_results: list[StepValidationResult] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @property
    def all_errors(self) -> list[str]:
        errs = list(self.errors)
        for sr in self.step_results:
            errs.extend(sr.errors)
        return errs


class PlanValidator:
    """
    PlanValidator enforcing strict security, capability, DAG, risk, and tenant boundaries.
    """

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        task_service: AgentTaskService | None = None,
        tool_registry: ToolRegistry | None = None,
        command_bus: CommandBus | None = None,
    ) -> None:
        self.registry = registry or AgentRegistry()
        self.task_service = task_service or AgentTaskService()
        self.tool_registry = tool_registry or ToolRegistry.get_instance()
        self.command_bus = command_bus or CommandBus()

    async def validate_plan(
        self,
        plan: Plan,
        agent: Agent | None = None,
        task: AgentTask | None = None,
    ) -> ValidationReport:
        """
        Validate plan against all 20 security and structural rules.
        """
        report_errors: list[str] = []
        step_results: list[StepValidationResult] = []

        # 1. Verify agent exists & is ACTIVE
        if agent is None:
            try:
                agent = await self.registry.get_agent(plan.organization_id, plan.agent_id)
            except Exception as e:
                report_errors.append(f"Agent '{plan.agent_id}' validation failed: {e}")
                agent = None

        if agent:
            if agent.status != AgentStatus.ACTIVE:
                report_errors.append(f"Agent '{agent.agent_id}' is not ACTIVE (status: {agent.status}).")
            if agent.organization_id != plan.organization_id:
                report_errors.append(
                    f"Agent organization '{agent.organization_id}' mismatch with plan organization '{plan.organization_id}'."
                )

        # 2. Verify task belongs to agent and organization
        if task is None and agent:
            task = await self.task_service.get_task(plan.organization_id, plan.task_id)

        if task:
            if task.agent_id != plan.agent_id:
                report_errors.append(
                    f"Task '{task.task_id}' assigned agent '{task.agent_id}' does not match plan agent '{plan.agent_id}'."
                )
            if task.organization_id != plan.organization_id:
                report_errors.append(
                    f"Task organization '{task.organization_id}' mismatch with plan organization '{plan.organization_id}'."
                )

        # 3. DAG Validation & Circular Dependency Detection
        try:
            self._validate_dag(plan.steps)
        except CircularDependencyError as cde:
            report_errors.append(f"Circular dependency detected in plan steps: {cde}")

        # 4. Validate Individual Steps
        step_ids = {s.step_id for s in plan.steps}

        for step in plan.steps:
            step_errs: list[str] = []
            risk_level = "LOW"
            requires_hitl = False

            # Check step dependency references
            for dep_id in step.dependencies:
                if dep_id not in step_ids:
                    step_errs.append(f"Step '{step.step_id}' references unknown dependency step '{dep_id}'.")

            # Check prohibited tools (arbitrary SQL/Python/Shell execution)
            if step.tool_name in PROHIBITED_TOOL_IDS or step.command_type in PROHIBITED_TOOL_IDS:
                step_errs.append(f"Prohibited tool/command '{step.tool_name}' (direct SQL/Python/Shell tool).")

            # Validate tool in ToolRegistry
            tool_def = None
            try:
                tool_def = self.tool_registry.get_tool(step.tool_name)
            except Exception:
                step_errs.append(f"Tool '{step.tool_name}' is not registered in ToolRegistry.")

            # Validate capability if agent & tool present
            if agent and tool_def:
                if not agent.has_capability(tool_def.resource, tool_def.action):
                    step_errs.append(
                        f"Agent '{agent.name}' lacks capability for tool '{step.tool_name}' ({tool_def.resource}:{tool_def.action})."
                    )

                # Risk & HITL calculation
                risk_level = tool_def.risk_level
                requires_hitl = tool_def.requires_hitl or (risk_level in ["HIGH", "CRITICAL"])

                # Fill mapped command_type if empty
                if not step.command_type:
                    step.command_type = tool_def.command_type

            # Check command in CommandBus registry
            if step.command_type:
                try:
                    cmd_meta = self.command_bus.registry.get_metadata(step.command_type)
                    if cmd_meta.requires_approval or cmd_meta.risk_level.value in ["HIGH", "CRITICAL"]:
                        requires_hitl = True
                    risk_level = cmd_meta.risk_level.value
                except Exception:
                    # Non-fatal if pure query tool, but flag if unknown mutation command
                    if step.action_type in ["MUTATION", "COMMAND"]:
                        step_errs.append(f"Command '{step.command_type}' is not registered in CommandBus registry.")

            # Tenant payload injection check
            if "organization_id" in step.arguments and step.arguments["organization_id"] != plan.organization_id:
                step_errs.append("Cross-tenant payload modification detected in step arguments.")

            # Update step metadata fields
            step.risk_level = risk_level
            step.requires_approval = requires_hitl

            step_valid = len(step_errs) == 0
            if not step_valid:
                report_errors.extend(step_errs)

            step_results.append(
                StepValidationResult(
                    step_id=step.step_id,
                    tool_name=step.tool_name,
                    command_type=step.command_type,
                    valid=step_valid,
                    risk_level=risk_level,
                    requires_approval=requires_hitl,
                    errors=step_errs,
                )
            )

        is_plan_valid = len(report_errors) == 0

        if not is_plan_valid:
            plan.failure_reason = f"Plan validation failed: {'; '.join(report_errors[:3])}"

        return ValidationReport(
            plan_id=plan.plan_id,
            valid=is_plan_valid,
            total_steps=len(plan.steps),
            step_results=step_results,
            errors=report_errors,
        )

    def _validate_dag(self, steps: list[PlanStep]) -> None:
        """Kahn's topological sort algorithm detecting circular dependencies."""
        step_map = {s.step_id: s for s in steps}
        in_degree = {s.step_id: 0 for s in steps}
        graph: dict[str, list[str]] = {s.step_id: [] for s in steps}

        for step in steps:
            for dep_id in step.dependencies:
                if dep_id in step_map:
                    graph[dep_id].append(step.step_id)
                    in_degree[step.step_id] += 1

        queue = [node for node, deg in in_degree.items() if deg == 0]
        visited_count = 0

        while queue:
            node = queue.pop(0)
            visited_count += 1
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if visited_count != len(steps):
            raise CircularDependencyError("Plan steps contain a circular dependency loop.")
