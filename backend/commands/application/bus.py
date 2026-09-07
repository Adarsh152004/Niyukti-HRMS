"""
CommandBus — Universal Orchestrator for Command Execution, Policy, Authorization, Risk, HITL, and Events.

Enforces:
Command → Validation → Policy Evaluation → Authorization → Risk Classification → HITL/Approval Gate → Action Execution → Transaction → Outbox → Audit → Result
"""

from __future__ import annotations

import time

from backend.commands.application.action_executor import ActionExecutor
from backend.commands.application.approval_service import ApprovalService
from backend.commands.application.idempotency import IdempotencyEngine, IdempotencyMismatchError
from backend.commands.application.policy_engine import PolicyEngine
from backend.commands.application.registry import CommandRegistry
from backend.commands.application.risk_engine import RiskEngine
from backend.commands.domain.enums import CommandChannel, CommandStatus, PolicyDecision, RiskLevel
from backend.commands.domain.models import Command, CommandContext, CommandResult
from backend.hrms.application.authorization import AuthorizationService
from backend.hrms.domain.actor import Actor
from backend.runtime.events import Event, EventBus


class CommandBusExecutionError(Exception):
    """Raised when command bus execution encounters an error or authorization/policy denial."""

    def __init__(self, command_id: str, status: CommandStatus, message: str) -> None:
        self.command_id = command_id
        self.status = status
        self.message = message
        super().__init__(message)


