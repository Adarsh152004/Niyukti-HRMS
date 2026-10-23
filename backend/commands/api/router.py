"""
API v1 — Command Execution & Approval Endpoints (`/api/v1/commands` & `/api/v1/approvals`).
"""

from __future__ import annotations

import contextlib
from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.api.response import error_response, success_response
from backend.commands.application.bus import CommandBus, CommandBusExecutionError
from backend.commands.application.handlers import (
    CreateDepartmentCommandHandler,
    CreateEmployeeCommandHandler,
    CreateSkillCommandHandler,
    GetEmployeeCommandHandler,
    ListEmployeesCommandHandler,
    TerminateEmployeeCommandHandler,
    UpdateEmployeeCommandHandler,
)
from backend.commands.domain.enums import CommandChannel, CommandStatus, RiskLevel
from backend.commands.domain.models import Command, CommandMetadata
from backend.hrms.domain.actor import Actor
from backend.security.api.dependencies import get_current_actor

# Create routers
router = APIRouter(prefix="/api/v1/commands", tags=["Commands & Execution"])
approvals_router = APIRouter(prefix="/api/v1/approvals", tags=["HITL Approvals"])

# Singletons
_command_bus_instance: CommandBus | None = None


def get_command_bus() -> CommandBus:
    global _command_bus_instance
    if _command_bus_instance is None:
        _command_bus_instance = CommandBus()
        _init_command_registry()
    return _command_bus_instance


# Register reference command handlers on startup
def _init_command_registry() -> None:
    bus = get_command_bus()

    # Employee Read
    bus.registry.register(
        "employee.read",
        GetEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.read",
            description="Get employee details",
            required_permissions=["EMPLOYEE_READ"],
            risk_level=RiskLevel.LOW,
        ),
    )

    # Employee List
    bus.registry.register(
        "employee.list",
        ListEmployeesCommandHandler(),
        CommandMetadata(
            command_type="employee.list",
            description="List employees",
            required_permissions=["EMPLOYEE_READ"],
            risk_level=RiskLevel.LOW,
        ),
    )

    # Employee Create
    bus.registry.register(
        "employee.create",
        CreateEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.create",
            description="Create a new employee record",
            required_permissions=["EMPLOYEE_CREATE"],
            risk_level=RiskLevel.MEDIUM,
        ),
    )

    # Employee Update
    bus.registry.register(
        "employee.update",
        UpdateEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.update",
            description="Update an existing employee record",
            required_permissions=["EMPLOYEE_UPDATE"],
            risk_level=RiskLevel.MEDIUM,
        ),
    )

    # Employee Terminate
    bus.registry.register(
        "employee.terminate",
        TerminateEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.terminate",
            description="Terminate an employee employment status",
            required_permissions=["EMPLOYEE_DELETE"],
            risk_level=RiskLevel.HIGH,
            requires_approval=True,
        ),
    )

    # Department Create
    bus.registry.register(
        "department.create",
        CreateDepartmentCommandHandler(),
        CommandMetadata(
            command_type="department.create",
            description="Create a new department",
            required_permissions=["DEPARTMENT_CREATE"],
            risk_level=RiskLevel.MEDIUM,
        ),
    )

    # Skill Create
    bus.registry.register(
        "skill.create",
        CreateSkillCommandHandler(),
        CommandMetadata(
            command_type="skill.create",
            description="Create a new skill definition",
            required_permissions=["EMPLOYEE_MANAGE_SKILLS"],
            risk_level=RiskLevel.LOW,
        ),
    )


# Initialize default registry handlers
with contextlib.suppress(Exception):
    _init_command_registry()


class SubmitCommandRequest(BaseModel):
    command_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = Field(default=None)
    channel: CommandChannel = Field(default=CommandChannel.WEB)


class ApproveRejectRequest(BaseModel):
    reason: str | None = Field(default=None)


@router.post("", summary="Submit and Dispatch Command")
async def submit_command(
    req: SubmitCommandRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
    bus: Annotated[CommandBus, Depends(get_command_bus)],
) -> JSONResponse:
    """
    Submit command for execution through full validation, authorization, policy, risk, and HITL gate pipeline.
    """
    cmd = Command(
        command_type=req.command_type,
        actor_id=actor.actor_id,  # Populated strictly from authenticated security context!
        organization_id=actor.organization_id,  # Populated strictly from authenticated security context!
        channel=req.channel,
        payload=req.payload,
        idempotency_key=req.idempotency_key,
    )
    context = bus.build_context(actor=actor, channel=req.channel)

    try:
        res = await bus.dispatch(cmd, context)
        return success_response(
            data={
                "command_id": res.command_id,
                "status": res.status.value,
                "result_data": res.result_data,
                "execution_time_ms": res.execution_time_ms,
                "events_produced": res.events_produced,
            },
            status_code=status.HTTP_200_OK if res.status == CommandStatus.SUCCEEDED else status.HTTP_202_ACCEPTED,
        )
    except CommandBusExecutionError as e:
        return error_response(code=e.status.value, message=e.message, status_code=400)
    except Exception as e:
        return error_response(code="COMMAND_FAILED", message=str(e), status_code=400)


