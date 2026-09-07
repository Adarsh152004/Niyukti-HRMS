"""
In-Memory Vector Store Adapter — Provides vector similarity search with strict tenant isolation.
"""

from __future__ import annotations

import asyncio
import math
from collections.abc import Sequence
from typing import Any

from backend.knowledge.domain.models import KnowledgeChunk
from backend.knowledge.ports.vector_store import (
    VectorSearchResult,
    VectorStorePort,
)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class InMemoryVectorStore(VectorStorePort):
    """In-memory vector store for deterministic testing and local execution."""

    _instance: InMemoryVectorStore | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        # Key: (organization_id, chunk_id) -> KnowledgeChunk
        self._store: dict[tuple[str, str], KnowledgeChunk] = {}

    @classmethod
    def get_instance(cls) -> InMemoryVectorStore:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def upsert_chunks(self, chunks: Sequence[KnowledgeChunk]) -> int:
        async with self._lock:
            for chunk in chunks:
                key = (chunk.organization_id, chunk.chunk_id)
                self._store[key] = chunk
            return len(chunks)

    async def query_similar(
        self,
        organization_id: str,
        query_embedding: list[float],
        top_k: int = 5,
        min_score: float = 0.5,
        filter_document_ids: list[str] | None = None,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        async with self._lock:
            candidates: list[VectorSearchResult] = []

            for (org_id, _), chunk in self._store.items():
                # Strict Tenant Isolation
                if org_id != organization_id:
                    continue

                # Document Filter
                if filter_document_ids is not None and chunk.document_id not in filter_document_ids:
                    continue

                if not chunk.embedding:
                    continue

                score = cosine_similarity(query_embedding, chunk.embedding)
                if score >= min_score:
                    candidates.append(VectorSearchResult(chunk=chunk, score=round(score, 4)))

            # Sort descending by score
            candidates.sort(key=lambda x: x.score, reverse=True)
            return candidates[:top_k]

    async def delete_chunks_for_document(
        self,
        organization_id: str,
        document_id: str,
        version_number: int | None = None,
    ) -> int:
        async with self._lock:
            to_delete = [
                key
                for key, chunk in self._store.items()
                if key[0] == organization_id
                and chunk.document_id == document_id
                and (version_number is None or chunk.document_version == version_number)
            ]
            for key in to_delete:
                del self._store[key]
            return len(to_delete)

    async def clear(self) -> None:
        """Clear store for tests."""
        async with self._lock:
            self._store.clear()