class CommandBus:
    """
    Universal CommandBus orchestrator.
    """

    def __init__(
        self,
        registry: CommandRegistry | None = None,
        policy_engine: PolicyEngine | None = None,
        risk_engine: RiskEngine | None = None,
        authorization_service: AuthorizationService | None = None,
        approval_service: ApprovalService | None = None,
        idempotency_engine: IdempotencyEngine | None = None,
        action_executor: ActionExecutor | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.registry = registry or CommandRegistry()
        self.policy_engine = policy_engine or PolicyEngine()
        self.risk_engine = risk_engine or RiskEngine()
        self.authorization_service = authorization_service or AuthorizationService()
        self.approval_service = approval_service or ApprovalService()
        self.idempotency_engine = idempotency_engine or IdempotencyEngine()
        self.action_executor = action_executor or ActionExecutor()
        self.event_bus = event_bus or EventBus.get_instance()

        # In-memory execution store
        self._history: dict[str, Command] = {}

    def build_context(self, actor: Actor, channel: CommandChannel = CommandChannel.WEB) -> CommandContext:
        """
        Build a trusted CommandContext strictly from authenticated Actor and security token claims.
        """
        return CommandContext(
            actor=actor,
            organization_id=actor.organization_id,
            tenant_id=actor.organization_id,
            channel=channel,
            permissions=actor.permissions,
            capabilities=set(actor.metadata.get("capabilities", [])),
        )

    async def dispatch(self, command: Command, context: CommandContext) -> CommandResult:
        """
        Orchestrate complete universal command execution pipeline.
        """
        start_time = time.time()
        self._history[command.command_id] = command

        # 1. State Transition: RECEIVED -> VALIDATING
        if command.status != CommandStatus.APPROVED:
            command.transition_to(CommandStatus.VALIDATING)

        # 2. Idempotency Deduplication Check
        if command.idempotency_key:
            existing_rec = self.idempotency_engine.get_record(context.organization_id, command.idempotency_key)
            if existing_rec:
                if existing_rec.payload_hash != command.payload_hash:
                    command.transition_to(CommandStatus.FAILED)
                    raise IdempotencyMismatchError(
                        f"Idempotency key '{command.idempotency_key}' reused with different payload hash."
                    )
                # Return previously cached result!
                return CommandResult(
                    command_id=command.command_id,
                    status=existing_rec.status,
                    result_data=existing_rec.result_data,
                    execution_time_ms=(time.time() - start_time) * 1000,
                )

        # 3. Resolve Handler & Metadata
        handler = self.registry.get_handler(command.command_type)
        metadata = self.registry.get_metadata(command.command_type)

        if command.status != CommandStatus.APPROVED:
            # 4. State Transition: VALIDATING -> AUTHORIZED
            # Verify Authorization
            required_perm = metadata.required_permissions[0] if metadata.required_permissions else command.command_type
            if not self.authorization_service.can(context.actor, required_perm, context.organization_id):
                command.transition_to(CommandStatus.DENIED)
                raise CommandBusExecutionError(
                    command_id=command.command_id,
                    status=CommandStatus.DENIED,
                    message=f"Actor '{context.actor.actor_id}' is unauthorized for command '{command.command_type}'.",
                )
            command.transition_to(CommandStatus.AUTHORIZED)

            # 5. Assess Risk
            risk_assessment = self.risk_engine.assess_risk(command)
            if metadata.risk_level > risk_assessment.risk_level:
                risk_assessment.risk_level = metadata.risk_level

            # 6. Policy Engine Evaluation
            policy_res = self.policy_engine.evaluate(command, context, risk_assessment.risk_level)
            if policy_res.decision == PolicyDecision.DENY:
                command.transition_to(CommandStatus.DENIED)
                raise CommandBusExecutionError(
                    command_id=command.command_id,
                    status=CommandStatus.DENIED,
                    message=f"Policy denied execution: {policy_res.reason}",
                )

            command.transition_to(CommandStatus.POLICY_CHECKED)

        # 7. HITL / Approval Gate Check
        requires_approval = (
            metadata.requires_approval
            or policy_res.decision == PolicyDecision.REQUIRE_APPROVAL
            or risk_assessment.risk_level >= RiskLevel.HIGH
        )

        if requires_approval and command.status != CommandStatus.APPROVED:
            command.transition_to(CommandStatus.WAITING_APPROVAL)
            appr_req = self.approval_service.create_approval_request(
                command=command,
                context=context,
                required_permission=required_perm,
            )
            # Stage CommandApprovalRequested Event
            evt = Event(
                event_type="hrms.command.approval_requested",
                source=context.actor.actor_id,
                payload={
                    "command_id": command.command_id,
                    "organization_id": context.organization_id,
                    "approval_request_id": appr_req.request_id,
                    "risk_level": risk_assessment.risk_level.value,
                },
                correlation_id=command.correlation_id,
            )
            await self.event_bus.publish(evt)
            return CommandResult(
                command_id=command.command_id,
                status=CommandStatus.WAITING_APPROVAL,
                result_data={
                    "approval_request_id": appr_req.request_id,
                    "risk_level": risk_assessment.risk_level.value,
                    "message": "Command requires Human-In-The-Loop approval.",
                },
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        # 8. State Transition: POLICY_CHECKED/APPROVED -> EXECUTING
        if command.status == CommandStatus.WAITING_APPROVAL:
            command.transition_to(CommandStatus.APPROVED)
        command.transition_to(CommandStatus.EXECUTING)

        # 9. Execute Action via ActionExecutor
        try:
            _action, result_data = await self.action_executor.execute_action(command, handler, context)
            command.transition_to(CommandStatus.SUCCEEDED)
        except Exception as e:
            command.transition_to(CommandStatus.FAILED)
            raise CommandBusExecutionError(
                command_id=command.command_id,
                status=CommandStatus.FAILED,
                message=f"Command execution failed: {e}",
            ) from e

        # 10. Record Idempotency if key provided
        if command.idempotency_key:
            self.idempotency_engine.record_execution(
                organization_id=context.organization_id,
                idempotency_key=command.idempotency_key,
                command_id=command.command_id,
                payload_hash=command.payload_hash,
                status=CommandStatus.SUCCEEDED,
                result_data=result_data,
            )

        # 11. Publish CommandSucceeded Event
        exec_evt = Event(
            event_type="hrms.command.succeeded",
            source=context.actor.actor_id,
            payload={
                "command_id": command.command_id,
                "command_type": command.command_type,
                "organization_id": context.organization_id,
            },
            correlation_id=command.correlation_id,
        )
        await self.event_bus.publish(exec_evt)

        elapsed_ms = (time.time() - start_time) * 1000
        return CommandResult(
            command_id=command.command_id,
            status=CommandStatus.SUCCEEDED,
            result_data=result_data,
            execution_time_ms=elapsed_ms,
            events_produced=["CommandSucceeded"],
        )
