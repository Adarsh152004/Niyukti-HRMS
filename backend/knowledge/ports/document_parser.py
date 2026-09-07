"""
Document Parser Port — Interface for extracting structured text and section headers from file content.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import NamedTuple


class ParsedSection(NamedTuple):
    section_title: str | None
    content: str
    page_number: int | None = None


class ParsedDocument(NamedTuple):
    full_text: str
    sections: list[ParsedSection]
    metadata: dict[str, str]


class DocumentParserPort(ABC):
    """Abstract port for file format text extraction."""

    @abstractmethod
    def supports_mime_type(self, mime_type: str) -> bool:
        """Check if parser handles this mime type."""
        pass

    @abstractmethod
    async def parse(self, content_bytes: bytes, filename: str = "") -> ParsedDocument:
        """Extract clean text and structure from raw binary data."""
        pass
