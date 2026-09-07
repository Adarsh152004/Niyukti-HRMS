"""
Knowledge Retention Service — Integrates with DataRetentionEngine for archival and vector purging.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from backend.knowledge.domain.enums import DocumentStatus
from backend.knowledge.domain.exceptions import KnowledgeDocumentNotFoundError
from backend.knowledge.domain.models import KnowledgeDocument
from backend.knowledge.ports.repositories import (
    KnowledgeChunkRepositoryPort,
    KnowledgeDocumentRepositoryPort,
)
from backend.knowledge.ports.vector_store import VectorStorePort
from backend.privacy.retention import (
    DataRetentionEngine,
    RetentionCategory,
)

logger = logging.getLogger(__name__)


class KnowledgeRetentionService:
    """Manages document archival, retention lifecycle, and vector purge propagation."""

    def __init__(
        self,
        document_repo: KnowledgeDocumentRepositoryPort,
        chunk_repo: KnowledgeChunkRepositoryPort,
        vector_store: VectorStorePort,
        retention_engine: DataRetentionEngine | None = None,
    ) -> None:
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
        self.vector_store = vector_store
        self.retention_engine = retention_engine or DataRetentionEngine.get_instance()

    async def archive_document(self, organization_id: str, document_id: str, reason: str = "") -> KnowledgeDocument:
        """Archive a document and deactivate its vectors from active retrieval."""
        doc = await self.document_repo.get_document(organization_id, document_id)
        if not doc:
            raise KnowledgeDocumentNotFoundError(f"Document [{document_id}] not found.")

        doc.status = DocumentStatus.ARCHIVED
        doc.archived_at = datetime.now(tz=UTC)
        await self.document_repo.save_document(doc)

        # Deactivate vectors from active search by purging vector store index
        await self.vector_store.delete_chunks_for_document(organization_id, document_id)

        # Register in privacy retention engine
        await self.retention_engine.register_record(
            organization_id=organization_id,
            category=RetentionCategory.EMPLOYEE_RECORD,
            resource_id=document_id,
        )

        logger.info(f"Archived document [{document_id}] and purged active search vectors: {reason}")
        return doc
