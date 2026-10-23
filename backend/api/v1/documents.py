"""
API v1 — Employee Document Endpoints (`/api/v1/documents`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_document_service, get_tenant_context
from backend.api.response import error_response, success_response
from backend.hrms.application.services import EmployeeDocumentService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.documents import DocumentType
from backend.hrms.domain.exceptions import HRMSException

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


class UploadDocumentMetadataRequest(BaseModel):
    employee_id: str
    document_type: DocumentType
    document_name: str
    storage_reference: str
    mime_type: str = "application/pdf"
    size: int = 0
    checksum: str | None = None


@router.post("", summary="Register Document Metadata")
async def upload_document_metadata(
    req: UploadDocumentMetadataRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[EmployeeDocumentService, Depends(get_document_service)],
) -> JSONResponse:
    try:
        doc = await service.upload_document_metadata(
            ctx=ctx,
            employee_id=req.employee_id,
            document_type=req.document_type,
            document_name=req.document_name,
            storage_reference=req.storage_reference,
            mime_type=req.mime_type,
            size=req.size,
            checksum=req.checksum,
        )
        return success_response(data=doc.model_dump(), status_code=status.HTTP_201_CREATED)
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=400)


@router.post("/{document_id}/verify", summary="Verify Employee Document")
async def verify_document(
    document_id: str,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[EmployeeDocumentService, Depends(get_document_service)],
) -> JSONResponse:
    try:
        doc = await service.verify_document(ctx, document_id)
        return success_response(data=doc.model_dump())
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=400)
