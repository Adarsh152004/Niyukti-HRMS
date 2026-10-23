"""
AI-Powered Intelligent HRMS — Object Storage Abstraction Port.

Defines the contract for storing resumes, policy documents, generated payslips,
and exports without storing large binaries inside relational databases.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO


@dataclass
class StoredObject:
    object_key: str
    tenant_id: str
    file_name: str
    content_type: str
    size_bytes: int
    public_url: str | None
    created_at: str


class StoragePort(ABC):
    """Storage Port interface for enterprise file and object operations."""

    @abstractmethod
    async def upload(
        self,
        tenant_id: str,
        file_name: str,
        content_type: str,
        data: bytes | BinaryIO,
        category: str = "documents",
    ) -> StoredObject:
        """Uploads binary data and returns structured object metadata."""
        pass

    @abstractmethod
    async def download(self, tenant_id: str, object_key: str) -> bytes | None:
        """Downloads binary content for an object key."""
        pass

    @abstractmethod
    async def delete(self, tenant_id: str, object_key: str) -> bool:
        """Deletes an object by key."""
        pass

    @abstractmethod
    async def generate_signed_url(
        self,
        tenant_id: str,
        object_key: str,
        expires_seconds: int = 3600,
    ) -> str:
        """Generates a temporary signed download URL."""
        pass
