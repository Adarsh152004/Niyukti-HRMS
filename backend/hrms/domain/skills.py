"""
HRMS Domain — Skill and EmployeeSkill models.

Powers skill gap analysis, career development, recruitment matching, and workforce planning.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from backend.hrms.domain.common import HRMSBaseModel, generate_id, utc_now


class Proficiency(StrEnum):
    """Skill proficiency levels."""

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


# Compatibility alias
SkillLevel = Proficiency


class SkillCategory(StrEnum):
    TECHNICAL = "TECHNICAL"
    SOFT = "SOFT"
    DOMAIN = "DOMAIN"
    MANAGERIAL = "MANAGERIAL"
    LANGUAGE = "LANGUAGE"
    CERTIFICATION = "CERTIFICATION"
    TOOL = "TOOL"


class SkillStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class Skill(HRMSBaseModel):
    """
    A skill entity scoped to an organization.
    """

    skill_id: str = Field(default_factory=generate_id)
    organization_id: str = Field(description="Tenant ID boundary")
    name: str
    category: SkillCategory = Field(default=SkillCategory.TECHNICAL)
    description: str | None = Field(default=None)
    status: SkillStatus = Field(default=SkillStatus.ACTIVE)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @property
    def id(self) -> str:
        return self.skill_id

    @property
    def is_active(self) -> bool:
        return self.status == SkillStatus.ACTIVE


class EmployeeSkill(HRMSBaseModel):
    """
    Association between an employee and a skill with proficiency level.
    """

    employee_skill_id: str = Field(default_factory=generate_id)
    organization_id: str = Field(description="Tenant ID boundary")
    employee_id: str
    skill_id: str
    proficiency: Proficiency = Field(default=Proficiency.INTERMEDIATE)
    years_experience: float = Field(default=0.0, ge=0.0)
    verified: bool = Field(default=False)
    verified_by: str | None = Field(default=None, description="Actor ID who verified skill")
    verified_at: datetime | None = Field(default=None)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @property
    def id(self) -> str:
        return self.employee_skill_id
