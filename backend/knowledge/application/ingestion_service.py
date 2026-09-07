"""
Document Ingestion Service — Manages the full upload, extraction, indexing, and publication pipeline.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime

from backend.knowledge.application.indexing_service import KnowledgeIndexingService
from backend.knowledge.domain.enums import (
    DocumentStatus,
    DocumentType,
    KnowledgeClassification,
    SourceType,
)
from backend.knowledge.domain.exceptions import KnowledgeIngestionError
from backend.knowledge.domain.models import (
    KnowledgeAccessPolicy,
    KnowledgeDocument,
    KnowledgeDocumentVersion,
)
from backend.knowledge.ports.document_parser import DocumentParserPort
from backend.knowledge.ports.repositories import (
    KnowledgeAccessPolicyRepositoryPort,
    KnowledgeDocumentRepositoryPort,
)
from backend.runtime.events import EventBus

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    """Orchestrates document ingestion, versioning, indexing, and publication."""

    def __init__(
        self,
        document_repo: KnowledgeDocumentRepositoryPort,
        policy_repo: KnowledgeAccessPolicyRepositoryPort,
        indexing_service: KnowledgeIndexingService,
        parsers: list[DocumentParserPort],
        event_bus: EventBus | None = None,
    ) -> None:
        self.document_repo = document_repo
        self.policy_repo = policy_repo
        self.indexing_service = indexing_service
        self.parsers = parsers
        self.event_bus = event_bus or EventBus.get_instance()

    def get_parser_for_mime_type(self, mime_type: str) -> DocumentParserPort:
        """Find matching parser for MIME type."""
        for p in self.parsers:
            if p.supports_mime_type(mime_type):
                return p
        raise KnowledgeIngestionError(f"No registered parser supports MIME type '{mime_type}'")

    async def ingest_document(
        self,
        organization_id: str,
        title: str,
        content_bytes: bytes,
        owner_id: str,
        mime_type: str = "text/plain",
        source_type: SourceType = SourceType.HR_POLICY,
        document_type: DocumentType = DocumentType.POLICY,
        classification: KnowledgeClassification = KnowledgeClassification.INTERNAL,
        description: str = "",
        auto_publish: bool = True,
        effective_at: datetime | None = None,
        expires_at: datetime | None = None,
    ) -> KnowledgeDocument:
        """
        Execute full document ingestion pipeline:
        1. Compute SHA-256 checksum for idempotency.
        2. Parse text and structure using appropriate parser.
        3. Save Document and DocumentVersion entities.
        4. Initialize Access Policy.
        5. Index chunks into vector store.
        6. Publish if auto_publish is True.
        """
        checksum = hashlib.sha256(content_bytes).hexdigest()
        storage_ref = f"storage://{organization_id}/docs/{checksum}"

        # 1. Parse document content
        parser = self.get_parser_for_mime_type(mime_type)
        try:
            parsed_doc = await parser.parse(content_bytes, filename=title)
        except Exception as e:
            logger.error(f"Document parsing failed for '{title}': {e}")
            raise KnowledgeIngestionError(f"Failed to parse document content: {e}") from e

        # 2. Check if document exists with same checksum (Idempotency)
        existing_docs = await self.document_repo.list_documents(organization_id)
        existing = next((d for d in existing_docs if d.checksum == checksum), None)
        now = datetime.now(tz=UTC)

        if existing:
            logger.info(f"Document with identical checksum already exists [{existing.document_id}]. Re-indexing version.")
            doc = existing
            version_num = doc.current_version
        else:
            doc = KnowledgeDocument(
                organization_id=organization_id,
                title=title,
                description=description,
                source_type=source_type,
                document_type=document_type,
                classification=classification,
                owner_id=owner_id,
                status=DocumentStatus.PROCESSING,
                current_version=1,
                checksum=checksum,
                mime_type=mime_type,
                storage_reference=storage_ref,
                effective_at=effective_at or now,
                expires_at=expires_at,
            )
            version_num = 1
            await self.document_repo.save_document(doc)

        # 3. Create Version Record
        version_rec = KnowledgeDocumentVersion(
            document_id=doc.document_id,
            organization_id=organization_id,
            version_number=version_num,
            checksum=checksum,
            storage_reference=storage_ref,
            author_id=owner_id,
            change_summary="Initial upload" if version_num == 1 else "Updated document version",
            status=DocumentStatus.INDEXED,
            effective_at=effective_at or now,
            expires_at=expires_at,
        )
        await self.document_repo.save_version(version_rec)

        # 4. Save Default Access Policy if none exists
        existing_policy = await self.policy_repo.get_policy(organization_id, doc.document_id)
        if not existing_policy:
            policy = KnowledgeAccessPolicy(
                document_id=doc.document_id,
                organization_id=organization_id,
                max_classification=classification,
            )
            await self.policy_repo.save_policy(policy)

        # 5. Index chunks
        await self.indexing_service.index_document_version(doc, version_num, parsed_doc)

        # 6. Publish if requested
        if auto_publish:
            doc.status = DocumentStatus.PUBLISHED
            doc.published_at = now
            await self.document_repo.save_document(doc)

        logger.info(f"Successfully ingested and indexed document [{doc.document_id}] '{title}'")
        return doc
