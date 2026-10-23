"""
Structured Database Tools for Niyukti HRMS LangGraph Agents.
Provides deterministic, role-filtered access to employees, departments,
attendance records, leave balances, and payroll statistics matching the exact hrms.db schema.
"""

from __future__ import annotations

import logging
from typing import Any, Optional
import aiosqlite
from langchain_core.tools import tool

from backend.database.sqlite_db import get_db_connection

logger = logging.getLogger("hrms.agents.tools.db_tools")


@tool
async def get_all_employees(department: Optional[str] = None, status: str = "ACTIVE") -> list[dict[str, Any]]:
    """
    Fetches employee directory information including name, email, department, designation,
    status, and join date. Use this when asked to list employees, view staff directory,
    or count employees by status.
    """
    async with get_db_connection() as conn:
        query = """
            SELECT 
                e.id, e.employee_code, e.first_name, e.last_name, e.email,
                e.employment_status, e.employment_type, e.joining_date, e.location,
                d.name as department_name, des.name as designation_title
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            LEFT JOIN designations des ON e.designation_id = des.id
            WHERE 1=1
        """
        params: list[Any] = []
        if status and status.upper() != "ALL":
            query += " AND UPPER(e.employment_status) = ?"
            params.append(status.upper())
        if department:
            query += " AND (LOWER(d.name) LIKE ? OR LOWER(d.code) LIKE ?)"
            params.extend([f"%{department.lower()}%", f"%{department.lower()}%"])

        query += " ORDER BY e.employee_code ASC"
        cursor = await conn.execute(query, params)
        rows = await cursor.fetchall()

        # Also get the total count for this filter (not just the rows returned)
        count_query = "SELECT COUNT(*) as cnt FROM employees e LEFT JOIN departments d ON e.department_id = d.id WHERE 1=1"
        count_params: list[Any] = []
        if status and status.upper() != "ALL":
            count_query += " AND UPPER(e.employment_status) = ?"
            count_params.append(status.upper())
        if department:
            count_query += " AND (LOWER(d.name) LIKE ? OR LOWER(d.code) LIKE ?)"
            count_params.extend([f"%{department.lower()}%", f"%{department.lower()}%"])
        count_cursor = await conn.execute(count_query, count_params)
        count_row = await count_cursor.fetchone()
        total_count = count_row["cnt"] if count_row else len(rows)

        result = [
            {
                "employee_code": r["employee_code"],
                "name": f"{r['first_name']} {r['last_name']}".strip(),
                "email": r["email"],
                "department": r["department_name"] or "General",
                "designation": r["designation_title"] or "Staff Member",
                "status": r["employment_status"],
                "location": r["location"] or "Bangalore HQ",
                "joining_date": str(r["joining_date"]),
            }
            for r in rows
        ]
        # Prepend summary so agent always has the real total
        return [{"_summary": f"{total_count} employee(s) match the filter (showing all)", "_total_count": total_count}] + result


@tool
async def get_headcount_by_department() -> list[dict[str, Any]]:
    """
    Returns the headcount and employee breakdown across all departments.
    Use this when asked for department stats, team distribution, or organization size.
    """
    async with get_db_connection() as conn:
        query = """
            SELECT 
                COALESCE(d.name, 'Unassigned') as department,
                COUNT(*) as total_headcount,
                SUM(CASE WHEN UPPER(e.employment_status) = 'ACTIVE' THEN 1 ELSE 0 END) as active_count,
                SUM(CASE WHEN UPPER(e.employment_status) = 'INACTIVE' THEN 1 ELSE 0 END) as inactive_count
            FROM departments d
            LEFT JOIN employees e ON e.department_id = d.id
            GROUP BY d.id, d.name
            ORDER BY total_headcount DESC
        """
        cursor = await conn.execute(query)
        rows = await cursor.fetchall()
        return [
            {
                "department": r["department"],
                "total_headcount": r["total_headcount"],
                "active_count": r["active_count"],
                "inactive_count": r["inactive_count"],
            }
            for r in rows
        ]


