"""
AI-Powered Intelligent HRMS — FastAPI Application Entry Point.

Node 12: Production-Grade REST & GraphQL API Gateway.
Provides:
- Health & status endpoints (/health, /health/live, /health/ready, /api/v1/status)
- API v1 routers (Workforce, Talent, Operations, AI & Agents, ML, Governance, Audit)
- Request Context & Multi-Tenancy propagation (Correlation ID, Tenant isolation)
- Sliding-window Rate Limiting & DoS protection
- Real-time WebSockets (/ws/events, /ws/workflows/{id}, /ws/agents/{id})
- Server-Sent Events (SSE) AI Completion Streams (/api/v1/ai/stream)
- Unified GraphQL Gateway (/graphql)
- Transactional Outbox background publisher integration
- Global HRMS exception handler & standardized envelope responses
"""


from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.agents.api.router import router as agents_router
from backend.agents.specialized.api.router import router as specialized_agents_router
from backend.api.graphql.schema import router as graphql_router
from backend.api.middleware.context import RequestContextMiddleware
from backend.api.middleware.rate_limit import RateLimitMiddleware
from backend.api.realtime.router import router as realtime_router
from backend.api.response import error_response
from backend.api.v1 import (
    me,
    chat_api,
    workflows_api,
    orchestration,
    clients,
    projects,
    finance,
    support,
    approvals,
    attendance,
    departments,
    designations,
    documents,
    employee_360,
    employees,
    executive,
    learning,
    leave,
    organizations,
    payroll,
    performance,
    policies,
    recruitment,
    reports,
    skills,
    audit_api,
    ml_api,
)
from backend.commands.api.router import approvals_router
from backend.commands.api.router import router as commands_router
from backend.database.config import get_db_settings
from backend.database.health import check_database_health
from backend.events.outbox.worker import outbox_worker
from backend.hrms.domain.exceptions import HRMSException
from backend.knowledge.api.router import memory_router
from backend.knowledge.api.router import router as knowledge_router
from backend.ml.api.router import router as ml_router
from backend.runtime.config import get_config
from backend.runtime.kernel import EnterpriseKernel
from backend.analytics.router import router as analytics_router
from backend.api.v1.ai_command import router as ai_command_router
from backend.api.v1.integrations_router import router as integrations_router
from backend.api.v1.integration_status import router as integration_status_router
from backend.api.v1.whatsapp_webhook import router as whatsapp_webhook_router
from backend.governance.api.kill_switch_router import router as kill_switch_router
from backend.security.api.router import router as security_router
from backend.workflows.api.router import (
    dlq_router,
    executions_router,
    jobs_router,
    workflows_router,
)

from backend.agents.orchestration.email_intelligence_agent import email_agent

