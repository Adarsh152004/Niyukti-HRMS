"""
JWT Application Service — Access and Refresh token issuance & validation.

Uses python-jose for JWT encoding and decoding.
Validates signature, expiration, issuer, audience, token type, and jti claims.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import cast

try:
    from jose import JWTError, jwt
except ImportError:
    import jwt

    JWTError = jwt.PyJWTError
from pydantic import BaseModel, Field

from backend.hrms.domain.actor import ActorType
from backend.security.domain.enums import TokenType


class JWTInvalidTokenError(Exception):
    """Raised when a JWT is malformed, expired, or has an invalid signature."""

    pass


class TokenPayload(BaseModel):
    """
    Decoded JWT token payload schema.
    """

    sub: str = Field(description="Subject (user_id, agent_id, or actor_id)")
    actor_id: str
    organization_id: str
    actor_type: ActorType
    roles: set[str] = Field(default_factory=set)
    permissions: set[str] = Field(default_factory=set)
    capabilities: set[str] = Field(default_factory=set)
    token_type: TokenType = Field(default=TokenType.ACCESS)
    jti: str = Field(default_factory=lambda: str(uuid.uuid4()))
    iss: str = Field(default="hrms-auth-service")
    aud: str = Field(default="hrms-platform")
    iat: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    exp: datetime


class JWTService:
    """
    JWT Access & Refresh Token Service.
    """

    def __init__(
        self,
        secret_key: str = "hrms-enterprise-secret-key-change-in-production-2026",
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 7,
        issuer: str = "hrms-auth-service",
        audience: str = "hrms-platform",
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.issuer = issuer
        self.audience = audience

    def create_access_token(
        self,
        subject: str,
        actor_id: str,
        organization_id: str,
        actor_type: ActorType | str = ActorType.HUMAN,
        roles: set[str] | list[str] | None = None,
        permissions: set[str] | list[str] | None = None,
        capabilities: set[str] | list[str] | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a signed JWT access token."""
        now = datetime.now(tz=UTC)
        delta = expires_delta or timedelta(minutes=self.access_token_expire_minutes)
        expire = now + delta

        roles_set = set(roles) if roles else set()
        permissions_set = set(permissions) if permissions else set()
        capabilities_set = set(capabilities) if capabilities else set()
        actor_type_val = actor_type.value if hasattr(actor_type, "value") else str(actor_type)

        payload = {
            "sub": subject,
            "actor_id": actor_id,
            "organization_id": organization_id,
            "actor_type": actor_type_val,
            "roles": list(roles_set),
            "permissions": list(permissions_set),
            "capabilities": list(capabilities_set),
            "token_type": TokenType.ACCESS.value,
            "jti": str(uuid.uuid4()),
            "iss": self.issuer,
            "aud": self.audience,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }
        return cast("str", jwt.encode(payload, self.secret_key, algorithm=self.algorithm))

    def create_refresh_token(
        self,
        subject: str,
        actor_id: str,
        organization_id: str,
        actor_type: ActorType,
        family_id: str,
        expires_delta: timedelta | None = None,
    ) -> tuple[str, str, datetime]:
        """
        Create a signed JWT refresh token.
        Returns: (token_str, jti, expire_datetime)
        """
        now = datetime.now(tz=UTC)
        delta = expires_delta or timedelta(days=self.refresh_token_expire_days)
        expire = now + delta
        jti = str(uuid.uuid4())

        payload = {
            "sub": subject,
            "actor_id": actor_id,
            "organization_id": organization_id,
            "actor_type": actor_type.value,
            "family_id": family_id,
            "token_type": TokenType.REFRESH.value,
            "jti": jti,
            "iss": self.issuer,
            "aud": self.audience,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }
        encoded = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return encoded, jti, expire

    def verify_access_token(self, token: str) -> TokenPayload:
        """Verify and decode access token."""
        return self.decode_token(token, TokenType.ACCESS)

    def verify_token(self, token: str, expected_type: TokenType = TokenType.ACCESS) -> TokenPayload:
        """Alias for decode_token."""
        return self.decode_token(token, expected_type)

    def decode_token(self, token: str, expected_type: TokenType = TokenType.ACCESS) -> TokenPayload:
        """
        Decode and validate signature, expiration, issuer, audience, and token type.
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
            )
        except JWTError as e:
            raise JWTInvalidTokenError(f"Invalid token signature or expired: {e}") from e

        token_type_raw = payload.get("token_type")
        if token_type_raw != expected_type.value:
            raise JWTInvalidTokenError(f"Token type mismatch: expected '{expected_type.value}', got '{token_type_raw}'")

        actor_type_raw = payload.get("actor_type")
        try:
            actor_type_enum = ActorType(actor_type_raw)
        except ValueError as e:
            raise JWTInvalidTokenError(f"Invalid actor_type claim in token: {actor_type_raw}") from e

        exp_timestamp = payload.get("exp")
        exp_dt = datetime.fromtimestamp(exp_timestamp, tz=UTC)

        return TokenPayload(
            sub=payload["sub"],
            actor_id=payload["actor_id"],
            organization_id=payload["organization_id"],
            actor_type=actor_type_enum,
            roles=set(payload.get("roles", [])),
            permissions=set(payload.get("permissions", [])),
            capabilities=set(payload.get("capabilities", [])),
            token_type=expected_type,
            jti=payload.get("jti", str(uuid.uuid4())),
            iss=payload.get("iss", self.issuer),
            aud=payload.get("aud", self.audience),
            iat=datetime.fromtimestamp(payload.get("iat", 0), tz=UTC),
            exp=exp_dt,
        )
