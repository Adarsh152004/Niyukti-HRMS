"""Tests — Persistence Model schema definitions and constraints inspection."""

from backend.database.base import Base


def test_all_models_registered_in_metadata():
    tables = Base.metadata.tables
    assert "organizations" in tables
    assert "departments" in tables
    assert "designations" in tables
    assert "roles" in tables
    assert "employees" in tables
    assert "skills" in tables
    assert "employee_skills" in tables
    assert "employee_documents" in tables
    assert "outbox_events" in tables


def test_employee_table_foreign_keys_and_uniqueness():
    emp_table = Base.metadata.tables["employees"]
    fk_target_tables = {fk.column.table.name for fk in emp_table.foreign_keys}
    assert "organizations" in fk_target_tables
    assert "departments" in fk_target_tables
    assert "designations" in fk_target_tables
    assert "employees" in fk_target_tables  # self-referential manager_id

    unique_constraint_names = {uq.name for uq in emp_table.constraints if hasattr(uq, "name") and uq.name}
    assert "uq_employee_org_code" in unique_constraint_names
    assert "uq_employee_org_email" in unique_constraint_names


def test_department_and_designation_composite_uniqueness():
    dept_table = Base.metadata.tables["departments"]
    des_table = Base.metadata.tables["designations"]

    dept_uqs = {uq.name for uq in dept_table.constraints if hasattr(uq, "name") and uq.name}
    des_uqs = {uq.name for uq in des_table.constraints if hasattr(uq, "name") and uq.name}

    assert "uq_department_org_code" in dept_uqs
    assert "uq_designation_org_code" in des_uqs
