"""
Tests for Document Parsers, Ingestion Pipeline, and Checksum Idempotency.
"""

from __future__ import annotations

import pytest

from backend.knowledge.application.knowledge_service import KnowledgeService
from backend.knowledge.domain.enums import DocumentStatus, KnowledgeClassification, SourceType
from backend.knowledge.infrastructure.parsers.pdf_parser import PDFDocumentParser
from backend.knowledge.infrastructure.parsers.text_parser import TextDocumentParser


@pytest.mark.asyncio
async def test_text_and_markdown_parser():
    parser = TextDocumentParser()
    assert parser.supports_mime_type("text/markdown") is True

    md_content = """# Company Code of Conduct

All employees are expected to maintain professional behavior.

## Working Hours
Standard working hours are 9:00 AM to 6:00 PM Monday through Friday.

## Remote Work Policy
Employees can work remotely up to 2 days per week with manager approval.
"""
    parsed = await parser.parse(md_content.encode("utf-8"), filename="conduct.md")
    assert len(parsed.sections) >= 3
    section_titles = [s.section_title for s in parsed.sections if s.section_title]
    assert any("Working Hours" in t for t in section_titles)
    assert any("Remote Work" in t for t in section_titles)


@pytest.mark.asyncio
async def test_pdf_parser_fallback():
    parser = PDFDocumentParser()
    assert parser.supports_mime_type("application/pdf") is True

    dummy_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Title (Benefits Summary) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    parsed = await parser.parse(dummy_pdf_bytes, filename="benefits.pdf")
    assert parsed.full_text is not None
    assert len(parsed.sections) > 0


@pytest.mark.asyncio
async def test_ingestion_pipeline_and_idempotency():
    svc = KnowledgeService.get_instance()
    org_id = "org-ingest-test"
    owner_id = "hr-admin-1"

    doc_text = """# HR Onboarding Guide
Welcome to the company!
Step 1: Complete IT asset setup.
Step 2: Sign benefits and insurance forms.
"""

    # First Ingestion
    doc1 = await svc.upload_and_index_document(
        organization_id=org_id,
        title="Onboarding Guide",
        content_bytes=doc_text.encode("utf-8"),
        owner_id=owner_id,
        source_type=SourceType.SOP,
        classification=KnowledgeClassification.INTERNAL,
        auto_publish=True,
    )
    assert doc1.status == DocumentStatus.PUBLISHED
    assert doc1.current_version == 1

    # Verify chunks created in repository
    chunks = await svc.chunk_repo.get_chunks_for_document(org_id, doc1.document_id)
    assert len(chunks) > 0

    # Second Ingestion with IDENTICAL content -> Idempotent re-use
    doc2 = await svc.upload_and_index_document(
        organization_id=org_id,
        title="Onboarding Guide",
        content_bytes=doc_text.encode("utf-8"),
        owner_id=owner_id,
    )
    assert doc2.document_id == doc1.document_id
    assert doc2.checksum == doc1.checksum
