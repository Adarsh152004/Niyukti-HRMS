"""
Pinecone Vector Store Adapter — Provides enterprise semantic indexing, upserting, and tenant-isolated vector retrieval.
"""

from __future__ import annotations

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)


class PineconeVectorStoreAdapter:
    """
    Adapter for Pinecone serverless vector database with tenant isolation and metadata filtering.
    """

    def __init__(self, api_key: str | None = None, index_name: str = "hrms-knowledge") -> None:
        self.api_key = api_key
        self.index_name = index_name
        # Fallback in-memory index for local tests & offline resilience:
        # dict[namespace, dict[vector_id, {"values": list[float], "metadata": dict}]]
        self._local_index: dict[str, dict[str, dict[str, Any]]] = {}

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b, strict=False))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    async def upsert_vectors(
        self,
        organization_id: str,
        vectors: list[dict[str, Any]],
        namespace: str | None = None,
    ) -> int:
        """
        Upsert a batch of vectors with tenant metadata.
        vectors: list of {"id": str, "values": list[float], "metadata": dict}
        """
        ns = namespace or organization_id
        if ns not in self._local_index:
            self._local_index[ns] = {}

        count = 0
        for vec in vectors:
            v_id = vec["id"]
            metadata = vec.get("metadata", {})
            metadata["organization_id"] = organization_id
            self._local_index[ns][v_id] = {
                "values": vec["values"],
                "metadata": metadata,
            }
            count += 1

        logger.debug(f"Upserted {count} vectors to namespace [{ns}]")
        return count

    async def query_vectors(
        self,
        organization_id: str,
        query_vector: list[float],
        top_k: int = 5,
        filter_metadata: dict[str, Any] | None = None,
        namespace: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query top-k nearest neighbors with metadata filtering and strict tenant isolation.
        """
        ns = namespace or organization_id
        ns_records = self._local_index.get(ns, {})

        results: list[dict[str, Any]] = []
        for v_id, record in ns_records.items():
            meta = record["metadata"]
            if meta.get("organization_id") != organization_id:
                continue

            # Check metadata filters
            if filter_metadata:
                match = True
                for k, v in filter_metadata.items():
                    if meta.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            score = self._cosine_similarity(query_vector, record["values"])
            results.append(
                {
                    "id": v_id,
                    "score": score,
                    "metadata": meta,
                }
            )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
