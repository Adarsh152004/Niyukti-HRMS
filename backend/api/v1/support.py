"""
FastAPI Router - Support Contracts, Support Tickets.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db_session
import backend.hrms.infrastructure.database.models as models

router = APIRouter(prefix="/support", tags=["Support & SLA"])


@router.get("/tickets")
async def list_support_tickets(session: AsyncSession = Depends(get_db_session)) -> list[dict[str, Any]]:
    """List all support tickets."""
    result = await session.execute(select(models.SupportTicketModel))
    tickets = result.scalars().all()
    return [
        {
            "id": tkt.id,
            "ticket_number": tkt.ticket_number,
            "client_id": tkt.client_id,
            "project_id": tkt.project_id,
            "title": tkt.title,
            "description": tkt.description,
            "category": tkt.category,
            "priority": tkt.priority,
            "status": tkt.status,
            "estimated_hours": tkt.estimated_hours,
            "actual_hours": tkt.actual_hours,
        }
        for tkt in tickets
    ]
