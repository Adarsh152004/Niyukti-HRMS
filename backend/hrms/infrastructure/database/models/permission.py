"""
SQLAlchemy Models - Permissions, RolePermissions, EmployeeRoles.
"""

from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class PermissionModel(Base, TimestampMixin):
    """Catalog of granular system permissions."""
    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_permission_org_code"),
        Index("ix_permissions_org_id", "organization_id"),
        Index("ix_permissions_module", "organization_id", "module"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    module: Mapped[str] = mapped_column(String(64), nullable=False)  # HR, PAYROLL, RECRUITMENT, PROJECTS, CLIENTS, FINANCE
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)


class RolePermissionModel(Base):
    """Junction table linking Roles to granular Permissions."""
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("organization_id", "role_id", "permission_id", name="uq_role_permission"),
        Index("ix_role_permissions_role", "organization_id", "role_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[str] = mapped_column(String(64), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[str] = mapped_column(String(64), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)


class EmployeeRoleModel(Base):
    """Junction table linking Employees to RBAC Roles."""
    __tablename__ = "employee_roles"
    __table_args__ = (
        UniqueConstraint("organization_id", "employee_id", "role_id", name="uq_employee_role"),
        Index("ix_employee_roles_emp", "organization_id", "employee_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[str] = mapped_column(String(64), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    assigned_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