@router.get("/discovery", summary="Inspect Available Commands (AI Tool Registry)")
async def discover_commands(
    actor: Annotated[Actor, Depends(get_current_actor)],
    bus: Annotated[CommandBus, Depends(get_command_bus)],
) -> JSONResponse:
    cmds = bus.registry.list_commands()
    return success_response(data={"commands": [c.model_dump() for c in cmds]})


@router.get("/{command_id}", summary="Inspect Command Details")
async def get_command_details(
    command_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
    bus: Annotated[CommandBus, Depends(get_command_bus)],
) -> JSONResponse:
    cmd = bus._history.get(command_id)
    if not cmd or cmd.organization_id != actor.organization_id:
        return error_response(code="COMMAND_NOT_FOUND", message="Command not found.", status_code=404)
    return success_response(data=cmd.model_dump())


@router.get("/{command_id}/status", summary="Get Command Status")
async def get_command_status(
    command_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
    bus: Annotated[CommandBus, Depends(get_command_bus)],
) -> JSONResponse:
    cmd = bus._history.get(command_id)
    if not cmd or cmd.organization_id != actor.organization_id:
        return error_response(code="COMMAND_NOT_FOUND", message="Command not found.", status_code=404)
    return success_response(data={"command_id": cmd.command_id, "status": cmd.status.value})


@router.post("/{command_id}/cancel", summary="Cancel Waiting Command")
async def cancel_command(
    command_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
    bus: Annotated[CommandBus, Depends(get_command_bus)],
) -> JSONResponse:
    cmd = bus._history.get(command_id)
    if not cmd or cmd.organization_id != actor.organization_id:
        return error_response(code="COMMAND_NOT_FOUND", message="Command not found.", status_code=404)
    try:
        cmd.transition_to(CommandStatus.CANCELLED)
        return success_response(data={"command_id": cmd.command_id, "status": cmd.status.value})
    except ValueError as e:
        return error_response(code="INVALID_TRANSITION", message=str(e), status_code=400)


# Approvals Endpoints
@approvals_router.get("", summary="List Pending Approval Requests")
async def list_approvals(
    actor: Annotated[Actor, Depends(get_current_actor)],
    bus: Annotated[CommandBus, Depends(get_command_bus)],
) -> JSONResponse:
    reqs = bus.approval_service.list_pending_for_organization(actor.organization_id)
    return success_response(data={"approval_requests": [r.model_dump() for r in reqs]})


@approvals_router.get("/{request_id}", summary="Get Approval Request Details")
async def get_approval(
    request_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
    bus: Annotated[CommandBus, Depends(get_command_bus)],
) -> JSONResponse:
    req = bus.approval_service.get_request(request_id)
    if not req or req.organization_id != actor.organization_id:
        return error_response(code="APPROVAL_NOT_FOUND", message="Approval request not found.", status_code=404)
    return success_response(data=req.model_dump())


@approvals_router.post("/{request_id}/approve", summary="Approve HITL Request")
async def approve_request(
    request_id: str,
    req_body: ApproveRejectRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
    bus: Annotated[CommandBus, Depends(get_command_bus)],
) -> JSONResponse:
    try:
        appr_req = bus.approval_service.get_request(request_id)
        if not appr_req:
            return error_response(code="APPROVAL_NOT_FOUND", message="Approval request not found.", status_code=404)

        cmd_id = appr_req.target_resource_id
        cmd = bus._history.get(cmd_id)
        payload_hash = cmd.payload_hash if cmd else None

        approved_req = bus.approval_service.approve(
            request_id=request_id,
            approver_actor=actor,
            current_command_payload_hash=payload_hash,
            reason=req_body.reason,
        )

        # Resume and execute command!
        if cmd:
            cmd.status = CommandStatus.APPROVED
            context = bus.build_context(actor=actor)
            exec_res = await bus.dispatch(cmd, context)
            return success_response(
                data={
                    "approval_status": approved_req.status.value,
                    "command_result": exec_res.model_dump(),
                }
            )

        return success_response(data={"approval_status": approved_req.status.value})
    except Exception as e:
        return error_response(code="APPROVAL_FAILED", message=str(e), status_code=400)


@approvals_router.post("/{request_id}/reject", summary="Reject HITL Request")
async def reject_request(
    request_id: str,
    req_body: ApproveRejectRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
    bus: Annotated[CommandBus, Depends(get_command_bus)],
) -> JSONResponse:
    try:
        rejected_req = bus.approval_service.reject(
            request_id=request_id,
            approver_actor=actor,
            reason=req_body.reason,
        )
        return success_response(data={"approval_status": rejected_req.status.value})
    except Exception as e:
        return error_response(code="REJECTION_FAILED", message=str(e), status_code=400)
