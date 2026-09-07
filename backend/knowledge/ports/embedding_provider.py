"""
Embedding Provider Port — Generates dense vector representations of text.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence


class EmbeddingProviderPort(ABC):
    """Abstract port for vector embedding generation."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Generate embedding vector for a single query string."""
        pass

    @abstractmethod
    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Batch generate embeddings for multiple text passages."""
        pass
