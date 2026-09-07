"""
FastAPI Router - Automated Enterprise Workflow DAG Engine.
Standing workflows list starts EMPTY.
All DAGs are dynamically created by:
  - The orchestration engine (when a long-running query is detected)
  - The user clicking "Trigger Workflow" in the UI
"""

from __future__ import annotations
import uuid
import datetime
from typing import Any, List, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/enterprise-workflows", tags=["Automated Enterprise Workflows"])


class TriggerWorkflowRequest(BaseModel):
    name: str = Field(..., example="New Hire Onboarding - Priya Sharma")
    category: str = Field(default="Workforce", example="Workforce / Payroll / Talent")
    target_id: str | None = Field(default=None)


# Empty by default - populated by real orchestration triggers or manual UI triggers
ENTERPRISE_WORKFLOWS: List[Dict[str, Any]] = []


@router.get("")
@router.get("/")
async def list_enterprise_workflows() -> List[Dict[str, Any]]:
    """Return all currently running/pending/completed standing enterprise DAGs."""
    return ENTERPRISE_WORKFLOWS


@router.post("/trigger")
async def trigger_new_enterprise_workflow(req: TriggerWorkflowRequest) -> Dict[str, Any]:
    """Manually trigger a new enterprise background DAG workflow from the UI."""
    wf_id = f"dag-{uuid.uuid4().hex[:6]}"
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    new_dag = {
        "id": wf_id,
        "name": req.name,
        "category": req.category,
        "status": "running",
        "currentStep": "Initial Context & Authorization Verification",
        "progress": 10,
        "startedAt": now,
        "steps": [
            {"id": "s-1", "label": "Initial Context & Authorization Verification", "agent": "Workflow Orchestration Agent", "status": "running", "duration": "In progress"},
            {"id": "s-2", "label": "Resource & Database Allocation", "agent": "Infrastructure Agent", "status": "pending"},
            {"id": "s-3", "label": "Executive Approval Checkpoint", "agent": "Human-in-the-Loop", "status": "pending"},
            {"id": "s-4", "label": "Automated Execution & Verification", "agent": "Compliance Agent", "status": "pending"},
            {"id": "s-5", "label": "Completion & Audit Encryption", "agent": "Audit Logger", "status": "pending"},
        ],
    }
    ENTERPRISE_WORKFLOWS.insert(0, new_dag)
    return new_dag


@router.post("/{workflow_id}/approve")
async def approve_hitl_step(workflow_id: str) -> Dict[str, Any]:
    """Approve a Human-in-the-Loop gate and advance the workflow to the next step."""
    for wf in ENTERPRISE_WORKFLOWS:
        if wf["id"] == workflow_id:
            wf["progress"] = min(100, wf["progress"] + 25)
            for i, st in enumerate(wf["steps"]):
                if st["status"] == "running":
                    st["status"] = "completed"
                    st["duration"] = "Approved"
                    if i + 1 < len(wf["steps"]):
                        wf["steps"][i + 1]["status"] = "running"
                        wf["steps"][i + 1]["duration"] = "In progress"
                        wf["currentStep"] = wf["steps"][i + 1]["label"]
                    else:
                        wf["status"] = "completed"
                        wf["currentStep"] = "Workflow Completed Successfully"
                        wf["progress"] = 100
                    break
            return wf
    raise HTTPException(status_code=404, detail="Workflow not found")


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str) -> Dict[str, str]:
    """Remove a workflow DAG entry."""
    global ENTERPRISE_WORKFLOWS
    before = len(ENTERPRISE_WORKFLOWS)
    ENTERPRISE_WORKFLOWS = [w for w in ENTERPRISE_WORKFLOWS if w["id"] != workflow_id]
    if len(ENTERPRISE_WORKFLOWS) == before:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"status": "deleted", "id": workflow_id}
