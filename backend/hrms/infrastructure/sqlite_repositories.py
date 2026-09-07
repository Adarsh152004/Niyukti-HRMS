"""
SQLite Repository Implementations.
Direct, transactional, and tenant-scoped access to `hrms.db`.
"""

from __future__ import annotations

import datetime
import json
import logging
import uuid
from collections.abc import Sequence
from datetime import date, datetime as dt
from typing import Any

from backend.database.sqlite_db import get_db_connection
from backend.hrms.domain.actor import Actor
from backend.hrms.domain.attendance import AttendanceRecord
from backend.hrms.domain.common import AttendanceStatus, EmploymentStatus, EmploymentType, Gender, utc_now
from backend.hrms.domain.employee import Employee
from backend.hrms.domain.organization import Department, DepartmentStatus, Designation, DesignationStatus
from backend.hrms.ports.repositories import (
    AttendanceRepository,
    DepartmentRepository,
    DesignationRepository,
    EmployeeRepository,
)

logger = logging.getLogger(__name__)


def _parse_dt(val: Any) -> dt | None:
    if not val:
        return None
    if isinstance(val, dt):
        return val
    try:
        return dt.fromisoformat(str(val))
    except Exception:
        return None


def _parse_date(val: Any) -> date:
    if isinstance(val, date):
        return val
    return date.fromisoformat(str(val).split("T")[0].split(" ")[0])


