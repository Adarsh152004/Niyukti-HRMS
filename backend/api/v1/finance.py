"""
FastAPI Router - Invoices, Payments, Expenses.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db_session
import backend.hrms.infrastructure.database.models as models

router = APIRouter(prefix="/finance", tags=["Finance & Billing"])


@router.get("/invoices")
async def list_invoices(session: AsyncSession = Depends(get_db_session)) -> list[dict[str, Any]]:
    """List all client invoices."""
    result = await session.execute(select(models.InvoiceModel))
    invoices = result.scalars().all()
    return [
        {
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "client_id": inv.client_id,
            "project_id": inv.project_id,
            "issue_date": str(inv.issue_date),
            "due_date": str(inv.due_date),
            "subtotal": inv.subtotal,
            "tax_amount": inv.tax_amount,
            "total_amount": inv.total_amount,
            "currency": inv.currency,
            "status": inv.status,
        }
        for inv in invoices
    ]
