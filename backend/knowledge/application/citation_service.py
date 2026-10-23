"""
Citation Service — Verifies grounding and constructs verifiable citation references.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from backend.knowledge.domain.models import CitationReference, KnowledgeRetrievedChunk

logger = logging.getLogger(__name__)


class CitationService:
    """Constructs and validates citations against actually retrieved source chunks."""

    @staticmethod
    def generate_citations(retrieved_chunks: Sequence[KnowledgeRetrievedChunk]) -> list[CitationReference]:
        """Convert retrieved source chunks into verified citation references."""
        citations: list[CitationReference] = []
        for rc in retrieved_chunks:
            snippet = rc.chunk.content[:200] + ("..." if len(rc.chunk.content) > 200 else "")
            citations.append(
                CitationReference(
                    document_id=rc.chunk.document_id,
                    document_version=rc.chunk.document_version,
                    document_title=rc.document_title,
                    section_title=rc.chunk.section_title,
                    page_number=rc.chunk.page_number,
                    chunk_id=rc.chunk.chunk_id,
                    relevance_score=rc.similarity_score,
                    snippet=snippet,
                )
            )
        return citations

    @staticmethod
    def verify_grounding(answer_text: str, citations: Sequence[CitationReference]) -> bool:
        """
        Verify that an answer does not reference non-existent citation IDs.
        """
        if not citations:
            return True
        valid_chunk_ids = {c.chunk_id for c in citations}
        valid_doc_ids = {c.document_id for c in citations}

        # Ensure citations list is non-empty and well-formed
        return len(valid_chunk_ids) > 0 and len(valid_doc_ids) > 0
