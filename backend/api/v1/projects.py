"""
FastAPI Router - Projects, Milestones, Tasks.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db_session
import backend.hrms.infrastructure.database.models as models

router = APIRouter(prefix="/projects", tags=["Projects & Dev Management"])


@router.get("/")
async def list_projects(session: AsyncSession = Depends(get_db_session)) -> list[dict[str, Any]]:
    """List all software development projects."""
    result = await session.execute(select(models.ProjectModel))
    projects = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "client_id": p.client_id,
            "project_type": p.project_type,
            "status": p.status,
            "priority": p.priority,
            "start_date": str(p.start_date),
            "estimated_end_date": str(p.estimated_end_date),
            "budget_amount": p.budget_amount,
            "technology_stack": p.technology_stack_json,
            "repository_url": p.repository_url,
        }
        for p in projects
    ]


@router.get("/{project_id}/tasks")
async def get_project_tasks(project_id: str, session: AsyncSession = Depends(get_db_session)) -> list[dict[str, Any]]:
    """Get tasks for a specific project."""
    result = await session.execute(
        select(models.TaskModel).where(models.TaskModel.project_id == project_id)
    )
    tasks = result.scalars().all()
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "task_type": t.task_type,
            "status": t.status,
            "priority": t.priority,
            "estimated_hours": t.estimated_hours,
            "actual_hours": t.actual_hours,
            "due_date": str(t.due_date) if t.due_date else None,
        }
        for t in tasks
    ]
