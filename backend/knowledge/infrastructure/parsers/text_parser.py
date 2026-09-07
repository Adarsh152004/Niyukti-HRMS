"""
Plain Text & Markdown Document Parser.
"""

from __future__ import annotations

import re

from backend.knowledge.ports.document_parser import (
    DocumentParserPort,
    ParsedDocument,
    ParsedSection,
)


class TextDocumentParser(DocumentParserPort):
    """Parser for raw text and markdown files with header/section awareness."""

    def supports_mime_type(self, mime_type: str) -> bool:
        return mime_type in ["text/plain", "text/markdown", "text/x-markdown", "text/csv", "application/json"]

    async def parse(self, content_bytes: bytes, filename: str = "") -> ParsedDocument:
        text = content_bytes.decode("utf-8", errors="replace")
        lines = text.splitlines()

        sections: list[ParsedSection] = []
        current_title: str | None = None
        current_lines: list[str] = []

        header_pattern = re.compile(r"^(#{1,6}\s+.*|[A-Z0-9\s]{4,}:)$")

        for line in lines:
            if header_pattern.match(line.strip()):
                if current_lines:
                    sections.append(
                        ParsedSection(
                            section_title=current_title,
                            content="\n".join(current_lines).strip(),
                        )
                    )
                    current_lines = []
                current_title = line.strip().lstrip("#").strip().rstrip(":")
            else:
                current_lines.append(line)

        if current_lines:
            sections.append(
                ParsedSection(
                    section_title=current_title,
                    content="\n".join(current_lines).strip(),
                )
            )

        if not sections:
            sections.append(ParsedSection(section_title=None, content=text))

        return ParsedDocument(
            full_text=text,
            sections=sections,
            metadata={"filename": filename, "line_count": str(len(lines))},
        )