class SqliteEmployeeRepository(EmployeeRepository):
    """SQLite Employee repository strictly enforcing tenant scoping."""

    async def create(self, employee: Employee) -> Employee:
        now_str = utc_now().isoformat()
        async with get_db_connection() as db:
            await db.execute(
                """
                INSERT INTO employees (
                    id, organization_id, employee_code, first_name, last_name, preferred_name,
                    email, phone, department_id, designation_id, manager_id,
                    employment_status, employment_type, joining_date, exit_date,
                    location, timezone, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    employee.employee_id,
                    employee.organization_id,
                    employee.employee_code,
                    employee.first_name,
                    employee.last_name,
                    employee.preferred_name,
                    employee.email,
                    employee.phone,
                    employee.department_id,
                    employee.designation_id,
                    employee.manager_id,
                    employee.employment_status.value if hasattr(employee.employment_status, "value") else str(employee.employment_status),
                    employee.employment_type.value if hasattr(employee.employment_type, "value") else str(employee.employment_type),
                    employee.joining_date.isoformat() if employee.joining_date else None,
                    employee.exit_date.isoformat() if employee.exit_date else None,
                    employee.location,
                    employee.timezone,
                    json.dumps(employee.metadata or {}),
                    now_str,
                    now_str,
                ),
            )
            await db.commit()
        return employee

    async def get_by_id(self, organization_id: str, employee_id: str) -> Employee | None:
        async with get_db_connection() as db:
            async with db.execute(
                "SELECT * FROM employees WHERE organization_id = ? AND id = ?",
                (organization_id, employee_id),
            ) as c:
                row = await c.fetchone()
                if not row:
                    return None
                return self._row_to_entity(dict(row))

    async def get_by_code(self, organization_id: str, employee_code: str) -> Employee | None:
        async with get_db_connection() as db:
            async with db.execute(
                "SELECT * FROM employees WHERE organization_id = ? AND employee_code = ?",
                (organization_id, employee_code),
            ) as c:
                row = await c.fetchone()
                if not row:
                    return None
                return self._row_to_entity(dict(row))

    async def get_by_email(self, organization_id: str, email: str) -> Employee | None:
        async with get_db_connection() as db:
            async with db.execute(
                "SELECT * FROM employees WHERE organization_id = ? AND email = ?",
                (organization_id, email),
            ) as c:
                row = await c.fetchone()
                if not row:
                    return None
                return self._row_to_entity(dict(row))

    async def list_by_organization(
        self, organization_id: str, department_id: str | None = None, limit: int = 100, offset: int = 0
    ) -> Sequence[Employee]:
        async with get_db_connection() as db:
            if department_id:
                async with db.execute(
                    "SELECT * FROM employees WHERE organization_id = ? AND department_id = ? ORDER BY created_at ASC LIMIT ? OFFSET ?",
                    (organization_id, department_id, limit, offset),
                ) as c:
                    rows = await c.fetchall()
            else:
                async with db.execute(
                    "SELECT * FROM employees WHERE organization_id = ? ORDER BY created_at ASC LIMIT ? OFFSET ?",
                    (organization_id, limit, offset),
                ) as c:
                    rows = await c.fetchall()
            return [self._row_to_entity(dict(r)) for r in rows]

    async def update(self, employee: Employee) -> Employee:
        now_str = utc_now().isoformat()
        async with get_db_connection() as db:
            await db.execute(
                """
                UPDATE employees SET
                    first_name = ?, last_name = ?, preferred_name = ?, email = ?, phone = ?,
                    department_id = ?, designation_id = ?, manager_id = ?,
                    employment_status = ?, employment_type = ?, joining_date = ?, exit_date = ?,
                    location = ?, timezone = ?, metadata_json = ?, updated_at = ?
                WHERE organization_id = ? AND id = ?
                """,
                (
                    employee.first_name,
                    employee.last_name,
                    employee.preferred_name,
                    employee.email,
                    employee.phone,
                    employee.department_id,
                    employee.designation_id,
                    employee.manager_id,
                    employee.employment_status.value if hasattr(employee.employment_status, "value") else str(employee.employment_status),
                    employee.employment_type.value if hasattr(employee.employment_type, "value") else str(employee.employment_type),
                    employee.joining_date.isoformat() if employee.joining_date else None,
                    employee.exit_date.isoformat() if employee.exit_date else None,
                    employee.location,
                    employee.timezone,
                    json.dumps(employee.metadata or {}),
                    now_str,
                    employee.organization_id,
                    employee.employee_id,
                ),
            )
            await db.commit()
        return employee

    def _row_to_entity(self, r: dict[str, Any]) -> Employee:
        status_raw = r.get("employment_status") or "ACTIVE"
        try:
            status_enum = EmploymentStatus(status_raw)
        except Exception:
            status_enum = EmploymentStatus.ACTIVE

        type_raw = r.get("employment_type") or "FULL_TIME"
        try:
            type_enum = EmploymentType(type_raw)
        except Exception:
            type_enum = EmploymentType.FULL_TIME

        meta = {}
        if r.get("metadata_json"):
            try:
                meta = json.loads(r["metadata_json"])
            except Exception:
                pass

        return Employee(
            employee_id=r["id"],
            organization_id=r["organization_id"],
            employee_code=r["employee_code"],
            first_name=r["first_name"],
            last_name=r["last_name"],
            preferred_name=r.get("preferred_name"),
            email=r["email"],
            phone=r.get("phone"),
            date_of_birth=_parse_date(r["date_of_birth"]) if r.get("date_of_birth") else None,
            gender=None,
            department_id=r.get("department_id") or "",
            designation_id=r.get("designation_id") or "",
            manager_id=r.get("manager_id"),
            employment_status=status_enum,
            employment_type=type_enum,
            joining_date=_parse_date(r["joining_date"]) if r.get("joining_date") else utc_now().date(),
            exit_date=_parse_date(r["exit_date"]) if r.get("exit_date") else None,
            location=r.get("location"),
            timezone=r.get("timezone") or "UTC",
            metadata=meta,
            created_at=_parse_dt(r.get("created_at")) or utc_now(),
            updated_at=_parse_dt(r.get("updated_at")) or utc_now(),
        )


class SqliteDepartmentRepository(DepartmentRepository):
    """SQLite Department repository."""

    async def get_by_id(self, organization_id: str, department_id: str) -> Department | None:
        async with get_db_connection() as db:
            async with db.execute(
                "SELECT * FROM departments WHERE organization_id = ? AND id = ?",
                (organization_id, department_id),
            ) as c:
                row = await c.fetchone()
                if not row:
                    return None
                return self._row_to_entity(dict(row))

    async def get_by_code(self, organization_id: str, code: str) -> Department | None:
        async with get_db_connection() as db:
            async with db.execute(
                "SELECT * FROM departments WHERE organization_id = ? AND code = ?",
                (organization_id, code),
            ) as c:
                row = await c.fetchone()
                if not row:
                    return None
                return self._row_to_entity(dict(row))

    async def list_by_organization(self, organization_id: str) -> Sequence[Department]:
        async with get_db_connection() as db:
            async with db.execute("SELECT * FROM departments WHERE organization_id = ?", (organization_id,)) as c:
                rows = await c.fetchall()
                return [self._row_to_entity(dict(r)) for r in rows]

    async def create(self, department: Department) -> Department:
        async with get_db_connection() as db:
            await db.execute(
                """
                INSERT INTO departments (
                    id, organization_id, name, code, description, parent_department_id,
                    manager_employee_id, cost_center, location, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    department.department_id,
                    department.organization_id,
                    department.name,
                    department.code,
                    department.description,
                    department.parent_department_id,
                    department.manager_employee_id,
                    department.cost_center,
                    department.location,
                    department.status.value if hasattr(department.status, "value") else str(department.status),
                    utc_now().isoformat(),
                    utc_now().isoformat(),
                ),
            )
            await db.commit()
        return department

    async def update(self, department: Department) -> Department:
        return department

    def _row_to_entity(self, r: dict[str, Any]) -> Department:
        status_raw = r.get("status") or "ACTIVE"
        try:
            status_enum = DepartmentStatus(status_raw)
        except Exception:
            status_enum = DepartmentStatus.ACTIVE

        return Department(
            department_id=r["id"],
            organization_id=r["organization_id"],
            name=r["name"],
            code=r["code"],
            description=r.get("description"),
            parent_department_id=r.get("parent_department_id"),
            manager_employee_id=r.get("manager_employee_id"),
            cost_center=r.get("cost_center"),
            location=r.get("location"),
            status=status_enum,
            created_at=_parse_dt(r.get("created_at")) or utc_now(),
            updated_at=_parse_dt(r.get("updated_at")) or utc_now(),
        )


