"""Tests — PII Classification."""

from backend.security.pii import (
    HRMS_PII_FIELDS,
    PIIClassification,
    PIIField,
    get_pii_fields_for_model,
    mask_value,
)


def test_pii_classification_count():
    assert len(PIIClassification) == 5


def test_pii_classification_values():
    assert PIIClassification.PUBLIC == "PUBLIC"
    assert PIIClassification.INTERNAL == "INTERNAL"
    assert PIIClassification.CONFIDENTIAL == "CONFIDENTIAL"
    assert PIIClassification.SENSITIVE == "SENSITIVE"
    assert PIIClassification.HIGHLY_SENSITIVE == "HIGHLY_SENSITIVE"
    assert PIIClassification.RESTRICTED == "HIGHLY_SENSITIVE"


def test_encryption_at_rest():
    assert not PIIClassification.PUBLIC.requires_encryption_at_rest
    assert not PIIClassification.CONFIDENTIAL.requires_encryption_at_rest
    assert PIIClassification.SENSITIVE.requires_encryption_at_rest
    assert PIIClassification.HIGHLY_SENSITIVE.requires_encryption_at_rest


def test_mask_in_logs():
    assert not PIIClassification.PUBLIC.mask_in_logs
    assert not PIIClassification.INTERNAL.mask_in_logs
    assert PIIClassification.CONFIDENTIAL.mask_in_logs
    assert PIIClassification.SENSITIVE.mask_in_logs
    assert PIIClassification.HIGHLY_SENSITIVE.mask_in_logs


def test_ai_agent_access():
    """AI agents must not access CONFIDENTIAL+ fields without explicit grant."""
    assert PIIClassification.PUBLIC.ai_agent_access_allowed
    assert PIIClassification.INTERNAL.ai_agent_access_allowed
    assert not PIIClassification.CONFIDENTIAL.ai_agent_access_allowed
    assert not PIIClassification.SENSITIVE.ai_agent_access_allowed
    assert not PIIClassification.HIGHLY_SENSITIVE.ai_agent_access_allowed


def test_pii_fields_registry_not_empty():
    assert len(HRMS_PII_FIELDS) > 0


def test_employee_pii_fields_exist():
    employee_fields = get_pii_fields_for_model("Employee")
    assert len(employee_fields) > 0
    field_names = [f.field_name for f in employee_fields]
    assert "email" in field_names
    assert "national_id" in field_names


def test_salary_is_highly_sensitive():
    payroll_fields = get_pii_fields_for_model("PayrollRecord")
    for f in payroll_fields:
        assert f.classification == PIIClassification.HIGHLY_SENSITIVE


def test_national_id_is_restricted_and_encrypted():
    employee_fields = get_pii_fields_for_model("Employee")
    national_id = next(f for f in employee_fields if f.field_name == "national_id")
    assert national_id.classification == PIIClassification.HIGHLY_SENSITIVE
    assert national_id.encrypt_at_rest is True


def test_mask_value_confidential():
    field = PIIField(
        field_name="email",
        model_name="Employee",
        classification=PIIClassification.CONFIDENTIAL,
        mask_pattern="***@***.***",
    )
    masked = mask_value("john.doe@company.com", field)
    assert "john.doe" not in masked
    assert masked == "***@***.***"


def test_mask_value_public_not_masked():
    field = PIIField(
        field_name="job_title",
        model_name="Employee",
        classification=PIIClassification.PUBLIC,
    )
    original = "Senior Engineer"
    assert mask_value(original, field) == original
