"""
External Integration — Cloud Storage adapter interface.

Used for storing: resumes, employee documents, payslips, training materials,
audit export files, and model artifacts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class StorageObject:
    """Metadata about a stored object."""

    key: str
    bucket: str
    size_bytes: int
    content_type: str
    url: str | None = None
    etag: str | None = None
    created_at: str | None = None


class StorageAdapter(ABC):
    """
    Abstract cloud storage adapter.

    Concrete implementations: AWS S3, Google Cloud Storage, Azure Blob, MinIO.
    All uploads of sensitive documents (resumes, payslips) must use server-side encryption.
    """

    @abstractmethod
    async def upload(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        encrypt: bool = True,
    ) -> StorageObject:
        """Upload a file. Returns the storage object metadata."""
        ...

    @abstractmethod
    async def download(self, bucket: str, key: str) -> bytes:
        """Download a file by key. Returns raw bytes."""
        ...

    @abstractmethod
    async def delete(self, bucket: str, key: str) -> None:
        """Delete a stored object."""
        ...

    @abstractmethod
    async def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expiry_seconds: int = 3600,
    ) -> str:
        """Generate a time-limited pre-signed URL for secure download."""
        ...

    @abstractmethod
    async def list_objects(
        self,
        bucket: str,
        prefix: str = "",
    ) -> list[StorageObject]:
        """List objects in a bucket under an optional prefix."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the storage service is reachable."""
        ...
