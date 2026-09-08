"""
Unified 18-Employee HRMS Database Seeder & Normalizer.
Synchronizes all 18 employees under org-nova-01 across 8 departments,
with realistic designations, salary structures, payslips, attendance punches, and leave requests.
"""

import sqlite3
import datetime
import json
import uuid

DB_PATH = "hrms.db"

ALL_18_EMPLOYEES = [
    {
        "id": "emp-001",
        "employee_code": "EMP-001",
        "first_name": "Vikram",
        "last_name": "Aditya",
        "email": "vikram.aditya@novadigital.demo",
        "phone": "+91 98111 00001",
        "department_id": "dept-exec",
        "designation_id": "desg-ceo",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2020-01-15",
        "location": "Bangalore HQ",
        "ctc": 6500000.0,
    },
    {
        "id": "emp-002",
        "employee_code": "EMP-002",
        "first_name": "Elena",
        "last_name": "Rostova",
        "email": "elena.rostova@novadigital.demo",
        "phone": "+91 98111 00002",
        "department_id": "dept-ai",
        "designation_id": "desg-cto",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2020-03-01",
        "location": "Bangalore HQ",
        "ctc": 5200000.0,
    },
    {
        "id": "emp-003",
        "employee_code": "EMP-003",
        "first_name": "Rachel",
        "last_name": "Green",
        "email": "rachel.green@novadigital.demo",
        "phone": "+91 98111 00003",
        "department_id": "dept-pm",
        "designation_id": "desg-pm",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2021-06-15",
        "location": "Bangalore HQ",
        "ctc": 3800000.0,
    },
    {
        "id": "emp-004",
        "employee_code": "EMP-004",
        "first_name": "Alex",
        "last_name": "Rivera",
        "email": "alex.rivera@novadigital.demo",
        "phone": "+91 98111 00004",
        "department_id": "dept-eng",
        "designation_id": "desg-tl",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2021-08-01",
        "location": "Bangalore HQ",
        "ctc": 3500000.0,
    },
    {
        "id": "emp-005",
        "employee_code": "EMP-005",
        "first_name": "Priya",
        "last_name": "Sharma",
        "email": "priya.sharma@novadigital.demo",
        "phone": "+91 98111 00005",
        "department_id": "dept-eng",
        "designation_id": "desg-sde3",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2022-01-10",
        "location": "Bangalore HQ",
        "ctc": 2600000.0,
    },
    {
        "id": "emp-006",
        "employee_code": "EMP-006",
        "first_name": "Marcus",
        "last_name": "Vance",
        "email": "marcus.vance@novadigital.demo",
        "phone": "+91 98111 00006",
        "department_id": "dept-ai",
        "designation_id": "desg-sde3",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2022-04-18",
        "location": "Bangalore HQ",
        "ctc": 2700000.0,
    },
    {
        "id": "emp-007",
        "employee_code": "EMP-007",
        "first_name": "Sophia",
        "last_name": "Lin",
        "email": "sophia.lin@novadigital.demo",
        "phone": "+91 98111 00007",
        "department_id": "dept-pm",
        "designation_id": "desg-design",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2022-07-01",
        "location": "Bangalore HQ",
        "ctc": 2400000.0,
    },
    {
        "id": "emp-008",
        "employee_code": "EMP-008",
        "first_name": "Daniel",
        "last_name": "Kim",
        "email": "daniel.kim@novadigital.demo",
        "phone": "+91 98111 00008",
        "department_id": "dept-qa",
        "designation_id": "desg-qa",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2022-09-15",
        "location": "Mumbai Branch",
        "ctc": 2300000.0,
    },
    {
        "id": "emp-009",
        "employee_code": "EMP-009",
        "first_name": "James",
        "last_name": "Wilson",
        "email": "james.wilson@novadigital.demo",
        "phone": "+91 98111 00009",
        "department_id": "dept-sales",
        "designation_id": "desg-sales",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2022-10-01",
        "location": "Delhi NCR",
        "ctc": 2900000.0,
    },
    {
        "id": "emp-010",
        "employee_code": "EMP-010",
        "first_name": "Sarah",
        "last_name": "Jenkins",
        "email": "sarah.jenkins@novadigital.demo",
        "phone": "+91 98111 00010",
        "department_id": "dept-hr",
        "designation_id": "desg-[#hr]",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2021-03-15",
        "location": "Bangalore HQ",
        "ctc": 2200000.0,
    },
    {
        "id": "emp-011",
        "employee_code": "EMP-011",
        "first_name": "Robert",
        "last_name": "Taylor",
        "email": "robert.taylor@novadigital.demo",
        "phone": "+91 98111 00011",
        "department_id": "dept-fin",
        "designation_id": "desg-fin",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2021-05-20",
        "location": "Bangalore HQ",
        "ctc": 3100000.0,
    },
    {
        "id": "emp-012",
        "employee_code": "EMP-012",
        "first_name": "Deepak",
        "last_name": "Verma",
        "email": "deepak.verma@novadigital.demo",
        "phone": "+91 98111 00012",
        "department_id": "dept-ai",
        "designation_id": "desg-sde3",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2023-04-10",
        "location": "Bangalore HQ",
        "ctc": 2800000.0,
    },
    {
        "id": "emp-013",
        "employee_code": "EMP-013",
        "first_name": "Ananya",
        "last_name": "Roy",
        "email": "ananya.roy@novadigital.demo",
        "phone": "+91 98111 00013",
        "department_id": "dept-eng",
        "designation_id": "desg-sde2",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2023-08-01",
        "location": "Bangalore HQ",
        "ctc": 2200000.0,
    },
    {
        "id": "emp-014",
        "employee_code": "EMP-014",
        "first_name": "Rohan",
        "last_name": "Mehta",
        "email": "rohan.mehta@novadigital.demo",
        "phone": "+91 98111 00014",
        "department_id": "dept-qa",
        "designation_id": "desg-sde2",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2022-11-15",
        "location": "Mumbai Branch",
        "ctc": 1950000.0,
    },
    {
        "id": "emp-015",
        "employee_code": "EMP-015",
        "first_name": "Aditi",
        "last_name": "Sharma",
        "email": "aditi.sharma@novadigital.demo",
        "phone": "+91 98111 00015",
        "department_id": "dept-hr",
        "designation_id": "desg-[#hr]",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2023-01-09",
        "location": "Bangalore HQ",
        "ctc": 1800000.0,
    },
    {
        "id": "emp-016",
        "employee_code": "EMP-016",
        "first_name": "Kavita",
        "last_name": "Nair",
        "email": "kavita.nair@novadigital.demo",
        "phone": "+91 98111 00016",
        "department_id": "dept-sales",
        "designation_id": "desg-sales",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2022-09-20",
        "location": "Delhi NCR",
        "ctc": 3200000.0,
    },
    {
        "id": "emp-017",
        "employee_code": "EMP-017",
        "first_name": "Arjun",
        "last_name": "Menon",
        "email": "arjun.menon@novadigital.demo",
        "phone": "+91 98111 00017",
        "department_id": "dept-sales",
        "designation_id": "desg-sales",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2023-06-12",
        "location": "Delhi NCR",
        "ctc": 1600000.0,
    },
    {
        "id": "emp-018",
        "employee_code": "EMP-018",
        "first_name": "Sunita",
        "last_name": "Rao",
        "email": "sunita.rao@novadigital.demo",
        "phone": "+91 98111 00018",
        "department_id": "dept-pm",
        "designation_id": "desg-design",
        "employment_status": "ACTIVE",
        "employment_type": "FULL_TIME",
        "joining_date": "2023-03-01",
        "location": "Bangalore HQ",
        "ctc": 2400000.0,
    },
]

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    org_id = "org-nova-01"
    today_dt = datetime.date.today()
    today = today_dt.isoformat()

    # Ensure Organization exists
    cur.execute("""
        INSERT OR REPLACE INTO organizations (id, legal_name, display_name, slug, industry, country, timezone, currency, status, employee_count, settings, created_at, updated_at)
        VALUES ('org-nova-01', 'Nova Digital Technologies Inc.', 'Nova HRMS', 'nova-digital', 'AI & Cloud Software', 'IN', 'Asia/Kolkata', 'INR', 'ACTIVE', 18, '{}', datetime('now'), datetime('now'))
    """)

    # Seed all 18 employees cleanly
    for emp in ALL_18_EMPLOYEES:
        cur.execute(
            """
            INSERT OR REPLACE INTO employees (
                id, organization_id, employee_code, first_name, last_name, preferred_name,
                email, phone, department_id, designation_id, employment_status, employment_type,
                joining_date, location, timezone, metadata_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Asia/Kolkata', '{}', datetime('now'), datetime('now'))
            """,
            (
                emp["id"], org_id, emp["employee_code"], emp["first_name"], emp["last_name"],
                emp["first_name"], emp["email"], emp["phone"], emp["department_id"], emp["designation_id"],
                emp["employment_status"], emp["employment_type"], emp["joining_date"],
                emp["location"]
            )
        )

        # Salary Structure Record
        cur.execute(
            """
            INSERT OR REPLACE INTO employee_salary_records (
                id, organization_id, employee_id, salary_structure_id, ctc_annual, base_monthly,
                effective_from, status, created_at, updated_at
            ) VALUES (?, ?, ?, 'struct-standard', ?, ?, ?, 'ACTIVE', datetime('now'), datetime('now'))
            """,
            (f"sal-{emp['id']}", org_id, emp["id"], emp["ctc"], round(emp["ctc"] / 12, 2), emp["joining_date"])
        )

        # Seed attendance for the last 7 working days
        for day_offset in range(7):
            past_date = (today_dt - datetime.timedelta(days=day_offset)).isoformat()
            cur.execute(
                """
                INSERT OR REPLACE INTO attendance_records (
                    id, organization_id, employee_id, date, check_in, check_out,
                    status, source, overtime_hours, created_at, updated_at
                ) VALUES (?, ?, ?, ?, '09:15:00', '18:30:00', 'PRESENT', 'WEB', 0.0, datetime('now'), datetime('now'))
                """,
                (f"att-{emp['id']}-{past_date}", org_id, emp["id"], past_date)
            )

        # Seed monthly Payslip
        monthly_gross = round(emp["ctc"] / 12, 2)
        monthly_deductions = round(monthly_gross * 0.15, 2)
        monthly_net = round(monthly_gross - monthly_deductions, 2)
        cur.execute(
            """
            INSERT OR REPLACE INTO payslips (
                id, organization_id, run_id, employee_id, gross_pay, total_deductions, net_pay,
                days_worked, days_absent, overtime_hours, overtime_pay, status, created_at, updated_at
            ) VALUES (?, ?, 'payrun-aug-2026', ?, ?, ?, ?, 22.0, 0.0, 0.0, 0.0, 'PAID', datetime('now'), datetime('now'))
            """,
            (f"slip-{emp['id']}-2026-08", org_id, emp["id"], monthly_gross, monthly_deductions, monthly_net)
        )

    # Seed standard Leave Requests
    leave_data = [
        ("lr-001", "emp-005", "2026-09-18", "2026-09-20", 3.0, "Family function", "APPROVED"),
        ("lr-002", "emp-006", "2026-09-25", "2026-09-26", 2.0, "Personal leave", "APPROVED"),
        ("lr-003", "emp-013", "2026-10-02", "2026-10-05", 4.0, "Vacation travel", "PENDING"),
        ("lr-004", "emp-018", "2026-10-10", "2026-10-12", 3.0, "Medical appointment", "PENDING"),
    ]
    cur.execute("SELECT id FROM leave_types LIMIT 1")
    lt_row = cur.fetchone()
    lt_id = lt_row[0] if lt_row else "lt-annual"

    for lr in leave_data:
        cur.execute(
            """
            INSERT OR REPLACE INTO leave_requests (
                id, organization_id, employee_id, leave_type_id, start_date, end_date,
                days_count, is_half_day, reason, status, applied_on, documents_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, date('now'), '[]', datetime('now'), datetime('now'))
            """,
            (lr[0], org_id, lr[1], lt_id, lr[2], lr[3], lr[4], lr[5], lr[6])
        )

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM employees WHERE organization_id = 'org-nova-01'")
    total_emp = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM employee_salary_records WHERE organization_id = 'org-nova-01'")
    total_sal = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM payslips WHERE organization_id = 'org-nova-01'")
    total_slips = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM attendance_records WHERE organization_id = 'org-nova-01'")
    total_att = cur.fetchone()[0]
    conn.close()

    print(f"[SUCCESS] Normalization Complete!")
    print(f"  - Active Employees under org-nova-01 : {total_emp}")
    print(f"  - Salary Records                     : {total_sal}")
    print(f"  - Payslips                           : {total_slips}")
    print(f"  - Attendance Records                 : {total_att}")

if __name__ == "__main__":
    seed_database()
