"""
Consent & Preference Center — Granular purpose-based consent and AI interaction preferences.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConsentPurpose(StrEnum):
    AI_ASSISTANT_INTERACTION = "AI_ASSISTANT_INTERACTION"
    AI_CAREER_RECOMMENDATION = "AI_CAREER_RECOMMENDATION"
    PERFORMANCE_ANALYTICS = "PERFORMANCE_ANALYTICS"
    AUTOMATED_NOTIFICATIONS = "AUTOMATED_NOTIFICATIONS"
    THIRD_PARTY_BENEFITS_SYNC = "THIRD_PARTY_BENEFITS_SYNC"


class ConsentRecord(BaseModel):
    """Immutable record of employee consent decision for a specific purpose."""

    consent_id: str
    organization_id: str
    employee_id: str
    purpose: ConsentPurpose
    granted: bool
    version: str = Field(default="1.0")
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    ip_address: str | None = None


class EmployeePreferenceProfile(BaseModel):
    """Employee notification and AI assistant preferences."""

    organization_id: str
    employee_id: str
    preferred_channels: list[str] = Field(default_factory=lambda: ["WEB", "EMAIL"])
    quiet_hours_enabled: bool = Field(default=False)
    quiet_hours_start_utc: str = Field(default="22:00")
    quiet_hours_end_utc: str = Field(default="08:00")
    ai_assistance_enabled: bool = Field(default=True)
    ai_proactive_reminders_enabled: bool = Field(default=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class ConsentService:
    """Service managing purpose-specific employee consents."""

    _instance: ConsentService | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._consents: dict[str, ConsentRecord] = {}
        self._preferences: dict[str, EmployeePreferenceProfile] = {}

    @classmethod
    def get_instance(cls) -> ConsentService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def record_consent(
        self,
        organization_id: str,
        employee_id: str,
        purpose: ConsentPurpose,
        granted: bool,
        ip_address: str | None = None,
    ) -> ConsentRecord:
        """Record or update consent for a purpose."""
        consent_id = f"cst-{organization_id}:{employee_id}:{purpose.value}"
        record = ConsentRecord(
            consent_id=consent_id,
            organization_id=organization_id,
            employee_id=employee_id,
            purpose=purpose,
            granted=granted,
            ip_address=ip_address,
        )

        async with self._lock:
            self._consents[consent_id] = record
            logger.info(f"Recorded consent for employee '{employee_id}' on purpose '{purpose.value}': {granted}")
            return record

    async def has_consent(self, organization_id: str, employee_id: str, purpose: ConsentPurpose) -> bool:
        """Verify whether employee has active consent for purpose."""
        consent_id = f"cst-{organization_id}:{employee_id}:{purpose.value}"
        async with self._lock:
            record = self._consents.get(consent_id)
            return record.granted if record else False

    async def get_or_create_preferences(self, organization_id: str, employee_id: str) -> EmployeePreferenceProfile:
        """Get or initialize employee preferences."""
        key = f"{organization_id}:{employee_id}"
        async with self._lock:
            profile = self._preferences.get(key)
            if not profile:
                profile = EmployeePreferenceProfile(organization_id=organization_id, employee_id=employee_id)
                self._preferences[key] = profile
            return profile

    async def update_preferences(
        self,
        organization_id: str,
        employee_id: str,
        preferred_channels: list[str] | None = None,
        quiet_hours_enabled: bool | None = None,
        ai_assistance_enabled: bool | None = None,
    ) -> EmployeePreferenceProfile:
        """Update employee preference settings."""
        profile = await self.get_or_create_preferences(organization_id, employee_id)
        if preferred_channels is not None:
            profile.preferred_channels = preferred_channels
        if quiet_hours_enabled is not None:
            profile.quiet_hours_enabled = quiet_hours_enabled
        if ai_assistance_enabled is not None:
            profile.ai_assistance_enabled = ai_assistance_enabled
        profile.updated_at = datetime.now(tz=UTC)

        key = f"{organization_id}:{employee_id}"
        async with self._lock:
            self._preferences[key] = profile
            return profile
