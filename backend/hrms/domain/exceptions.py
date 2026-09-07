"""
HRMS Domain Exceptions.

Structured hierarchy of domain and application errors.
Prevents internal stack traces from leaking through API responses.
"""

from __future__ import annotations


class HRMSException(Exception):
    """Base exception for all HRMS errors."""

    def __init__(self, message: str, code: str = "HRMS_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class OrganizationNotFound(HRMSException):
    def __init__(self, organization_id: str):
        super().__init__(
            f"Organization with ID '{organization_id}' not found.",
            code="ORGANIZATION_NOT_FOUND",
        )


class DepartmentNotFound(HRMSException):
    def __init__(self, department_id: str):
        super().__init__(
            f"Department with ID '{department_id}' not found.",
            code="DEPARTMENT_NOT_FOUND",
        )


class DesignationNotFound(HRMSException):
    def __init__(self, designation_id: str):
        super().__init__(
            f"Designation with ID '{designation_id}' not found.",
            code="DESIGNATION_NOT_FOUND",
        )


class EmployeeNotFound(HRMSException):
    def __init__(self, employee_id: str):
        super().__init__(
            f"Employee with ID '{employee_id}' not found.",
            code="EMPLOYEE_NOT_FOUND",
        )


class DuplicateEmployeeCode(HRMSException):
    def __init__(self, employee_code: str, organization_id: str):
        super().__init__(
            f"Employee code '{employee_code}' already exists in organization '{organization_id}'.",
            code="DUPLICATE_EMPLOYEE_CODE",
        )


class InvalidTenant(HRMSException):
    def __init__(self, message: str = "Invalid or missing tenant context."):
        super().__init__(message, code="INVALID_TENANT")


class CrossTenantViolation(HRMSException):
    def __init__(self, entity_type: str, entity_id: str, tenant_id: str):
        super().__init__(
            f"Cross-tenant access violation: {entity_type} '{entity_id}' does not belong to tenant '{tenant_id}'.",
            code="CROSS_TENANT_VIOLATION",
        )


class UnauthorizedAction(HRMSException):
    def __init__(self, actor_id: str, action: str):
        super().__init__(
            f"Actor '{actor_id}' is not authorized to perform action '{action}'.",
            code="UNAUTHORIZED_ACTION",
        )


class ForbiddenAction(HRMSException):
    def __init__(self, reason: str):
        super().__init__(reason, code="FORBIDDEN_ACTION")


class InvalidEmployeeState(HRMSException):
    def __init__(self, current_status: str, target_status: str):
        super().__init__(
            f"Invalid employee status transition from '{current_status}' to '{target_status}'.",
            code="INVALID_EMPLOYEE_STATE",
        )


class InvalidSkill(HRMSException):
    def __init__(self, skill_id: str):
        super().__init__(
            f"Skill with ID '{skill_id}' is invalid or inactive.",
            code="INVALID_SKILL",
        )


class DocumentNotFound(HRMSException):
    def __init__(self, document_id: str):
        super().__init__(
            f"Document with ID '{document_id}' not found.",
            code="DOCUMENT_NOT_FOUND",
        )


class DocumentValidationError(HRMSException):
    def __init__(self, message: str):
        super().__init__(message, code="DOCUMENT_VALIDATION_ERROR")