@tool
async def get_employee_profile(identifier: str) -> dict[str, Any]:
    """
    Fetches full profile details for a specific employee by Employee Code (e.g. EMP-001)
    or email or ID.
    """
    async with get_db_connection() as conn:
        query = """
            SELECT 
                e.id, e.employee_code, e.first_name, e.last_name, e.email,
                e.phone, e.employment_status, e.employment_type, e.joining_date, e.location,
                d.name as department_name, des.name as designation_title
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            LEFT JOIN designations des ON e.designation_id = des.id
            WHERE LOWER(e.employee_code) = LOWER(?) 
               OR LOWER(e.email) = LOWER(?)
               OR e.id = ?
            LIMIT 1
        """
        cursor = await conn.execute(query, [identifier, identifier, identifier])
        row = await cursor.fetchone()
        if not row:
            return {"error": f"Employee '{identifier}' not found in records."}
        return {
            "employee_id": row["id"],
            "employee_code": row["employee_code"],
            "name": f"{row['first_name']} {row['last_name']}".strip(),
            "email": row["email"],
            "phone": row["phone"] or "N/A",
            "department": row["department_name"] or "General",
            "designation": row["designation_title"] or "Staff Member",
            "status": row["employment_status"],
            "location": row["location"] or "Bangalore HQ",
            "joining_date": str(row["joining_date"]),
        }


@tool
async def get_attendance_summary(date_str: Optional[str] = None) -> dict[str, Any]:
    """
    Retrieves aggregated daily attendance statistics (Present, Late, Absent, Half-Day).
    Use this when asked about today's attendance, who is working, or punctuality stats.
    """
    async with get_db_connection() as conn:
        cursor = await conn.execute("SELECT COUNT(*) as total FROM employees WHERE UPPER(employment_status) = 'ACTIVE'")
        total_emp = (await cursor.fetchone())["total"] or 1

        query = """
            SELECT status, COUNT(*) as count 
            FROM attendance_records 
            WHERE 1=1
        """
        params = []
        if date_str and date_str != "today":
            query += " AND date = ?"
            params.append(date_str)
        else:
            query += " AND date = date('now')"

        query += " GROUP BY status"
        cursor = await conn.execute(query, params)
        rows = await cursor.fetchall()
        breakdown = {r["status"]: r["count"] for r in rows}

        present = breakdown.get("PRESENT", 0) + breakdown.get("HALF_DAY", 0)
        on_leave = breakdown.get("ON_LEAVE", 0)
        absent = max(0, total_emp - present - on_leave)

        return {
            "date": date_str or "today",
            "total_employees": total_emp,
            "present_count": present,
            "absent_count": absent,
            "on_leave_count": on_leave,
            "attendance_rate_pct": round((present / total_emp) * 100, 1) if total_emp else 0,
            "status_breakdown": breakdown,
        }


@tool
async def get_leave_balances(employee_code: Optional[str] = None) -> list[dict[str, Any]]:
    """
    Retrieves leave requests and PTO records. If employee_code is provided, filters for that employee.
    Use this when asked about vacation days, sick leaves, or pending leave requests.
    """
    async with get_db_connection() as conn:
        query = """
            SELECT 
                lr.id, e.employee_code, e.first_name || ' ' || e.last_name as name,
                lt.name as leave_type, lr.start_date, lr.end_date, lr.days_count,
                lr.status, lr.reason
            FROM leave_requests lr
            JOIN employees e ON lr.employee_id = e.id
            LEFT JOIN leave_types lt ON lr.leave_type_id = lt.id
            WHERE 1=1
        """
        params = []
        if employee_code:
            query += " AND LOWER(e.employee_code) = LOWER(?)"
            params.append(employee_code)

        query += " ORDER BY lr.start_date DESC LIMIT 20"
        cursor = await conn.execute(query, params)
        rows = await cursor.fetchall()
        return [
            {
                "id": r["id"],
                "employee_code": r["employee_code"],
                "name": r["name"],
                "leave_type": r["leave_type"] or "Annual Leave",
                "dates": f"{r['start_date']} to {r['end_date']}",
                "days": r["days_count"],
                "status": r["status"],
                "reason": r["reason"] or "Personal leave",
            }
            for r in rows
        ]