class SqliteDesignationRepository(DesignationRepository):
    """SQLite Designation repository."""

    async def get_by_id(self, organization_id: str, designation_id: str) -> Designation | None:
        async with get_db_connection() as db:
            async with db.execute("SELECT * FROM designations WHERE organization_id = ? AND id = ?", (organization_id, designation_id)) as c:
                row = await c.fetchone()
                if not row:
                    return None
                return self._row_to_entity(dict(row))

    async def get_by_code(self, organization_id: str, code: str) -> Designation | None:
        async with get_db_connection() as db:
            async with db.execute("SELECT * FROM designations WHERE organization_id = ? AND code = ?", (organization_id, code)) as c:
                row = await c.fetchone()
                if not row:
                    return None
                return self._row_to_entity(dict(row))

    async def list_by_organization(self, organization_id: str) -> Sequence[Designation]:
        async with get_db_connection() as db:
            async with db.execute("SELECT * FROM designations WHERE organization_id = ?", (organization_id,)) as c:
                rows = await c.fetchall()
                return [self._row_to_entity(dict(r)) for r in rows]

    async def create(self, designation: Designation) -> Designation:
        return designation

    async def update(self, designation: Designation) -> Designation:
        return designation

    def _row_to_entity(self, r: dict[str, Any]) -> Designation:
        status_raw = r.get("status") or "ACTIVE"
        try:
            status_enum = DesignationStatus(status_raw)
        except Exception:
            status_enum = DesignationStatus.ACTIVE

        return Designation(
            designation_id=r["id"],
            organization_id=r["organization_id"],
            name=r["name"],
            code=r["code"],
            description=r.get("description"),
            level=r.get("level") or 1,
            department_id=r.get("department_id"),
            status=status_enum,
            min_experience_years=float(r["min_experience_years"]) if r.get("min_experience_years") is not None else None,
            is_managerial=bool(r.get("is_managerial")),
            created_at=_parse_dt(r.get("created_at")) or utc_now(),
            updated_at=_parse_dt(r.get("updated_at")) or utc_now(),
        )


