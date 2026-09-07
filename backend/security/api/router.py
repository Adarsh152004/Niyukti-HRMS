"""
API v1 — Security & Authentication Endpoints (`/api/v1/auth`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.api.response import error_response, success_response
from backend.security.api.dependencies import get_auth_service, get_current_identity
from backend.security.application.auth_service import AuthenticationError, AuthenticationService
from backend.security.domain.enums import AuthenticationChannel
from backend.security.domain.models import Identity

router = APIRouter(prefix="/api/v1/auth", tags=["Security & Auth"])


class UserRegisterRequest(BaseModel):
    organization_id: str
    username: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    organization_id: str
    email: str
    password: str
    channel: AuthenticationChannel = AuthenticationChannel.WEB


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AgentLoginRequest(BaseModel):
    agent_id: str
    organization_id: str


class CreateAPIKeyRequest(BaseModel):
    organization_id: str
    scopes: list[str] = Field(default_factory=list)
    name_prefix: str = "hrms_live"
    expires_days: int = 365


class RevokeSessionRequest(BaseModel):
    session_id: str


@router.post("/register", summary="Register Human User Account")
async def register_user(
    req: UserRegisterRequest,
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> JSONResponse:
    try:
        user = auth_service.register_user(
            organization_id=req.organization_id,
            username=req.username,
            email=req.email,
            password=req.password,
        )
        return success_response(
            data={"user_id": user.user_id, "email": user.email, "status": user.status.value},
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return error_response(code="REGISTRATION_FAILED", message=str(e), status_code=400)


@router.post("/login", summary="User Password Login")
async def user_login(
    req: UserLoginRequest,
    request: Request,
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> JSONResponse:
    try:
        ip = request.client.host if request.client else None
        ua = request.headers.get("User-Agent")
        access_tok, refresh_tok, sess, identity = auth_service.authenticate_user(
            organization_id=req.organization_id,
            email=req.email,
            password=req.password,
            channel=req.channel,
            ip_address=ip,
            user_agent=ua,
        )
        return success_response(
            data={
                "access_token": access_tok,
                "refresh_token": refresh_tok,
                "token_type": "Bearer",
                "session_id": sess.session_id,
                "actor_id": identity.actor_id,
                "organization_id": identity.organization_id,
            }
        )
    except AuthenticationError as e:
        return error_response(code="AUTHENTICATION_FAILED", message=str(e), status_code=401)


@router.post("/refresh", summary="Rotate Refresh Token")
async def refresh_token(
    req: RefreshTokenRequest,
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> JSONResponse:
    try:
        new_access_tok, new_refresh_tok = auth_service.refresh_access_token(req.refresh_token)
        return success_response(
            data={
                "access_token": new_access_tok,
                "refresh_token": new_refresh_tok,
                "token_type": "Bearer",
            }
        )
    except AuthenticationError as e:
        return error_response(code="REFRESH_FAILED", message=str(e), status_code=401)


@router.post("/agent/login", summary="AI Agent Authentication")
async def agent_login(
    req: AgentLoginRequest,
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> JSONResponse:
    try:
        access_tok, identity = auth_service.authenticate_agent(
            agent_id=req.agent_id,
            organization_id=req.organization_id,
        )
        return success_response(
            data={
                "access_token": access_tok,
                "token_type": "Bearer",
                "actor_id": identity.actor_id,
                "agent_id": identity.agent_id,
                "organization_id": identity.organization_id,
                "capabilities": list(identity.capabilities),
            }
        )
    except Exception as e:
        return error_response(code="AGENT_AUTH_FAILED", message=str(e), status_code=401)


@router.post("/api-keys", summary="Create Integration API Key")
async def create_api_key(
    req: CreateAPIKeyRequest,
    identity: Annotated[Identity, Depends(get_current_identity)],
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> JSONResponse:
    try:
        key_entity, raw_secret_key = auth_service.api_key_service.create_api_key(
            organization_id=req.organization_id,
            owner_actor_id=identity.actor_id,
            scopes=req.scopes,
            name_prefix=req.name_prefix,
            expires_days=req.expires_days,
        )
        return success_response(
            data={
                "key_id": key_entity.key_id,
                "prefix": key_entity.prefix,
                "raw_secret_key": raw_secret_key,  # Shown ONCE only
                "scopes": list(key_entity.scopes),
                "expires_at": key_entity.expires_at.isoformat() if key_entity.expires_at else None,
            },
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return error_response(code="API_KEY_CREATE_FAILED", message=str(e), status_code=400)


@router.delete("/api-keys/{key_id}", summary="Revoke API Key")
async def revoke_api_key(
    key_id: str,
    identity: Annotated[Identity, Depends(get_current_identity)],
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> JSONResponse:
    try:
        revoked = auth_service.api_key_service.revoke_api_key(key_id)
        return success_response(data={"key_id": revoked.key_id, "status": revoked.status.value})
    except Exception as e:
        return error_response(code="API_KEY_REVOKE_FAILED", message=str(e), status_code=400)


@router.post("/logout", summary="Logout Current Session")
async def logout(
    req: RevokeSessionRequest,
    identity: Annotated[Identity, Depends(get_current_identity)],
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> JSONResponse:
    auth_service.logout(req.session_id, identity.actor_id, identity.organization_id)
    return success_response(data={"message": "Logged out successfully."})


@router.post("/logout-all", summary="Logout All Active Sessions")
async def logout_all(
    identity: Annotated[Identity, Depends(get_current_identity)],
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> JSONResponse:
    count = auth_service.logout_all_sessions(identity.actor_id, identity.organization_id)
    return success_response(data={"message": f"Revoked {count} active sessions."})


@router.get("/me", summary="Current Principal Identity Profile")
async def get_my_identity(
    identity: Annotated[Identity, Depends(get_current_identity)],
) -> JSONResponse:
    return success_response(
        data={
            "actor_id": identity.actor_id,
            "organization_id": identity.organization_id,
            "actor_type": identity.actor_type.value,
            "user_id": identity.user_id,
            "agent_id": identity.agent_id,
            "roles": list(identity.roles),
            "permissions": list(identity.permissions),
            "capabilities": list(identity.capabilities),
        }
    )
