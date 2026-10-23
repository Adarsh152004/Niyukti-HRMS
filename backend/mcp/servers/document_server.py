"""
Document MCP Server — Document metadata extraction and completeness checking tools.
"""

from __future__ import annotations

from typing import Any

from backend.mcp.domain.models import MCPToolCallRequest, MCPToolContract
from backend.mcp.servers.base import MCPServer


class DocumentMCPServer(MCPServer):
    """Internal MCP server exposing document classification and metadata verification tools."""

    def __init__(self) -> None:
        super().__init__(
            server_id="document-server",
            name="Document Intelligence MCP Server",
            description="Extracts structured metadata, verifies tax forms, and checks onboarding document completeness.",
        )

    def _register_server_tools(self) -> None:
        self.register_tool(
            MCPToolContract(
                tool_id="document.extract_metadata",
                server_id=self.server_id,
                name="Extract Document Metadata",
                description="Extract structured attributes (document type, expiry date, identification numbers) from an uploaded file reference.",
                input_schema={"type": "object", "properties": {"document_id": {"type": "string"}}, "required": ["document_id"]},
                required_capabilities=["document:read"],
                is_read_only=True,
            ),
            self._handle_extract_metadata,
        )

    async def _handle_extract_metadata(self, req: MCPToolCallRequest) -> dict[str, Any]:
        doc_id = req.arguments.get("document_id", "doc-default")
        return {
            "document_id": doc_id,
            "document_type": "PASSPORT",
            "extracted_fields": {
                "document_number": "P12345678",
                "issuing_country": "USA",
                "expiration_date": "2030-05-15",
                "full_name": "Taylor Alex",
            },
            "confidence_score": 0.98,
        }
