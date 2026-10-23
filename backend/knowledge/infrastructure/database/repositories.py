"""
Knowledge Repositories — In-memory implementations of document, version, chunk, and access policy ports.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from backend.knowledge.domain.enums import DocumentStatus, KnowledgeClassification
from backend.knowledge.domain.models import (
    KnowledgeAccessPolicy,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeDocumentVersion,
    KnowledgeIndexRecord,
)
from backend.knowledge.ports.repositories import (
    KnowledgeAccessPolicyRepositoryPort,
    KnowledgeChunkRepositoryPort,
    KnowledgeDocumentRepositoryPort,
    KnowledgeIndexRecordRepositoryPort,
)


class InMemoryKnowledgeDocumentRepository(KnowledgeDocumentRepositoryPort):
    """In-memory repository for knowledge documents and versions."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._documents: dict[tuple[str, str], KnowledgeDocument] = {}
        self._versions: dict[tuple[str, int], KnowledgeDocumentVersion] = {}

    async def save_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        async with self._lock:
            key = (document.organization_id, document.document_id)
            self._documents[key] = document
            return document

    async def get_document(self, organization_id: str, document_id: str) -> KnowledgeDocument | None:
        async with self._lock:
            return self._documents.get((organization_id, document_id))

    async def list_documents(
        self,
        organization_id: str,
        status: DocumentStatus | None = None,
        classification: KnowledgeClassification | None = None,
    ) -> Sequence[KnowledgeDocument]:
        async with self._lock:
            results = [doc for (org_id, _), doc in self._documents.items() if org_id == organization_id]
            if status:
                results = [d for d in results if d.status == status]
            if classification:
                results = [d for d in results if d.classification == classification]
            return results

    async def save_version(self, version: KnowledgeDocumentVersion) -> KnowledgeDocumentVersion:
        async with self._lock:
            key = (version.document_id, version.version_number)
            self._versions[key] = version
            return version

    async def get_version(self, document_id: str, version_number: int) -> KnowledgeDocumentVersion | None:
        async with self._lock:
            return self._versions.get((document_id, version_number))

    async def list_versions(self, document_id: str) -> Sequence[KnowledgeDocumentVersion]:
        async with self._lock:
            return [v for (doc_id, _), v in self._versions.items() if doc_id == document_id]

    async def clear(self) -> None:
        async with self._lock:
            self._documents.clear()
            self._versions.clear()


class InMemoryKnowledgeChunkRepository(KnowledgeChunkRepositoryPort):
    """In-memory repository for knowledge chunks."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._chunks: dict[str, KnowledgeChunk] = {}

    async def save_chunks(self, chunks: Sequence[KnowledgeChunk]) -> Sequence[KnowledgeChunk]:
        async with self._lock:
            for c in chunks:
                self._chunks[c.chunk_id] = c
            return chunks

    async def get_chunks_for_document(
        self,
        organization_id: str,
        document_id: str,
        version_number: int | None = None,
    ) -> Sequence[KnowledgeChunk]:
        async with self._lock:
            return [
                c
                for c in self._chunks.values()
                if c.organization_id == organization_id
                and c.document_id == document_id
                and (version_number is None or c.document_version == version_number)
            ]

    async def delete_chunks(self, organization_id: str, document_id: str, version_number: int | None = None) -> int:
        async with self._lock:
            to_del = [
                cid
                for cid, c in self._chunks.items()
                if c.organization_id == organization_id
                and c.document_id == document_id
                and (version_number is None or c.document_version == version_number)
            ]
            for cid in to_del:
                del self._chunks[cid]
            return len(to_del)


class InMemoryKnowledgeAccessPolicyRepository(KnowledgeAccessPolicyRepositoryPort):
    """In-memory repository for knowledge access policies."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._policies: dict[tuple[str, str], KnowledgeAccessPolicy] = {}

    async def save_policy(self, policy: KnowledgeAccessPolicy) -> KnowledgeAccessPolicy:
        async with self._lock:
            key = (policy.organization_id, policy.document_id)
            self._policies[key] = policy
            return policy

    async def get_policy(self, organization_id: str, document_id: str) -> KnowledgeAccessPolicy | None:
        async with self._lock:
            return self._policies.get((organization_id, document_id))


class InMemoryKnowledgeIndexRecordRepository(KnowledgeIndexRecordRepositoryPort):
    """In-memory repository for knowledge index records."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._records: dict[tuple[str, int], KnowledgeIndexRecord] = {}

    async def save_index_record(self, record: KnowledgeIndexRecord) -> KnowledgeIndexRecord:
        async with self._lock:
            key = (record.document_id, record.version_number)
            self._records[key] = record
            return record

    async def get_index_record(self, document_id: str, version_number: int) -> KnowledgeIndexRecord | None:
        async with self._lock:
            return self._records.get((document_id, version_number))
