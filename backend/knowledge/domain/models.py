"""
Knowledge Domain Models — Entities for documents, versions, chunks, access policies, and RAG answers.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.knowledge.domain.enums import (
    AccessScopeType,
    DocumentStatus,
    DocumentType,
    IndexStatus,
    KnowledgeClassification,
    SourceType,
)


class KnowledgeDocument(BaseModel):
    """Primary metadata entity for an ingested HR document."""

    document_id: str = Field(default_factory=lambda: f"doc-{uuid.uuid4()}")
    organization_id: str = Field(description="Tenant isolation boundary")
    title: str
    description: str = Field(default="")
    source_type: SourceType = Field(default=SourceType.HR_POLICY)
    document_type: DocumentType = Field(default=DocumentType.POLICY)
    classification: KnowledgeClassification = Field(default=KnowledgeClassification.INTERNAL)
    owner_id: str = Field(description="Actor ID of uploader / owner")
    status: DocumentStatus = Field(default=DocumentStatus.UPLOADED)
    current_version: int = Field(default=1, ge=1)
    checksum: str = Field(description="SHA-256 hash of latest binary content")
    mime_type: str = Field(default="text/plain")
    storage_reference: str = Field(description="URI or key in object storage")
    language: str = Field(default="en")
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    published_at: datetime | None = None
    effective_at: datetime | None = None
    expires_at: datetime | None = None
    archived_at: datetime | None = None


class KnowledgeDocumentVersion(BaseModel):
    """Immutable snapshot of a specific document version."""

    version_id: str = Field(default_factory=lambda: f"docver-{uuid.uuid4()}")
    document_id: str
    organization_id: str
    version_number: int = Field(ge=1)
    checksum: str
    storage_reference: str
    author_id: str
    change_summary: str = Field(default="")
    status: DocumentStatus = Field(default=DocumentStatus.PROCESSING)
    effective_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    expires_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class KnowledgeChunk(BaseModel):
    """Discrete text segment extracted and indexed for vector search."""

    chunk_id: str = Field(default_factory=lambda: f"chk-{uuid.uuid4()}")
    document_id: str
    document_version: int = Field(ge=1)
    organization_id: str
    chunk_index: int = Field(ge=0)
    content: str = Field(description="Extracted text chunk content")
    token_count: int = Field(ge=0, default=0)
    char_length: int = Field(ge=0, default=0)
    section_title: str | None = None
    page_number: int | None = None
    classification: KnowledgeClassification = Field(default=KnowledgeClassification.INTERNAL)
    embedding: list[float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class KnowledgeAccessPolicy(BaseModel):
    """Fine-grained authorization policy controlling who/what can retrieve document chunks."""

    policy_id: str = Field(default_factory=lambda: f"kap-{uuid.uuid4()}")
    document_id: str
    organization_id: str
    scope_type: AccessScopeType = Field(default=AccessScopeType.ALL_EMPLOYEES)
    allowed_roles: list[str] = Field(default_factory=list)
    allowed_departments: list[str] = Field(default_factory=list)
    allowed_capabilities: list[str] = Field(default_factory=list)
    allowed_employee_ids: list[str] = Field(default_factory=list)
    max_classification: KnowledgeClassification = Field(default=KnowledgeClassification.INTERNAL)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class KnowledgeIndexRecord(BaseModel):
    """Synchronization status between document version and vector database."""

    index_id: str = Field(default_factory=lambda: f"idx-{uuid.uuid4()}")
    document_id: str
    version_number: int
    organization_id: str
    chunk_count: int = Field(ge=0, default=0)
    status: IndexStatus = Field(default=IndexStatus.PENDING)
    last_indexed_at: datetime | None = None
    error_message: str | None = None


class KnowledgeRetrievalQuery(BaseModel):
    """Contextual retrieval query container."""

    query_text: str
    organization_id: str
    actor_id: str
    actor_roles: list[str] = Field(default_factory=list)
    actor_department_id: str | None = None
    agent_id: str | None = None
    agent_capabilities: list[str] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=50)
    min_similarity_score: float = Field(default=0.60, ge=0.0, le=1.0)
    include_historical: bool = Field(default=False)
    filter_document_types: list[DocumentType] | None = None


class KnowledgeRetrievedChunk(BaseModel):
    """Retrieved chunk matching similarity and authorization filters."""

    chunk: KnowledgeChunk
    similarity_score: float = Field(ge=0.0, le=1.0)
    document_title: str
    source_type: SourceType


class CitationReference(BaseModel):
    """Grounded reference supporting an AI response."""

    citation_id: str = Field(default_factory=lambda: f"cit-{uuid.uuid4()}")
    document_id: str
    document_version: int
    document_title: str
    section_title: str | None = None
    page_number: int | None = None
    chunk_id: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    snippet: str = Field(description="Exerpt snippet from verified source chunk")


class KnowledgeAnswer(BaseModel):
    """Structured response to a knowledge inquiry."""

    answer: str
    citations: list[CitationReference] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    abstain: bool = Field(default=False, description="True if evidence is insufficient or unauthorized")
    abstain_reason: str | None = None
    retrieved_source_count: int = Field(ge=0, default=0)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class KnowledgeQualityReport(BaseModel):
    """Aggregate health and quality metrics for knowledge base."""

    organization_id: str
    quality_score: float = Field(ge=0.0, le=100.0)
    total_documents: int
    published_documents: int
    expired_documents: int
    stale_documents: int
    failed_ingestions: int
    broken_citations_detected: int
    unauthorized_retrieval_rate: float = Field(default=0.0)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
