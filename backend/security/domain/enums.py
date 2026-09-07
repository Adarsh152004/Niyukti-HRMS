"""
Security Domain — Enums for security, identity, authentication channels, and audit events.
"""

from __future__ import annotations

from enum import StrEnum


class AuthenticationChannel(StrEnum):
    """Channels through which principals authenticate or issue commands."""

    WEB = "WEB"
    CLI = "CLI"
    WHATSAPP = "WHATSAPP"
    API = "API"
    SERVICE = "SERVICE"
    AGENT = "AGENT"


class UserStatus(StrEnum):
    """Operational status of a human user account."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"
    SUSPENDED = "SUSPENDED"


class AgentStatus(StrEnum):
    """Lifecycle status of an AI agent identity."""

    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    DECOMMISSIONED = "DECOMMISSIONED"


class APIKeyStatus(StrEnum):
    """Status of an integration API key."""

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class TokenType(StrEnum):
    """JWT Token classification."""

    ACCESS = "ACCESS"
    REFRESH = "REFRESH"


class SecurityEventType(StrEnum):
    """Audit event classifications for security logging."""

    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    LOGOUT = "LOGOUT"
    TOKEN_REFRESH = "TOKEN_REFRESH"
    TOKEN_REVOKED = "TOKEN_REVOKED"
    SESSION_REVOKED = "SESSION_REVOKED"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    PASSWORD_RESET_REQUESTED = "PASSWORD_RESET_REQUESTED"
    PASSWORD_RESET_COMPLETED = "PASSWORD_RESET_COMPLETED"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ACCOUNT_UNLOCKED = "ACCOUNT_UNLOCKED"
    API_KEY_CREATED = "API_KEY_CREATED"
    API_KEY_REVOKED = "API_KEY_REVOKED"
    AGENT_CREATED = "AGENT_CREATED"
    AGENT_SUSPENDED = "AGENT_SUSPENDED"
    AGENT_REVOKED = "AGENT_REVOKED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_REVOKED = "PERMISSION_REVOKED"
    UNAUTHORIZED_ACTION = "UNAUTHORIZED_ACTION"
    CROSS_TENANT_ACCESS_ATTEMPT = "CROSS_TENANT_ACCESS_ATTEMPT"
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    REFRESH_TOKEN_REUSE = "REFRESH_TOKEN_REUSE"


class ApprovalStatus(StrEnum):
    """Human-In-The-Loop approval request states."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
