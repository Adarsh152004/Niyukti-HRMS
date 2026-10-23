"""
API v1 Tests — End-to-End API Router Verification.

Verifies FastAPI HTTP endpoints, header-based TenantContext resolution,
standard API envelope responses, and error handlers.
"""

from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_platform_status_endpoint():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert "Node" in data["node"]
    assert "AI-Powered Intelligent HRMS" in data["domain"]


def test_create_organization_api():
    headers = {
        "X-Tenant-ID": "tenant-test-org",
        "X-Actor-ID": "admin-user",
        "X-Actor-Permissions": "ALL_PERMISSIONS",
    }
    payload = {
        "legal_name": "Test Org Pvt Ltd",
        "display_name": "Test Org",
        "slug": "test-org",
        "industry": "Software",
        "country": "IN",
        "timezone": "Asia/Kolkata",
        "currency": "INR",
    }
    response = client.post("/api/v1/organizations", json=payload, headers=headers)
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True
    assert res["data"]["slug"] == "test-org"
    assert "request_id" in res
    assert "timestamp" in res


def test_create_department_and_employee_api():
    headers = {
        "X-Tenant-ID": "tenant-api-flow",
        "X-Actor-ID": "admin-flow",
        "X-Actor-Permissions": "ALL_PERMISSIONS",
    }

    # 1. Create Department
    dept_res = client.post(
        "/api/v1/departments",
        json={"name": "Quality Assurance", "code": "QA"},
        headers=headers,
    )
    assert dept_res.status_code == 201
    dept_id = dept_res.json()["data"]["department_id"]

    # 2. Create Designation
    des_res = client.post(
        "/api/v1/designations",
        json={"name": "QA Analyst", "code": "QA-1", "department_id": dept_id},
        headers=headers,
    )
    assert des_res.status_code == 201
    des_id = des_res.json()["data"]["designation_id"]

    # 3. Create Employee
    emp_payload = {
        "employee_code": "EMP-QA01",
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@apiflow.com",
        "department_id": dept_id,
        "designation_id": des_id,
        "joining_date": "2024-01-01",
    }
    emp_res = client.post("/api/v1/employees", json=emp_payload, headers=headers)
    assert emp_res.status_code == 201
    emp_data = emp_res.json()["data"]
    assert emp_data["employee_code"] == "EMP-QA01"
    assert emp_data["first_name"] == "Test"

    # 4. Get Employee by ID
    get_res = client.get(f"/api/v1/employees/{emp_data['employee_id']}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["email"] == "test.user@apiflow.com"


def test_cross_tenant_api_isolation_error():
    """Verify that accessing non-existent or cross-tenant resource returns error response."""
    headers_org_b = {
        "X-Tenant-ID": "tenant-org-B",
        "X-Actor-ID": "admin-B",
        "X-Actor-Permissions": "ALL_PERMISSIONS",
    }
    response = client.get("/api/v1/employees/non-existent-id", headers=headers_org_b)
    assert response.status_code == 404
    res = response.json()
    assert res["success"] is False
    assert res["error"]["code"] == "EMPLOYEE_NOT_FOUND"
