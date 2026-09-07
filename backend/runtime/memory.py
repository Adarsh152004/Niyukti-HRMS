"""
Enterprise Runtime — Memory abstraction.

Defines adapter interfaces for:
- Key-Value store (Redis-backed in production)
- Vector/Semantic store (Qdrant-backed in production)

No real connections are made here; concrete adapters are injected at runtime.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class KVStore(ABC):
    """
    Abstract key-value store interface.

    Used for caching, session state, rate-limiting counters, and agent context.
    """

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Retrieve a value by key. Returns None if not found."""
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Store a value. Optional TTL causes expiry."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove a key from the store."""
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check whether a key exists."""
        ...

    @abstractmethod
    async def increment(self, key: str, amount: int = 1) -> int:
        """Atomically increment an integer counter."""
        ...


class VectorStore(ABC):
    """
    Abstract vector / semantic memory interface.

    Used for semantic search across embeddings of HR documents, policies,
    candidate profiles, and agent memory.
    """

    @abstractmethod
    async def upsert(
        self,
        collection: str,
        doc_id: str,
        vector: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Insert or update a vector with associated metadata."""
        ...

    @abstractmethod
    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Semantic nearest-neighbour search. Returns ranked results with scores."""
        ...

    @abstractmethod
    async def delete(self, collection: str, doc_id: str) -> None:
        """Remove a document from the vector collection."""
        ...

    @abstractmethod
    async def create_collection(self, collection: str, vector_size: int) -> None:
        """Create a new vector collection if it does not exist."""
        ...


class InMemoryKVStore(KVStore):
    """Simple in-memory KV store for development and testing."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    async def get(self, key: str) -> Any | None:
        return self._store.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        # TTL not enforced in memory store (acceptable for testing)
        self._store[key] = value

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        return key in self._store

    async def increment(self, key: str, amount: int = 1) -> int:
        current = int(self._store.get(key, 0))
        new_value = current + amount
        self._store[key] = new_value
        return new_value
