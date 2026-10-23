"""
Gateway Embedding Adapter — Bridges EmbeddingProviderPort with AIGatewayRouter.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence

from backend.ai.gateway.router import AIGatewayRouter
from backend.knowledge.ports.embedding_provider import EmbeddingProviderPort


class GatewayEmbeddingAdapter(EmbeddingProviderPort):
    """Generates embeddings by invoking the AI Gateway router or local mock provider."""

    def __init__(self, dimension: int = 128) -> None:
        self._dimension = dimension
        self.router = AIGatewayRouter.get_instance()

    @property
    def provider_name(self) -> str:
        return "gateway_embedding"

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed_query(self, text: str) -> list[float]:
        # Deterministic 128-dim embedding derived from SHA-256 for consistent testing
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [(int(sha[i % len(sha)], 16) / 15.0) for i in range(self._dimension)]

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        results: list[list[float]] = []
        for text in texts:
            emb = await self.embed_query(text)
            results.append(emb)
        return results
