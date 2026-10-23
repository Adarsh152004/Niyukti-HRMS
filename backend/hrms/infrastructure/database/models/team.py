"""
SQLAlchemy Models - Teams, TeamMembers, EmploymentHistory.
"""

from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class TeamModel(Base, TimestampMixin):
    """Internal functional teams (e.g. Frontend Squad, Core AI Team)."""
    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_team_org_code"),
        Index("ix_teams_org_id", "organization_id"),
        Index("ix_teams_dept_id", "department_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    department_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    lead_employee_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)


class TeamMemberModel(Base):
    """Assignment of employees to teams."""
    __tablename__ = "team_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "team_id", "employee_id", name="uq_team_member"),
        Index("ix_team_members_team", "organization_id", "team_id"),
        Index("ix_team_members_emp", "organization_id", "employee_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    team_id: Mapped[str] = mapped_column(String(64), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    role_in_team: Mapped[str] = mapped_column(String(64), default="MEMBER", nullable=False)  # LEAD, MEMBER, CONTRIBUTOR
    joined_at: Mapped[date] = mapped_column(Date, nullable=False)


class EmploymentHistoryModel(Base, TimestampMixin):
    """Historical audit of employee promotions, transfers, and manager changes."""
    __tablename__ = "employment_history"
    __table_args__ = (
        Index("ix_emp_history_emp_id", "organization_id", "employee_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    change_type: Mapped[str] = mapped_column(String(64), nullable=False)  # PROMOTION, TRANSFER, REDESIGNATION, MANAGER_CHANGE
    from_department_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    to_department_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    from_designation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    to_designation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    from_manager_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    to_manager_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    remarks: Mapped[str | None] = mapped_column(String(512), nullable=True)
    changed_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
