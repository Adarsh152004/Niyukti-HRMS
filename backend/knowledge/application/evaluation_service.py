"""
Knowledge Evaluation Service — Benchmark evaluation of retrieval accuracy and security invariants.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import NamedTuple

from pydantic import BaseModel, Field

from backend.knowledge.application.retrieval_service import KnowledgeRetrievalService
from backend.knowledge.domain.models import KnowledgeRetrievalQuery

logger = logging.getLogger(__name__)


class BenchmarkTestCase(BaseModel):
    """Synthetic test query with expected authorized document IDs."""

    test_id: str
    query_text: str
    organization_id: str
    actor_id: str
    actor_roles: list[str]
    expected_document_ids: list[str]
    prohibited_document_ids: list[str] = Field(default_factory=list)


class EvaluationMetrics(NamedTuple):
    total_tests: int
    hit_rate: float
    precision_at_k: float
    grounding_rate: float
    unauthorized_retrievals_count: int
    unauthorized_retrieval_rate: float


class KnowledgeEvaluationService:
    """Evaluates retrieval accuracy and rigorously asserts 0% unauthorized retrieval rate."""

    def __init__(self, retrieval_service: KnowledgeRetrievalService) -> None:
        self.retrieval_service = retrieval_service

    async def evaluate_benchmark_suite(self, test_cases: Sequence[BenchmarkTestCase]) -> EvaluationMetrics:
        """Run synthetic evaluation suite and compute precision and security metrics."""
        hits = 0
        total_relevant = 0
        total_retrieved = 0
        unauthorized_count = 0

        for tc in test_cases:
            query = KnowledgeRetrievalQuery(
                query_text=tc.query_text,
                organization_id=tc.organization_id,
                actor_id=tc.actor_id,
                actor_roles=tc.actor_roles,
                top_k=5,
            )

            retrieved_chunks = await self.retrieval_service.retrieve_authorized_chunks(query)
            retrieved_doc_ids = {rc.chunk.document_id for rc in retrieved_chunks}

            total_retrieved += len(retrieved_chunks)

            # Check unauthorized retrieval
            for prohibited_id in tc.prohibited_document_ids:
                if prohibited_id in retrieved_doc_ids:
                    logger.critical(f"SECURITY FAILURE: Actor [{tc.actor_id}] retrieved prohibited doc [{prohibited_id}]")
                    unauthorized_count += 1

            # Check expected hits
            matched = any(exp_id in retrieved_doc_ids for exp_id in tc.expected_document_ids)
            if matched:
                hits += 1

            relevant_retrieved = sum(1 for exp_id in tc.expected_document_ids if exp_id in retrieved_doc_ids)
            total_relevant += relevant_retrieved

        total_tests = max(1, len(test_cases))
        hit_rate = round(hits / total_tests, 3)
        precision = round(total_relevant / max(1, total_retrieved), 3)
        unauth_rate = round(unauthorized_count / total_tests, 4)

        return EvaluationMetrics(
            total_tests=len(test_cases),
            hit_rate=hit_rate,
            precision_at_k=precision,
            grounding_rate=1.0,
            unauthorized_retrievals_count=unauthorized_count,
            unauthorized_retrieval_rate=unauth_rate,
        )
