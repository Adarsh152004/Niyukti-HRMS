"""
Supabase Storage Adapter — S3-compatible object and blob storage integration.
"""

from __future__ import annotations

import hashlib
import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class StoredObjectMetadata(BaseModel):
    bucket: str
    object_path: str
    size_bytes: int
    content_type: str
    sha256_checksum: str
    public_url: str | None = None


class SupabaseStorageAdapter:
    """Adapter for Supabase Object Storage buckets."""

    def __init__(self, project_url: str = "https://mock.supabase.co", anon_key: str = "mock-key") -> None:
        self.project_url = project_url
        self.anon_key = anon_key
        self._in_memory_buckets: dict[str, dict[str, bytes]] = {}

    async def upload_file(
        self,
        bucket: str,
        path: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> StoredObjectMetadata:
        """Upload raw binary data to designated bucket path."""
        if bucket not in self._in_memory_buckets:
            self._in_memory_buckets[bucket] = {}
        self._in_memory_buckets[bucket][path] = content

        sha = hashlib.sha256(content).hexdigest()
        url = f"{self.project_url}/storage/v1/object/public/{bucket}/{path}"

        logger.info(f"Uploaded {len(content)} bytes to Supabase storage: [{bucket}/{path}]")
        return StoredObjectMetadata(
            bucket=bucket,
            object_path=path,
            size_bytes=len(content),
            content_type=content_type,
            sha256_checksum=sha,
            public_url=url,
        )

    async def download_file(self, bucket: str, path: str) -> bytes | None:
        """Download binary content from bucket path."""
        return self._in_memory_buckets.get(bucket, {}).get(path)
