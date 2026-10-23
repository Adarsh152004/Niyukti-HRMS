"""
FastAPI Router - Clients, Leads, Proposals, Contracts.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db_session
import backend.hrms.infrastructure.database.models as models

router = APIRouter(prefix="/clients", tags=["Clients & CRM"])


@router.get("/")
async def list_clients(session: AsyncSession = Depends(get_db_session)) -> list[dict[str, Any]]:
    """List all client organizations."""
    result = await session.execute(select(models.ClientModel))
    clients = result.scalars().all()
    return [
        {
            "id": c.id,
            "company_name": c.company_name,
            "legal_name": c.legal_name,
            "industry": c.industry,
            "website": c.website,
            "gst_number": c.gst_number,
            "status": c.status,
            "source": c.source,
            "notes": c.notes,
        }
        for c in clients
    ]


@router.get("/{client_id}/contacts")
async def get_client_contacts(client_id: str, session: AsyncSession = Depends(get_db_session)) -> list[dict[str, Any]]:
    """Get contacts for a specific client."""
    result = await session.execute(
        select(models.ClientContactModel).where(models.ClientContactModel.client_id == client_id)
    )
    contacts = result.scalars().all()
    return [
        {
            "id": cc.id,
            "first_name": cc.first_name,
            "last_name": cc.last_name,
            "email": cc.email,
            "phone": cc.phone,
            "designation": cc.designation,
            "is_primary": cc.is_primary,
            "is_billing_contact": cc.is_billing_contact,
        }
        for cc in contacts
    ]
