"""
FastAPI Security Dependencies — Bearer JWT authentication, Identity resolution, and authorization guards.

Strictly enforces:
JWT tenant ID == Actor tenant ID == TenantContext tenant ID.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.actor import Actor, ActorType
from backend.security.application.auth_service import AuthenticationService
from backend.security.application.jwt import JWTInvalidTokenError, JWTService, TokenPayload
from backend.security.domain.enums import AuthenticationChannel, TokenType
from backend.security.domain.models import Identity, User

security_scheme = HTTPBearer(auto_error=False)

# Global singleton authentication service instance for API layer
_AUTH_SERVICE = AuthenticationService()


def get_auth_service() -> AuthenticationService:
    """Return the global AuthenticationService singleton."""
    return _AUTH_SERVICE


def get_jwt_service() -> JWTService:
    return _AUTH_SERVICE.jwt_service


def get_current_identity(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    x_tenant_id: Annotated[str | None, Header(alias="X-Tenant-ID")] = None,
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)] = None,  # type: ignore[assignment]
) -> Identity:
    """
    Resolve and validate authenticated Identity from Authorization Bearer JWT.
    Strictly verifies signature, expiration, token type, and tenant binding.
    """
    svc = auth_service or _AUTH_SERVICE
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Bearer token header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload: TokenPayload = svc.jwt_service.decode_token(token, expected_type=TokenType.ACCESS)
    except JWTInvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired access token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # Tenant Binding Verification
    if x_tenant_id and x_tenant_id != payload.organization_id and "ALL_PERMISSIONS" not in payload.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Tenant mismatch: Token is bound to tenant '{payload.organization_id}' but request specifies '{x_tenant_id}'.",
        )

    return Identity(
        actor_id=payload.actor_id,
        organization_id=payload.organization_id,
        actor_type=payload.actor_type,
        auth_channel=AuthenticationChannel.WEB,
        user_id=payload.sub if payload.actor_type == ActorType.HUMAN else None,
        agent_id=payload.sub if payload.actor_type == ActorType.AI_AGENT else None,
        roles=payload.roles,
        permissions=payload.permissions,
        capabilities=payload.capabilities,
    )


def get_current_actor(
    identity: Annotated[Identity, Depends(get_current_identity)],
) -> Actor:
    """Return mapped Actor object from authenticated Identity."""
    return identity.to_actor()


def get_current_tenant_context(
    identity: Annotated[Identity, Depends(get_current_identity)],
) -> TenantContext:
    """Derive trusted TenantContext strictly from authenticated Identity claims."""
    return TenantContext(
        organization_id=identity.organization_id,
        actor_id=identity.actor_id,
        actor_type=identity.actor_type,
        permissions=identity.permissions,
    )


def get_current_user(
    identity: Annotated[Identity, Depends(get_current_identity)],
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)] = None,  # type: ignore[assignment]
) -> User:
    """Require current identity to be a Human User."""
    if identity.actor_type != ActorType.HUMAN or not identity.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires a human user identity.",
        )
    svc = auth_service or _AUTH_SERVICE
    user = svc._users_by_id.get(identity.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user record not found.",
        )
    return user


def require_permission(permission_name: str) -> Callable[[Actor], Actor]:
    """Dependency factory enforcing explicit permission check."""

    def permission_guard(actor: Annotated[Actor, Depends(get_current_actor)]) -> Actor:
        if permission_name in actor.permissions or "ALL_PERMISSIONS" in actor.permissions:
            return actor
        if "SUPER_ADMIN" in actor.roles or "HR_ADMIN" in actor.roles:
            return actor
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Action requires permission '{permission_name}'.",
        )

    return permission_guard


def require_capability(capability_name: str) -> Callable[[Actor], Actor]:
    """Dependency factory enforcing explicit capability grant (ideal for AI Agents)."""

    def capability_guard(actor: Annotated[Actor, Depends(get_current_actor)]) -> Actor:
        caps = set(actor.metadata.get("capabilities", []))
        if capability_name in caps or "ALL_CAPABILITIES" in caps or "ALL_PERMISSIONS" in actor.permissions:
            return actor
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Action requires capability '{capability_name}'.",
        )

    return capability_guard


def require_actor_type(target_type: ActorType) -> Callable[[Actor], Actor]:
    """Dependency factory enforcing principal classification check."""

    def actor_type_guard(actor: Annotated[Actor, Depends(get_current_actor)]) -> Actor:
        if actor.actor_type != target_type:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Endpoint restricted to principal type '{target_type.value}'.",
            )
        return actor

    return actor_type_guard
