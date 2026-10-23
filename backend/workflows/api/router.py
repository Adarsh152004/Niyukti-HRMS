"""
API v1 — Workflow Engine & Job Execution Endpoints (`/api/v1/workflows`, `/api/v1/workflow-executions`, `/api/v1/jobs`, `/api/v1/dead-letter`).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.api.response import error_response, success_response
from backend.commands.api.router import get_command_bus
from backend.hrms.domain.actor import Actor
from backend.security.api.dependencies import get_current_actor
from backend.workflows.application.cancellation_service import CancellationService
from backend.workflows.application.step_executor import StepExecutor
from backend.workflows.application.workflow_engine import WorkflowEngine
from backend.workflows.application.workflow_service import WorkflowService
from backend.workflows.domain.models import WorkflowExecution, WorkflowStepDefinition
from backend.workflows.infrastructure.database.repositories import (
    InMemoryDeadLetterJobRepository,
    InMemoryScheduledJobRepository,
    InMemoryStepExecutionRepository,
    InMemoryWorkflowDefinitionRepository,
    InMemoryWorkflowExecutionRepository,
)

# Routers
workflows_router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])
executions_router = APIRouter(prefix="/api/v1/workflow-executions", tags=["Workflow Executions"])
jobs_router = APIRouter(prefix="/api/v1/jobs", tags=["Scheduled Jobs"])
dlq_router = APIRouter(prefix="/api/v1/dead-letter", tags=["Dead Letter Queue"])

# Repositories & Services singletons for API layer
_wf_def_repo = InMemoryWorkflowDefinitionRepository()
_wf_exec_repo = InMemoryWorkflowExecutionRepository()
_step_exec_repo = InMemoryStepExecutionRepository()
_job_repo = InMemoryScheduledJobRepository()
_dlq_repo = InMemoryDeadLetterJobRepository()

_step_executor = StepExecutor(command_bus=get_command_bus())
_workflow_engine = WorkflowEngine(
    step_executor=_step_executor,
    wf_def_repo=_wf_def_repo,
    wf_exec_repo=_wf_exec_repo,
    step_exec_repo=_step_exec_repo,
    dlq_repo=_dlq_repo,
)
_workflow_service = WorkflowService(repository=_wf_def_repo)
_cancellation_service = CancellationService(wf_exec_repo=_wf_exec_repo)


class CreateWorkflowRequest(BaseModel):
    name: str
    description: str = ""
    steps: list[dict[str, Any]] = Field(default_factory=list)
    trigger_type: str = "MANUAL"
    trigger_config: dict[str, Any] = Field(default_factory=dict)


class StartExecutionRequest(BaseModel):
    workflow_id: str
    input_payload: dict[str, Any] = Field(default_factory=dict)


@workflows_router.post("", summary="Create Workflow Definition")
async def create_workflow(
    req: CreateWorkflowRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        step_defs = [WorkflowStepDefinition(**s) for s in req.steps]
        wf_def = await _workflow_service.create_workflow_definition(
            organization_id=actor.organization_id,
            name=req.name,
            description=req.description,
            steps=step_defs,
            trigger_type=req.trigger_type,
            trigger_config=req.trigger_config,
        )
        return success_response(data=wf_def.model_dump(), status_code=status.HTTP_201_CREATED)
    except Exception as e:
        return error_response(code="WORKFLOW_CREATE_FAILED", message=str(e), status_code=400)


@workflows_router.get("", summary="List Workflow Definitions")
async def list_workflows(
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    defs = await _workflow_service.list_workflows(actor.organization_id)
    return success_response(data={"workflows": [d.model_dump() for d in defs]})


@workflows_router.get("/{workflow_id}", summary="Get Workflow Definition Details")
async def get_workflow(
    workflow_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    wf = await _workflow_service.get_workflow_definition(actor.organization_id, workflow_id)
    if not wf:
        return error_response(code="WORKFLOW_NOT_FOUND", message="Workflow definition not found.", status_code=404)
    return success_response(data=wf.model_dump())


@workflows_router.post("/{workflow_id}/enable", summary="Enable Workflow Definition")
async def enable_workflow(
    workflow_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        wf = await _workflow_service.enable_workflow(actor.organization_id, workflow_id)
        return success_response(data=wf.model_dump())
    except Exception as e:
        return error_response(code="ENABLE_FAILED", message=str(e), status_code=400)


@workflows_router.post("/{workflow_id}/disable", summary="Disable Workflow Definition")
async def disable_workflow(
    workflow_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        wf = await _workflow_service.disable_workflow(actor.organization_id, workflow_id)
        return success_response(data=wf.model_dump())
    except Exception as e:
        return error_response(code="DISABLE_FAILED", message=str(e), status_code=400)


# Executions Endpoints
@executions_router.post("", summary="Start Workflow Execution")
async def start_execution(
    req: StartExecutionRequest,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        wf_def = await _workflow_service.get_workflow_definition(actor.organization_id, req.workflow_id)
        if not wf_def or not wf_def.enabled:
            return error_response(
                code="WORKFLOW_NOT_AVAILABLE",
                message="Workflow definition not found or disabled.",
                status_code=400,
            )

        execution = WorkflowExecution(
            workflow_id=wf_def.workflow_id,
            organization_id=actor.organization_id,
            input_payload=req.input_payload,
        )
        await _wf_exec_repo.save(execution)

        exec_result = await _workflow_engine.execute_workflow(
            workflow_def=wf_def,
            execution=execution,
            actor=actor,
        )
        return success_response(data=exec_result.model_dump(), status_code=status.HTTP_202_ACCEPTED)
    except Exception as e:
        return error_response(code="EXECUTION_FAILED", message=str(e), status_code=400)


@executions_router.get("/{execution_id}", summary="Get Workflow Execution Details")
async def get_execution(
    execution_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    exec_inst = await _wf_exec_repo.get_by_id(actor.organization_id, execution_id)
    if not exec_inst:
        return error_response(code="EXECUTION_NOT_FOUND", message="Workflow execution not found.", status_code=404)
    return success_response(data=exec_inst.model_dump())


@executions_router.post("/{execution_id}/pause", summary="Pause Workflow Execution")
async def pause_execution(
    execution_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        exec_inst = await _cancellation_service.pause_execution(actor.organization_id, execution_id)
        return success_response(data=exec_inst.model_dump())
    except Exception as e:
        return error_response(code="PAUSE_FAILED", message=str(e), status_code=400)


@executions_router.post("/{execution_id}/resume", summary="Resume Workflow Execution")
async def resume_execution(
    execution_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        exec_inst = await _cancellation_service.resume_execution(actor.organization_id, execution_id)
        return success_response(data=exec_inst.model_dump())
    except Exception as e:
        return error_response(code="RESUME_FAILED", message=str(e), status_code=400)


@executions_router.post("/{execution_id}/cancel", summary="Cancel Workflow Execution")
async def cancel_execution(
    execution_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    try:
        exec_inst = await _cancellation_service.cancel_execution(actor.organization_id, execution_id)
        return success_response(data=exec_inst.model_dump())
    except Exception as e:
        return error_response(code="CANCEL_FAILED", message=str(e), status_code=400)


# Dead Letter Queue Endpoints
@dlq_router.get("", summary="List Dead Letter Jobs")
async def list_dlq(
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    items = await _dlq_repo.list_by_organization(actor.organization_id)
    return success_response(data={"dead_letter_jobs": [i.model_dump() for i in items]})


@dlq_router.post("/{job_id}/discard", summary="Discard DLQ Item")
async def discard_dlq(
    job_id: str,
    actor: Annotated[Actor, Depends(get_current_actor)],
) -> JSONResponse:
    deleted = await _dlq_repo.delete(job_id)
    if not deleted:
        return error_response(code="DLQ_NOT_FOUND", message="DLQ item not found.", status_code=404)
    return success_response(data={"message": "DLQ item discarded."})
