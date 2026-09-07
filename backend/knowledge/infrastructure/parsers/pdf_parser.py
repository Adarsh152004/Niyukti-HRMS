"""
PDF Document Parser with Safe Fallback.
"""

from __future__ import annotations

import io
import logging

from backend.knowledge.ports.document_parser import (
    DocumentParserPort,
    ParsedDocument,
    ParsedSection,
)

logger = logging.getLogger(__name__)


class PDFDocumentParser(DocumentParserPort):
    """Parser extracting text pages and sections from PDF documents."""

    def supports_mime_type(self, mime_type: str) -> bool:
        return mime_type in ["application/pdf", "application/x-pdf"]

    async def parse(self, content_bytes: bytes, filename: str = "") -> ParsedDocument:
        # Safe extraction attempt
        try:
            # Try importing pypdf or pdfplumber if available
            import pypdf

            reader = pypdf.PdfReader(io.BytesIO(content_bytes))
            sections: list[ParsedSection] = []
            full_text_parts: list[str] = []

            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    sections.append(
                        ParsedSection(
                            section_title=f"Page {idx + 1}",
                            content=page_text.strip(),
                            page_number=idx + 1,
                        )
                    )
                    full_text_parts.append(page_text.strip())

            full_text = "\n\n".join(full_text_parts)
            return ParsedDocument(
                full_text=full_text,
                sections=sections or [ParsedSection(section_title="Full Document", content=full_text)],
                metadata={"filename": filename, "page_count": str(len(reader.pages))},
            )

        except Exception as e:
            logger.warning(f"Native PDF extraction failed or library missing ({e}). Using raw text fallback.")
            # Fallback text extraction
            raw_text = content_bytes.decode("latin-1", errors="ignore")
            # Extract printable ASCII lines
            cleaned = "\n".join([line for line in raw_text.splitlines() if len(line.strip()) > 3 and line.isascii()])
            if not cleaned:
                cleaned = f"[PDF Document Content from {filename}]"

            return ParsedDocument(
                full_text=cleaned,
                sections=[ParsedSection(section_title="Extracted Text", content=cleaned, page_number=1)],
                metadata={"filename": filename, "parser_note": "fallback_extractor"},
            )
