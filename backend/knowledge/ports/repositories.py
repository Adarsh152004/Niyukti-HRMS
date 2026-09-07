"""
Knowledge Repository Ports — Persistence interfaces for documents, versions, chunks, and access policies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from backend.knowledge.domain.enums import DocumentStatus, KnowledgeClassification
from backend.knowledge.domain.models import (
    KnowledgeAccessPolicy,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeDocumentVersion,
    KnowledgeIndexRecord,
)


class KnowledgeDocumentRepositoryPort(ABC):
    """Port for KnowledgeDocument and Version persistence."""

    @abstractmethod
    async def save_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        pass

    @abstractmethod
    async def get_document(self, organization_id: str, document_id: str) -> KnowledgeDocument | None:
        pass

    @abstractmethod
    async def list_documents(
        self,
        organization_id: str,
        status: DocumentStatus | None = None,
        classification: KnowledgeClassification | None = None,
    ) -> Sequence[KnowledgeDocument]:
        pass

    @abstractmethod
    async def save_version(self, version: KnowledgeDocumentVersion) -> KnowledgeDocumentVersion:
        pass

    @abstractmethod
    async def get_version(self, document_id: str, version_number: int) -> KnowledgeDocumentVersion | None:
        pass

    @abstractmethod
    async def list_versions(self, document_id: str) -> Sequence[KnowledgeDocumentVersion]:
        pass


class KnowledgeChunkRepositoryPort(ABC):
    """Port for KnowledgeChunk metadata persistence."""

    @abstractmethod
    async def save_chunks(self, chunks: Sequence[KnowledgeChunk]) -> Sequence[KnowledgeChunk]:
        pass

    @abstractmethod
    async def get_chunks_for_document(
        self,
        organization_id: str,
        document_id: str,
        version_number: int | None = None,
    ) -> Sequence[KnowledgeChunk]:
        pass

    @abstractmethod
    async def delete_chunks(self, organization_id: str, document_id: str, version_number: int | None = None) -> int:
        pass


class KnowledgeAccessPolicyRepositoryPort(ABC):
    """Port for KnowledgeAccessPolicy persistence."""

    @abstractmethod
    async def save_policy(self, policy: KnowledgeAccessPolicy) -> KnowledgeAccessPolicy:
        pass

    @abstractmethod
    async def get_policy(self, organization_id: str, document_id: str) -> KnowledgeAccessPolicy | None:
        pass


class KnowledgeIndexRecordRepositoryPort(ABC):
    """Port for Indexing synchronization tracking."""

    @abstractmethod
    async def save_index_record(self, record: KnowledgeIndexRecord) -> KnowledgeIndexRecord:
        pass

    @abstractmethod
    async def get_index_record(self, document_id: str, version_number: int) -> KnowledgeIndexRecord | None:
        pass