@tool
async def get_payroll_summary() -> dict[str, Any]:
    """
    Calculates overall payroll expenses, latest payroll batch status, and salary disbursement metrics.
    RESTRICTED: Only callable for superadmin / executive role requests.
    """
    async with get_db_connection() as conn:
        cursor = await conn.execute(
            """
            SELECT 
                COUNT(*) as total_records,
                COALESCE(SUM(ctc_annual), 0) as total_annual_ctc,
                COALESCE(AVG(ctc_annual), 0) as avg_annual_ctc
            FROM employee_salary_records
            """
        )
        stats = await cursor.fetchone()

        cursor = await conn.execute(
            """
            SELECT id, period_id, status, total_gross, total_net, total_deductions, created_at
            FROM payroll_runs
            ORDER BY created_at DESC LIMIT 1
            """
        )
        latest_run = await cursor.fetchone()

        return {
            "active_payroll_records": stats["total_records"],
            "total_annual_payroll_inr": stats["total_annual_ctc"],
            "monthly_burn_rate_inr": round(stats["total_annual_ctc"] / 12, 2) if stats["total_annual_ctc"] else 0,
            "average_ctc_inr": round(stats["avg_annual_ctc"], 2),
            "latest_run": {
                "id": latest_run["id"] if latest_run else None,
                "status": latest_run["status"] if latest_run else "IDLE",
                "gross_pay": latest_run["total_gross"] if latest_run else 0,
                "net_pay": latest_run["total_net"] if latest_run else 0,
            } if latest_run else "No runs executed yet",
        }


# Export catalog of all tools


@tool
async def get_total_employee_count() -> dict[str, Any]:
    """
    Returns accurate total employee counts broken down by employment status.
    Use this when asked: 'how many employees do we have', 'total headcount', 'how many active employees',
    'employee count', 'staff count', 'how many staff'.
    Always use this tool first for any headcount/total count question to ensure accuracy.
    """
    async with get_db_connection() as conn:
        cursor = await conn.execute(
            """
            SELECT 
                employment_status,
                COUNT(*) as count
            FROM employees
            GROUP BY employment_status
            """
        )
        rows = await cursor.fetchall()
        breakdown = {r["employment_status"]: r["count"] for r in rows}
        total = sum(breakdown.values())

        cursor2 = await conn.execute("SELECT COUNT(DISTINCT department_id) as dept_count FROM employees WHERE UPPER(employment_status) = 'ACTIVE'")
        dept_row = await cursor2.fetchone()

        return {
            "total_employees": total,
            "active": breakdown.get("ACTIVE", breakdown.get("active", 0)),
            "inactive": breakdown.get("INACTIVE", breakdown.get("inactive", 0)),
            "on_leave": breakdown.get("ON_LEAVE", breakdown.get("on_leave", 0)),
            "terminated": breakdown.get("TERMINATED", breakdown.get("terminated", 0)),
            "other_statuses": {k: v for k, v in breakdown.items() if k.upper() not in ("ACTIVE", "INACTIVE", "ON_LEAVE", "TERMINATED")},
            "active_departments_count": dept_row["dept_count"] if dept_row else 0,
        }


ALL_DB_TOOLS = [
    get_all_employees,
    get_headcount_by_department,
    get_employee_profile,
    get_attendance_summary,
    get_leave_balances,
    get_payroll_summary,
    get_total_employee_count,
]

