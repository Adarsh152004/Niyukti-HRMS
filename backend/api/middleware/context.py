"""
AI-Powered Intelligent HRMS — Request Context & Multi-Tenancy Middleware.

Provides threadsafe / async context variable propagation for:
- Correlation ID (tracing and log aggregation)
- Tenant Context (multi-tenant isolation, tenant_id)
- Principal Context (actor, user_id, roles, scopes, risk_tier)
"""

from __future__ import annotations

import contextvars
import uuid
from dataclasses import dataclass, field
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Context Variables
correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id_ctx", default="corr-init"
)
tenant_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "tenant_id_ctx", default="tenant-default"
)
user_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "user_id_ctx", default=None
)
user_roles_ctx: contextvars.ContextVar[list[str]] = contextvars.ContextVar(
    "user_roles_ctx", default=[]
)


@dataclass(frozen=True)
class RequestContext:
    """Immutable snapshot of request context metadata."""

    correlation_id: str
    tenant_id: str
    user_id: str | None = None
    roles: list[str] = field(default_factory=list)
    client_ip: str = "127.0.0.1"


def get_correlation_id() -> str:
    """Retrieve current request correlation ID."""
    return correlation_id_ctx.get()


def get_current_tenant_id() -> str:
    """Retrieve current request tenant ID."""
    return tenant_id_ctx.get()


def get_current_user_id() -> str | None:
    """Retrieve current request user ID if authenticated."""
    return user_id_ctx.get()


def get_current_roles() -> list[str]:
    """Retrieve current request roles list."""
    return user_roles_ctx.get()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that captures or generates:
    - X-Correlation-ID header
    - X-Tenant-ID header
    - Populates async contextvars for downstream services & logging
    - Echoes correlation ID in response headers
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Extract or generate correlation ID
        correlation_id = (
            request.headers.get("X-Correlation-ID")
            or request.headers.get("X-Request-ID")
            or f"corr-{uuid.uuid4().hex[:12]}"
        )
        corr_token = correlation_id_ctx.set(correlation_id)

        # Extract or default tenant ID
        tenant_id = (
            request.headers.get("X-Tenant-ID")
            or request.query_params.get("tenant_id")
            or "tenant-default"
        )
        tenant_token = tenant_id_ctx.set(tenant_id)

        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Tenant-ID"] = tenant_id
            return response
        finally:
            correlation_id_ctx.reset(corr_token)
            tenant_id_ctx.reset(tenant_token)
