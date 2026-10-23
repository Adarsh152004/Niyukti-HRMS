"""initial_hrms_schema

Revision ID: 001_initial_hrms_schema
Revises:
Create Date: 2026-08-22 20:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial_hrms_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Organizations
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("industry", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=8), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("registration_number", sa.String(length=128), nullable=True),
        sa.Column("logo_url", sa.String(length=512), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(length=512), nullable=True),
        sa.Column("founded_year", sa.Integer(), nullable=True),
        sa.Column("employee_count", sa.Integer(), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)

    # 2. Departments
    op.create_table(
        "departments",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("parent_department_id", sa.String(length=64), nullable=True),
        sa.Column("manager_employee_id", sa.String(length=64), nullable=True),
        sa.Column("cost_center", sa.String(length=64), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "code", name="uq_department_org_code"),
    )
    op.create_index("ix_departments_org_code", "departments", ["organization_id", "code"], unique=False)
    op.create_index("ix_departments_org_id", "departments", ["organization_id"], unique=False)

    # 3. Designations
    op.create_table(
        "designations",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("min_experience_years", sa.Float(), nullable=True),
        sa.Column("is_managerial", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "code", name="uq_designation_org_code"),
    )
    op.create_index("ix_designations_dept_id", "designations", ["department_id"], unique=False)
    op.create_index("ix_designations_org_id", "designations", ["organization_id"], unique=False)

    # 4. Roles
    op.create_table(
        "roles",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("permissions", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("is_system_role", sa.Boolean(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "code", name="uq_role_org_code"),
    )
    op.create_index("ix_roles_org_id", "roles", ["organization_id"], unique=False)

    # 5. Employees
    op.create_table(
        "employees",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("employee_code", sa.String(length=64), nullable=False),
        sa.Column("first_name", sa.String(length=128), nullable=False),
        sa.Column("last_name", sa.String(length=128), nullable=False),
        sa.Column("preferred_name", sa.String(length=128), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=32), nullable=True),
        sa.Column("department_id", sa.String(length=64), nullable=False),
        sa.Column("designation_id", sa.String(length=64), nullable=False),
        sa.Column("manager_id", sa.String(length=64), nullable=True),
        sa.Column("employment_status", sa.String(length=32), nullable=False),
        sa.Column("employment_type", sa.String(length=32), nullable=False),
        sa.Column("joining_date", sa.Date(), nullable=False),
        sa.Column("exit_date", sa.Date(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["designation_id"], ["designations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["manager_id"], ["employees.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "email", name="uq_employee_org_email"),
        sa.UniqueConstraint("organization_id", "employee_code", name="uq_employee_org_code"),
    )
    op.create_index("ix_employees_code", "employees", ["organization_id", "employee_code"], unique=False)
    op.create_index("ix_employees_dept_id", "employees", ["department_id"], unique=False)
    op.create_index("ix_employees_des_id", "employees", ["designation_id"], unique=False)
    op.create_index("ix_employees_email", "employees", ["organization_id", "email"], unique=False)
    op.create_index("ix_employees_manager_id", "employees", ["manager_id"], unique=False)
    op.create_index("ix_employees_org_id", "employees", ["organization_id"], unique=False)

    # 6. Skills
    op.create_table(
        "skills",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", name="uq_skill_org_name"),
    )
    op.create_index("ix_skills_org_id", "skills", ["organization_id"], unique=False)

    # 7. Employee Skills
    op.create_table(
        "employee_skills",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("employee_id", sa.String(length=64), nullable=False),
        sa.Column("skill_id", sa.String(length=64), nullable=False),
        sa.Column("proficiency", sa.String(length=32), nullable=False),
        sa.Column("years_experience", sa.Float(), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("verified_by", sa.String(length=64), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "employee_id", "skill_id", name="uq_emp_skill"),
    )
    op.create_index("ix_employee_skills_org_emp", "employee_skills", ["organization_id", "employee_id"], unique=False)

    # 8. Employee Documents
    op.create_table(
        "employee_documents",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("employee_id", sa.String(length=64), nullable=False),
        sa.Column("document_type", sa.String(length=64), nullable=False),
        sa.Column("document_name", sa.String(length=255), nullable=False),
        sa.Column("storage_reference", sa.String(length=512), nullable=False),
        sa.Column("mime_type", sa.String(length=128), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("verification_status", sa.String(length=32), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_by", sa.String(length=64), nullable=True),
        sa.Column("expires_at", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_org_emp", "employee_documents", ["organization_id", "employee_id"], unique=False)
    op.create_index("ix_documents_org_id", "employee_documents", ["organization_id"], unique=False)

    # 9. Outbox Events
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("aggregate_id", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )
    op.create_index("ix_outbox_events_status", "outbox_events", ["status", "occurred_at"], unique=False)
    op.create_index("ix_outbox_org_id", "outbox_events", ["organization_id"], unique=False)


def downgrade() -> None:
    op.drop_table("outbox_events")
    op.drop_table("employee_documents")
    op.drop_table("employee_skills")
    op.drop_table("skills")
    op.drop_table("employees")
    op.drop_table("roles")
    op.drop_table("designations")
    op.drop_table("departments")
    op.drop_table("organizations")
