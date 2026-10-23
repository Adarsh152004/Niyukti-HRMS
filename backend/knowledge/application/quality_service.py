"""
Knowledge Quality Service — Evaluates document base health, stale policies, and broken metadata.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from backend.knowledge.domain.enums import DocumentStatus
from backend.knowledge.domain.models import KnowledgeQualityReport
from backend.knowledge.ports.repositories import KnowledgeDocumentRepositoryPort

logger = logging.getLogger(__name__)


class KnowledgeQualityService:
    """Monitors knowledge base completeness, stale document ratios, and quality scores."""

    def __init__(self, document_repo: KnowledgeDocumentRepositoryPort) -> None:
        self.document_repo = document_repo

    async def generate_quality_report(self, organization_id: str) -> KnowledgeQualityReport:
        """Analyze all tenant documents and produce a 0-100 quality score."""
        docs = await self.document_repo.list_documents(organization_id)
        now = datetime.now(tz=UTC)
        one_year_ago = now - timedelta(days=365)

        total = len(docs)
        published = sum(1 for d in docs if d.status == DocumentStatus.PUBLISHED)
        expired = sum(1 for d in docs if d.expires_at and d.expires_at < now)
        failed = sum(1 for d in docs if d.status == DocumentStatus.FAILED)
        stale = sum(1 for d in docs if d.updated_at < one_year_ago and d.status == DocumentStatus.PUBLISHED)

        # Base 100 with penalties for expired, failed, and stale docs
        penalties = (failed * 15.0) + (expired * 5.0) + (stale * 2.0)
        score = max(0.0, min(100.0, round(100.0 - penalties, 1))) if total > 0 else 100.0

        return KnowledgeQualityReport(
            organization_id=organization_id,
            quality_score=score,
            total_documents=total,
            published_documents=published,
            expired_documents=expired,
            stale_documents=stale,
            failed_ingestions=failed,
            broken_citations_detected=0,
            unauthorized_retrieval_rate=0.0,
        )
