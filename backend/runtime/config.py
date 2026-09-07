"""
HRMS Configuration — Runtime configuration loaded from environment variables.

Uses pydantic-settings for typed, validated config with env-var override support.
No secrets are logged.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class HRMSConfig(BaseSettings):
    """Central configuration for the AI-Powered Intelligent HRMS platform."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="HRMS_",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = Field(default="AI-Powered Intelligent HRMS")
    app_version: str = Field(default="1.0.0")
    environment: Literal["development", "staging", "production"] = Field(default="development")
    debug: bool = Field(default=False)

    # ── API Server ────────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")

    # ── Security ──────────────────────────────────────────────────────────────
    secret_key: SecretStr = Field(default=SecretStr("change-me-in-production"))
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)

    # ── Database (planned — PostgreSQL) ───────────────────────────────────────
    database_url: str = Field(default="postgresql://hrms:hrms@localhost:5432/hrms_db")
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=20)

    # ── Cache / Event Bus (planned — Redis) ───────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_event_channel: str = Field(default="hrms:events")

    # ── Vector Memory (planned — Qdrant) ─────────────────────────────────────
    qdrant_url: str = Field(default="http://localhost:6333")
    qdrant_collection_prefix: str = Field(default="hrms")

    # ── AI Provider (planned) ─────────────────────────────────────────────────
    ai_provider: str = Field(default="openai")
    ai_model_default: str = Field(default="gpt-4o")
    ai_api_key: SecretStr = Field(default=SecretStr(""))
    ai_temperature: float = Field(default=0.1)
    ai_max_tokens: int = Field(default=4096)

    # ── Governance ────────────────────────────────────────────────────────────
    default_autonomy_level: int = Field(default=2, ge=0, le=5)
    hitl_approval_timeout_hours: int = Field(default=24)
    high_risk_requires_human_approval: bool = Field(default=True)
    emergency_stop_enabled: bool = Field(default=True)

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    log_format: Literal["json", "text"] = Field(default="json")
    log_pii_masking: bool = Field(default=True)

    # ── Notifications ────────────────────────────────────────────────────────
    smtp_host: str = Field(default="localhost")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: SecretStr = Field(default=SecretStr(""))

    # ── WhatsApp (planned) ────────────────────────────────────────────────────
    whatsapp_enabled: bool = Field(default=False)
    whatsapp_api_url: str = Field(default="")
    whatsapp_api_token: SecretStr = Field(default=SecretStr(""))


@lru_cache(maxsize=1)
def get_config() -> HRMSConfig:
    """Return the singleton HRMS configuration instance."""
    return HRMSConfig()
