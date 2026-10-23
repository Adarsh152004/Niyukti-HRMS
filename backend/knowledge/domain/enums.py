"""
Knowledge Domain Enums — Document statuses, classification taxonomies, and access scopes.
"""

from __future__ import annotations

from enum import StrEnum


class DocumentStatus(StrEnum):
    """Lifecycle status of a knowledge document."""

    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    INDEXED = "INDEXED"
    PUBLISHED = "PUBLISHED"
    EXPIRED = "EXPIRED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"
    FAILED = "FAILED"


class KnowledgeClassification(StrEnum):
    """
    Knowledge access classification levels.
    Extends PII taxonomy with corporate governance authorization scopes.
    """

    # Base PII compatibility
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    SENSITIVE = "SENSITIVE"
    HIGHLY_SENSITIVE = "HIGHLY_SENSITIVE"

    # HR & Role Scopes
    EMPLOYEE_PRIVATE = "EMPLOYEE_PRIVATE"
    HR_ONLY = "HR_ONLY"
    MANAGER_ONLY = "MANAGER_ONLY"
    EXECUTIVE_ONLY = "EXECUTIVE_ONLY"
    SYSTEM_ONLY = "SYSTEM_ONLY"


class SourceType(StrEnum):
    """Source provenance category for ingested documents."""

    HR_POLICY = "HR_POLICY"
    EMPLOYEE_HANDBOOK = "EMPLOYEE_HANDBOOK"
    BENEFITS_GUIDE = "BENEFITS_GUIDE"
    SOP = "SOP"
    TRAINING_MATERIAL = "TRAINING_MATERIAL"
    JOB_DESCRIPTION = "JOB_DESCRIPTION"
    COMPLIANCE_DOC = "COMPLIANCE_DOC"
    ORGANIZATIONAL_DOC = "ORGANIZATIONAL_DOC"


class DocumentType(StrEnum):
    """Document functional format type."""

    POLICY = "POLICY"
    HANDBOOK = "HANDBOOK"
    BENEFIT = "BENEFIT"
    SOP = "SOP"
    TRAINING = "TRAINING"
    JOB_POSTING = "JOB_POSTING"
    LEGAL = "LEGAL"
    CONTRACT = "CONTRACT"


class AccessScopeType(StrEnum):
    """Authorization access scope rule types."""

    ALL_EMPLOYEES = "ALL_EMPLOYEES"
    DEPARTMENT_ONLY = "DEPARTMENT_ONLY"
    ROLE_BASED = "ROLE_BASED"
    MANAGER_AND_ABOVE = "MANAGER_AND_ABOVE"
    EXECUTIVE_ONLY = "EXECUTIVE_ONLY"
    INDIVIDUAL_EMPLOYEE = "INDIVIDUAL_EMPLOYEE"
    AGENT_CAPABILITY = "AGENT_CAPABILITY"


class IndexStatus(StrEnum):
    """Vector index synchronization status."""

    PENDING = "PENDING"
    INDEXING = "INDEXING"
    INDEXED = "INDEXED"
    REINDEX_REQUIRED = "REINDEX_REQUIRED"
    FAILED = "FAILED"
    PURGED = "PURGED"
