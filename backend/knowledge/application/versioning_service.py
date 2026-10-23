"""
Knowledge Versioning Service — Manages document updates and immutable version lifecycles.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime

from backend.knowledge.application.indexing_service import KnowledgeIndexingService
from backend.knowledge.domain.enums import DocumentStatus
from backend.knowledge.domain.exceptions import KnowledgeDocumentNotFoundError
from backend.knowledge.domain.models import KnowledgeDocumentVersion
from backend.knowledge.ports.document_parser import DocumentParserPort
from backend.knowledge.ports.repositories import KnowledgeDocumentRepositoryPort

logger = logging.getLogger(__name__)


class KnowledgeVersioningService:
    """Manages document version transitions without mutating historical published snapshots."""

    def __init__(
        self,
        document_repo: KnowledgeDocumentRepositoryPort,
        indexing_service: KnowledgeIndexingService,
        parsers: list[DocumentParserPort],
    ) -> None:
        self.document_repo = document_repo
        self.indexing_service = indexing_service
        self.parsers = parsers

    async def create_new_version(
        self,
        organization_id: str,
        document_id: str,
        new_content_bytes: bytes,
        author_id: str,
        change_summary: str = "",
        mime_type: str = "text/plain",
    ) -> KnowledgeDocumentVersion:
        """Create and index a new immutable version of an existing document."""
        doc = await self.document_repo.get_document(organization_id, document_id)
        if not doc:
            raise KnowledgeDocumentNotFoundError(f"Document [{document_id}] not found in organization [{organization_id}]")

        new_version_num = doc.current_version + 1
        checksum = hashlib.sha256(new_content_bytes).hexdigest()
        storage_ref = f"storage://{organization_id}/docs/{checksum}"

        # Parse new content
        parser = next((p for p in self.parsers if p.supports_mime_type(mime_type)), self.parsers[0])
        parsed_doc = await parser.parse(new_content_bytes, filename=doc.title)

        now = datetime.now(tz=UTC)
        version_rec = KnowledgeDocumentVersion(
            document_id=document_id,
            organization_id=organization_id,
            version_number=new_version_num,
            checksum=checksum,
            storage_reference=storage_ref,
            author_id=author_id,
            change_summary=change_summary,
            status=DocumentStatus.INDEXED,
            effective_at=now,
        )
        await self.document_repo.save_version(version_rec)

        # Index new version chunks
        await self.indexing_service.index_document_version(doc, new_version_num, parsed_doc)

        # Update parent document metadata
        doc.current_version = new_version_num
        doc.checksum = checksum
        doc.updated_at = now
        await self.document_repo.save_document(doc)

        logger.info(f"Created version {new_version_num} for document [{document_id}]")
        return version_rec
