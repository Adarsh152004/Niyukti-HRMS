import urllib.request
import json
import sqlite3

def test_endpoint(name, url, headers=None):
    headers = headers or {}
    try:
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode())
        count = len(data) if isinstance(data, list) else len(data.get("data", data.get("items", data.get("employees", []))))
        print(f"[SUCCESS] {name:30s} -> Status {res.status} | Count: {count}")
        return data
    except Exception as e:
        print(f"[ERROR]   {name:30s} -> {e}")
        return None

print("Testing Backend APIs:")
print("==================================================")
test_endpoint("Health", "http://localhost:8000/health")
emp_data = test_endpoint("Employees List", "http://localhost:8000/api/v1/employees/", {"X-Tenant-ID": "org-nova-01"})
test_endpoint("Departments", "http://localhost:8000/api/v1/departments", {"X-Tenant-ID": "org-nova-01"})
test_endpoint("Designations", "http://localhost:8000/api/v1/designations", {"X-Tenant-ID": "org-nova-01"})
test_endpoint("Attendance Stats", "http://localhost:8000/api/v1/attendance/stats", {"X-Tenant-ID": "org-nova-01"})
test_endpoint("Leave Requests", "http://localhost:8000/api/v1/leave/requests", {"X-Tenant-ID": "org-nova-01"})
test_endpoint("Payroll Runs", "http://localhost:8000/api/v1/payroll/runs", {"X-Tenant-ID": "org-nova-01"})
test_endpoint("Orchestration History", "http://localhost:8000/api/v1/orchestration/history")
test_endpoint("Me (EMP-001)", "http://localhost:8000/api/v1/me", {"X-Actor-ID": "emp-001", "X-Tenant-ID": "org-nova-01"})
test_endpoint("Me Attendance (EMP-001)", "http://localhost:8000/api/v1/me/attendance", {"X-Actor-ID": "emp-001", "X-Tenant-ID": "org-nova-01"})
test_endpoint("Me Leave (EMP-001)", "http://localhost:8000/api/v1/me/leave", {"X-Actor-ID": "emp-001", "X-Tenant-ID": "org-nova-01"})
test_endpoint("Me Payslips (EMP-001)", "http://localhost:8000/api/v1/me/payslips", {"X-Actor-ID": "emp-001", "X-Tenant-ID": "org-nova-01"})
print("==================================================")