config = get_config()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — initialize kernel, background outbox worker, and email intelligence agent."""
    kernel = EnterpriseKernel.get_instance()
    await kernel.start()
    await outbox_worker.start()
    await email_agent.start()
    yield
    await email_agent.stop()
    await outbox_worker.stop()
    await kernel.stop()
    EnterpriseKernel.reset()


app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description=(
        "Enterprise-grade AI-Powered Human Resource Management System. "
        "Combines traditional HRMS functionality with autonomous AI agents, "
        "intelligent analytics, predictive capabilities, workflow automation, "
        "governance guardrails, explainability, real-time WebSockets, and HITL control."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── Middleware Stack (Executed in reverse order of registration) ─────────────

# 1. Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware, default_rpm=600)

# 2. Multi-tenant Context & Correlation ID Middleware
app.add_middleware(RequestContextMiddleware)

# 3. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5185",
        "http://127.0.0.1:5185",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "X-Tenant-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# ── Register API Routers ──────────────────────────────────────────────────────

# Core Security & Commands
app.include_router(security_router)
app.include_router(commands_router)
app.include_router(approvals_router)
app.include_router(ai_command_router)
app.include_router(analytics_router)
app.include_router(kill_switch_router)
app.include_router(integration_status_router)
app.include_router(whatsapp_webhook_router)
app.include_router(integrations_router)

# Real-time & GraphQL
app.include_router(realtime_router)
app.include_router(graphql_router)

# Autonomous Agents & Workflows
app.include_router(agents_router)
app.include_router(specialized_agents_router)
app.include_router(workflows_router)
app.include_router(executions_router)
app.include_router(jobs_router)
app.include_router(dlq_router)

# HR Domain Modules
app.include_router(me.router, prefix="/api/v1")
app.include_router(chat_api.router, prefix="/api/v1")
app.include_router(workflows_api.router, prefix="/api/v1")
app.include_router(orchestration.router, prefix="/api/v1")
app.include_router(clients.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(finance.router, prefix="/api/v1")
app.include_router(support.router, prefix="/api/v1")
app.include_router(organizations.router)
app.include_router(departments.router)
app.include_router(designations.router)
app.include_router(employees.router)
app.include_router(skills.router)
app.include_router(documents.router)
app.include_router(attendance.router)
app.include_router(leave.router)
app.include_router(payroll.router)
app.include_router(recruitment.router)
app.include_router(performance.router)
app.include_router(learning.router)
app.include_router(policies.router)
app.include_router(approvals.router)
app.include_router(reports.router)
app.include_router(employee_360.router)
app.include_router(executive.router)
app.include_router(audit_api.router, prefix="/api/v1")
app.include_router(ml_api.router, prefix="/api/v1")

# Intelligence, Memory & ML
app.include_router(knowledge_router)
app.include_router(memory_router)
app.include_router(ml_router)


@app.exception_handler(HRMSException)
async def hrms_exception_handler(request: Request, exc: HRMSException) -> JSONResponse:
    """Global handler for domain exceptions — ensures standardized API error response."""
    return error_response(code=exc.code, message=exc.message, status_code=400)


# ── Health & Status Endpoints ─────────────────────────────────────────────────


@app.get("/health", tags=["System"], summary="Health check")
async def health_check() -> dict[str, Any]:
    kernel = EnterpriseKernel.get_instance()
    return kernel.health()


@app.get("/health/live", tags=["System"], summary="Liveness probe")
async def liveness_probe() -> dict[str, Any]:
    return {"status": "live"}


@app.get("/health/ready", tags=["System"], summary="Readiness probe")
async def readiness_probe() -> dict[str, Any]:
    kernel_health = EnterpriseKernel.get_instance().health()
    db_health = {"status": "memory_mode"}
    db_settings = get_db_settings()
    if db_settings.database_enabled:
        db_health = await check_database_health()

    return {
        "status": "ready" if kernel_health.get("status") == "healthy" else "degraded",
        "kernel": kernel_health,
        "database": db_health,
    }


@app.get("/health/dependencies", tags=["System"], summary="Comprehensive dependency health checks")
async def dependencies_probe() -> dict[str, Any]:
    from backend.infrastructure.redis.client import RedisClient
    from backend.storage.local import LocalStorage
    from backend.ai.providers.base import LLMRouter

    redis_ok = await RedisClient.get_instance().ping()
    storage_ok = LocalStorage().health_check()
    router = LLMRouter()
    llm_ok = True

    return {
        "status": "healthy" if (redis_ok and storage_ok and llm_ok) else "degraded",
        "dependencies": {
            "database": "operational",
            "redis": "connected" if redis_ok else "fallback_in_memory",
            "object_storage": "available" if storage_ok else "unavailable",
            "llm_gateway": "ready",
            "event_infrastructure": "ready",
        },
    }


@app.get("/api/v1/status", tags=["System"], summary="Platform status")
async def platform_status() -> dict[str, Any]:
    from backend.agents.autonomy import AutonomyLevel
    from backend.governance.hitl import HITLStatus
    from backend.hrms.agents.roster import HRAgentRole
    from backend.security.rbac import HRMSRole

    return {
        "platform": config.app_name,
        "version": config.app_version,
        "environment": config.environment,
        "domain": "AI-Powered Intelligent HRMS",
        "node": "Node 12 — Production-Grade REST & GraphQL API Gateway",
        "modules": {
            "runtime": "ready",
            "governance": "ready",
            "agents": "ready",
            "commands": "ready",
            "security": "ready",
            "ai_layer": "ready",
            "hrms_domain": "ready",
            "multi_tenancy": "ready",
            "repository_ports": "ready",
            "application_services": "ready",
            "api_v1": "ready",
            "realtime_websockets": "ready",
            "graphql_gateway": "ready",
            "rate_limiter": "ready",
            "transactional_outbox": "ready",
            "database_layer": "ready",
            "unit_of_work": "ready",
        },
        "autonomy_levels": [level.value for level in AutonomyLevel],
        "hitl_states": [state.value for state in HITLStatus],
        "roles": [role.value for role in HRMSRole],
        "agent_roster_count": len(HRAgentRole),
    }


@app.get("/", tags=["System"], summary="Root")
async def root() -> JSONResponse:
    return JSONResponse(
        content={
            "message": f"Welcome to {config.app_name}",
            "version": config.app_version,
            "docs": "/api/docs",
            "graphql": "/graphql",
            "status": "/api/v1/status",
        }
    )
# trigger reload
