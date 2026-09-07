"""
API Response Standard — Standardized API response format for all HRMS endpoints.

Enforces consistent response envelope structure for success and error cases.
Never exposes sensitive internal stack traces or internal implementation details.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class APIErrorDetail(BaseModel):
    code: str
    message: str


class APIResponse(BaseModel):
    """Standard API envelope."""

    success: bool
    data: Any | None = Field(default=None)
    error: APIErrorDetail | None = Field(default=None)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(tz=UTC).isoformat())


def success_response(data: Any, status_code: int = 200, request_id: str | None = None) -> JSONResponse:
    req_id = request_id or str(uuid.uuid4())
    encoded_data = jsonable_encoder(data)
    body = APIResponse(
        success=True,
        data=encoded_data,
        request_id=req_id,
    ).model_dump()
    return JSONResponse(content=body, status_code=status_code)


def error_response(code: str, message: str, status_code: int = 400, request_id: str | None = None) -> JSONResponse:
    req_id = request_id or str(uuid.uuid4())
    body = APIResponse(
        success=False,
        error=APIErrorDetail(code=code, message=message),
        request_id=req_id,
    ).model_dump()
    return JSONResponse(content=body, status_code=status_code)
