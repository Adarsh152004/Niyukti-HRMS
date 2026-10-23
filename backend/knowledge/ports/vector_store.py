"""
Vector Store Port — Storage and similarity search abstraction for vectorized chunks.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, NamedTuple

from backend.knowledge.domain.models import KnowledgeChunk


class VectorSearchResult(NamedTuple):
    chunk: KnowledgeChunk
    score: float


class VectorStorePort(ABC):
    """Abstract interface for vector database storage and ANN search."""

    @abstractmethod
    async def upsert_chunks(self, chunks: Sequence[KnowledgeChunk]) -> int:
        """Insert or replace vector embeddings and metadata for chunks."""
        pass

    @abstractmethod
    async def query_similar(
        self,
        organization_id: str,
        query_embedding: list[float],
        top_k: int = 5,
        min_score: float = 0.5,
        filter_document_ids: list[str] | None = None,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Perform similarity search scoped strictly to organization_id and optional document filters."""
        pass

    @abstractmethod
    async def delete_chunks_for_document(
        self,
        organization_id: str,
        document_id: str,
        version_number: int | None = None,
    ) -> int:
        """Purge indexed vectors when document is archived, deleted, or superseded."""
        pass
