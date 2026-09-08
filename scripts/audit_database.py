import sqlite3
import os

db_path = "hrms.db" if os.path.exists("hrms.db") else "backend/hrms.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

tables = [row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"Database: {db_path}")
print("========================================")
for t in tables:
    try:
        cnt = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:30s}: {cnt:4d} rows")
    except Exception as e:
        print(f"  {t:30s}: error {e}")

print("========================================")
print("\nActive Employees in DB:")
employees = c.execute("""
    SELECT e.id, e.employee_code, e.first_name, e.last_name, e.email, e.employment_status,
           d.name as department, dg.name as designation, e.location
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.id
    LEFT JOIN designations dg ON e.designation_id = dg.id
    ORDER BY e.employee_code
""").fetchall()
for emp in employees:
    print(f"  [{emp['employee_code']}] {emp['first_name']} {emp['last_name']:15s} | Dept: {str(emp['department']):22s} | Role: {str(emp['designation']):25s} | Status: {emp['employment_status']}")

print(f"\nTotal Employees: {len(employees)}")

print("\nDepartment breakdown:")
depts = c.execute("""
    SELECT d.name, COUNT(e.id) as cnt
    FROM departments d
    LEFT JOIN employees e ON d.id = e.department_id
    GROUP BY d.name
""").fetchall()
for d in depts:
    print(f"  - {d['name']:25s}: {d['cnt']} employees")

conn.close()
