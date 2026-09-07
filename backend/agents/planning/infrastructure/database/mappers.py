"""
Plan Mappers — Bi-directional mapping between domain Plan entities and SQLAlchemy ORM models.
"""

from __future__ import annotations

from backend.agents.planning.domain.enums import PlanStatus, StepStatus
from backend.agents.planning.domain.models import Plan, PlanStep
from backend.agents.planning.infrastructure.database.models import PlanModel, PlanStepModel


class PlanStepMapper:
    """Mapper for PlanStep model."""

    @staticmethod
    def to_domain(model: PlanStepModel) -> PlanStep:
        return PlanStep(
            step_id=model.id,
            sequence=model.sequence,
            description=model.description,
            action_type=model.action_type,
            tool_name=model.tool_name,
            command_type=model.command_type,
            arguments=model.arguments_json or {},
            dependencies=model.dependencies_json or [],
            status=StepStatus(model.status),
            retry_count=model.retry_count,
            result=model.result_json or {},
            failure_reason=model.failure_reason,
            requires_approval=model.requires_approval,
            risk_level=model.risk_level,
        )

    @staticmethod
    def to_model(step: PlanStep, plan_id: str) -> PlanStepModel:
        return PlanStepModel(
            id=step.step_id,
            plan_id=plan_id,
            sequence=step.sequence,
            description=step.description,
            action_type=step.action_type,
            tool_name=step.tool_name,
            command_type=step.command_type,
            arguments_json=step.arguments,
            dependencies_json=step.dependencies,
            status=step.status.value,
            retry_count=step.retry_count,
            result_json=step.result,
            failure_reason=step.failure_reason,
            requires_approval=step.requires_approval,
            risk_level=step.risk_level,
        )


class PlanMapper:
    """Mapper for Plan domain model."""

    @staticmethod
    def to_domain(model: PlanModel, step_models: list[PlanStepModel] | None = None) -> Plan:
        steps = [PlanStepMapper.to_domain(s) for s in (step_models or [])]
        steps.sort(key=lambda x: x.sequence)

        return Plan(
            plan_id=model.id,
            agent_id=model.agent_id,
            task_id=model.task_id,
            organization_id=model.organization_id,
            status=PlanStatus(model.status),
            objective=model.objective,
            steps=steps,
            current_step=model.current_step,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
            failure_reason=model.failure_reason,
            correlation_id=model.correlation_id,
        )

    @staticmethod
    def to_model(plan: Plan) -> tuple[PlanModel, list[PlanStepModel]]:
        plan_model = PlanModel(
            id=plan.plan_id,
            organization_id=plan.organization_id,
            agent_id=plan.agent_id,
            task_id=plan.task_id,
            status=plan.status.value,
            objective=plan.objective,
            current_step=plan.current_step,
            version=plan.version,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            completed_at=plan.completed_at,
            failure_reason=plan.failure_reason,
            correlation_id=plan.correlation_id,
        )
        step_models = [PlanStepMapper.to_model(s, plan.plan_id) for s in plan.steps]
        return plan_model, step_models
