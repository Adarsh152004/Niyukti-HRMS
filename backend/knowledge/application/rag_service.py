"""
Knowledge RAG Service & Context Builder — End-to-end authorized RAG synthesis.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from backend.ai.firewall.prompt_firewall import (
    PromptFirewall,
)
from backend.ai.gateway.router import AIGatewayRouter, RoutingTier
from backend.knowledge.application.citation_service import CitationService
from backend.knowledge.application.retrieval_service import KnowledgeRetrievalService
from backend.knowledge.domain.models import (
    KnowledgeAnswer,
    KnowledgeRetrievalQuery,
    KnowledgeRetrievedChunk,
)

logger = logging.getLogger(__name__)


class KnowledgeContextBuilder:
    """Safely constructs bounded RAG prompt contexts with untrusted document containment."""

    @staticmethod
    def build_rag_prompt(query_text: str, retrieved_chunks: Sequence[KnowledgeRetrievedChunk]) -> str:
        """
        Assemble user query and retrieved source chunks.
        Applies PromptFirewall context wrapping to ensure external document chunks are treated as untrusted data.
        """
        doc_context_blocks: list[str] = []
        for idx, rc in enumerate(retrieved_chunks):
            doc_label = f"Source {idx + 1}: {rc.document_title} (v{rc.chunk.document_version})"
            wrapped_content = PromptFirewall.wrap_external_document_context(
                document_text=rc.chunk.content,
                document_name=doc_label,
            )
            doc_context_blocks.append(f"[{doc_label}]\n{wrapped_content}")

        context_str = "\n\n".join(doc_context_blocks)
        prompt = (
            f"You are an authoritative HR Assistant. Answer the employee's question based strictly on the provided authorized sources.\n"
            f"If the provided sources do not contain sufficient evidence to answer, state clearly that you do not have enough information.\n\n"
            f"=== AUTHORIZED KNOWLEDGE SOURCES ===\n"
            f"{context_str}\n\n"
            f"=== USER INQUIRY ===\n"
            f"{query_text}\n\n"
            f"=== INSTRUCTIONS ===\n"
            f"1. Ground your answer exclusively on the sources above.\n"
            f"2. Mention the source document titles where relevant.\n"
            f"3. Do NOT make up facts or extrapolate beyond provided policies."
        )
        return prompt


class KnowledgeRAGService:
    """Master RAG orchestration service."""

    def __init__(
        self,
        retrieval_service: KnowledgeRetrievalService,
        ai_gateway_router: AIGatewayRouter | None = None,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.router = ai_gateway_router or AIGatewayRouter.get_instance()

    async def answer_query(
        self,
        query: KnowledgeRetrievalQuery,
    ) -> KnowledgeAnswer:
        """
        End-to-end RAG query flow:
        1. Retrieve authorized chunks (pre-authorized).
        2. If no chunks found -> return ABSTAIN answer.
        3. Build sanitized prompt with PromptFirewall.
        4. Call AI Gateway.
        5. Generate verifiable citations.
        """
        # 1. Retrieve authorized source chunks
        chunks = await self.retrieval_service.retrieve_authorized_chunks(query)

        # 2. Check evidence sufficiency -> Abstain if 0 chunks found
        if not chunks:
            logger.info(f"RAG abstaining on query '{query.query_text[:50]}': no authorized sources found.")
            return KnowledgeAnswer(
                answer="I do not have access to any authorized documents or policies to answer this inquiry.",
                citations=[],
                confidence=0.0,
                abstain=True,
                abstain_reason="NO_AUTHORIZED_SOURCES",
                retrieved_source_count=0,
                warnings=["Query returned 0 authorized source documents."],
            )

        # 3. Build RAG prompt
        rag_prompt = KnowledgeContextBuilder.build_rag_prompt(query.query_text, chunks)

        # 4. Invoke AI Gateway
        response = await self.router.generate_text(
            prompt=rag_prompt,
            organization_id=query.organization_id,
            tier=RoutingTier.BALANCED,
            system_instruction="You are a compliant HRMS knowledge assistant adhering strictly to company policy.",
        )

        # 5. Generate verified citations
        citations = CitationService.generate_citations(chunks)

        return KnowledgeAnswer(
            answer=response.content,
            citations=citations,
            confidence=0.95,
            abstain=False,
            retrieved_source_count=len(chunks),
            metadata={"model": response.model_name, "provider": response.provider},
        )