class SqliteAttendanceRepository(AttendanceRepository):
    """SQLite implementation of AttendanceRepository reading/writing live records."""

    async def get_by_employee_and_date(
        self, organization_id: str, employee_id: str, record_date: date
    ) -> AttendanceRecord | None:
        date_str = record_date.isoformat()
        async with get_db_connection() as db:
            async with db.execute(
                "SELECT * FROM attendance_records WHERE organization_id = ? AND employee_id = ? AND date = ?",
                (organization_id, employee_id, date_str),
            ) as c:
                row = await c.fetchone()
                if not row:
                    return None
                return self._row_to_entity(dict(row))

    async def list_by_employee(
        self, organization_id: str, employee_id: str, start_date: date | None = None, end_date: date | None = None
    ) -> Sequence[AttendanceRecord]:
        async with get_db_connection() as db:
            query = "SELECT * FROM attendance_records WHERE organization_id = ? AND employee_id = ?"
            params: list[Any] = [organization_id, employee_id]
            if start_date:
                query += " AND date >= ?"
                params.append(start_date.isoformat())
            if end_date:
                query += " AND date <= ?"
                params.append(end_date.isoformat())
            query += " ORDER BY date DESC"
            async with db.execute(query, tuple(params)) as c:
                rows = await c.fetchall()
                return [self._row_to_entity(dict(r)) for r in rows]

    async def list_by_organization_and_date(
        self, organization_id: str, record_date: date
    ) -> Sequence[AttendanceRecord]:
        date_str = record_date.isoformat()
        async with get_db_connection() as db:
            async with db.execute(
                "SELECT * FROM attendance_records WHERE organization_id = ? AND date = ?",
                (organization_id, date_str),
            ) as c:
                rows = await c.fetchall()
                return [self._row_to_entity(dict(r)) for r in rows]

    async def create_or_update(self, record: AttendanceRecord) -> AttendanceRecord:
        now_str = utc_now().isoformat()
        date_str = record.date.isoformat()
        check_in_str = record.check_in_time.isoformat() if record.check_in_time else None
        check_out_str = record.check_out_time.isoformat() if record.check_out_time else None
        status_val = record.status.value if hasattr(record.status, "value") else str(record.status)

        async with get_db_connection() as db:
            async with db.execute(
                "SELECT id FROM attendance_records WHERE organization_id = ? AND employee_id = ? AND date = ?",
                (record.organization_id, record.employee_id, date_str),
            ) as c:
                existing = await c.fetchone()

            if existing:
                await db.execute(
                    """
                    UPDATE attendance_records SET 
                        check_in = COALESCE(?, check_in),
                        check_out = ?,
                        status = ?,
                        updated_at = ?
                    WHERE organization_id = ? AND employee_id = ? AND date = ?
                    """,
                    (check_in_str, check_out_str, status_val, now_str, record.organization_id, record.employee_id, date_str),
                )
            else:
                rec_id = record.attendance_id or f"att-{record.employee_id}-{date_str}"
                await db.execute(
                    """
                    INSERT INTO attendance_records (
                        id, organization_id, employee_id, date, check_in, check_out,
                        status, source, overtime_hours, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'WEB', 0.0, ?, ?)
                    """,
                    (rec_id, record.organization_id, record.employee_id, date_str, check_in_str, check_out_str, status_val, now_str, now_str),
                )
            await db.commit()
        return record

    def _row_to_entity(self, r: dict[str, Any]) -> AttendanceRecord:
        status_raw = r.get("status") or "PRESENT"
        try:
            status_enum = AttendanceStatus(status_raw)
        except Exception:
            status_enum = AttendanceStatus.PRESENT

        return AttendanceRecord(
            attendance_id=r["id"],
            employee_id=r["employee_id"],
            organization_id=r["organization_id"],
            date=_parse_date(r["date"]),
            shift_id=None,
            status=status_enum,
            check_in_time=_parse_dt(r.get("check_in")),
            check_out_time=_parse_dt(r.get("check_out")),
            work_hours=None,
            overtime_hours=float(r.get("overtime_hours") or 0.0),
            late_minutes=0,
            early_departure_minutes=0,
            biometric_record_id=None,
            is_regularized=False,
            regularized_by=None,
            notes=r.get("remarks"),
            created_at=_parse_dt(r.get("created_at")) or utc_now(),
            updated_at=_parse_dt(r.get("updated_at")) or utc_now(),
        )


class SqliteWorkLogRepository:
    """Repository for daily work logs decoupled from tasks."""

    async def create(
        self,
        organization_id: str,
        employee_id: str,
        description: str,
        hours_spent: float = 1.0,
        task_id: str | None = None,
        blockers: str | None = None,
        work_date: date | None = None,
    ) -> dict[str, Any]:
        log_id = f"wl-{uuid.uuid4().hex[:10]}"
        now_str = utc_now().isoformat()
        date_str = (work_date or utc_now().date()).isoformat()

        async with get_db_connection() as db:
            await db.execute(
                """
                INSERT INTO work_logs (
                    id, organization_id, employee_id, task_id, work_date,
                    description, hours_spent, blockers, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (log_id, organization_id, employee_id, task_id, date_str, description, hours_spent, blockers, now_str, now_str),
            )
            await db.commit()

        return {
            "id": log_id,
            "organization_id": organization_id,
            "employee_id": employee_id,
            "task_id": task_id,
            "work_date": date_str,
            "description": description,
            "hours_spent": hours_spent,
            "blockers": blockers,
            "created_at": now_str,
        }

    async def list_by_employee(
        self, organization_id: str, employee_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        async with get_db_connection() as db:
            async with db.execute(
                "SELECT * FROM work_logs WHERE organization_id = ? AND employee_id = ? ORDER BY work_date DESC, created_at DESC LIMIT ?",
                (organization_id, employee_id, limit),
            ) as c:
                rows = await c.fetchall()
                return [dict(r) for r in rows]
