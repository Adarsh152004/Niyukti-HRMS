"""
Knowledge Retrieval Service — Pre-retrieval authorization, semantic similarity, and precedence resolution.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from backend.knowledge.application.access_service import KnowledgeAccessService
from backend.knowledge.domain.enums import DocumentStatus
from backend.knowledge.domain.models import (
    KnowledgeDocument,
    KnowledgeRetrievalQuery,
    KnowledgeRetrievedChunk,
)
from backend.knowledge.ports.embedding_provider import EmbeddingProviderPort
from backend.knowledge.ports.repositories import KnowledgeDocumentRepositoryPort
from backend.knowledge.ports.vector_store import VectorStorePort

logger = logging.getLogger(__name__)


class KnowledgeRetrievalService:
    """Orchestrates authorization-filtered semantic search against the vector store."""

    def __init__(
        self,
        document_repo: KnowledgeDocumentRepositoryPort,
        access_service: KnowledgeAccessService,
        embedding_provider: EmbeddingProviderPort,
        vector_store: VectorStorePort,
    ) -> None:
        self.document_repo = document_repo
        self.access_service = access_service
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def retrieve_authorized_chunks(
        self,
        query: KnowledgeRetrievalQuery,
    ) -> list[KnowledgeRetrievedChunk]:
        """
        Execute pre-authorized vector retrieval.
        Workflow:
        1. Find all candidate published/active documents in tenant.
        2. Evaluate actor authorization before querying vector store.
        3. Scopes vector query strictly to authorized document IDs.
        4. Apply expiration and source precedence checks.
        """
        now = datetime.now(tz=UTC)

        # 1. Fetch tenant documents
        all_docs = await self.document_repo.list_documents(query.organization_id)

        # Filter active / published status (unless query explicitly allows historical)
        candidate_docs: list[KnowledgeDocument] = []
        for doc in all_docs:
            if not query.include_historical:
                if doc.status not in [DocumentStatus.PUBLISHED, DocumentStatus.INDEXED]:
                    continue
                if doc.expires_at and doc.expires_at < now:
                    continue
                if doc.effective_at and doc.effective_at > now:
                    continue
            if query.filter_document_types and doc.document_type not in query.filter_document_types:
                continue
            candidate_docs.append(doc)

        if not candidate_docs:
            logger.info(f"No active candidate documents for org [{query.organization_id}]")
            return []

        # 2. PRE-RETRIEVAL AUTHORIZATION FILTERING
        authorized_docs = await self.access_service.filter_accessible_documents(
            documents=candidate_docs,
            actor_id=query.actor_id,
            actor_roles=query.actor_roles,
            actor_department_id=query.actor_department_id,
            agent_id=query.agent_id,
            agent_capabilities=query.agent_capabilities,
        )

        if not authorized_docs:
            logger.warning(
                f"Actor [{query.actor_id}] lacks authorization for any candidate documents in org [{query.organization_id}]"
            )
            return []

        authorized_doc_ids = [d.document_id for d in authorized_docs]
        doc_map = {d.document_id: d for d in authorized_docs}

        # 3. Vector Similarity Search
        query_emb = await self.embedding_provider.embed_query(query.query_text)
        search_results = await self.vector_store.query_similar(
            organization_id=query.organization_id,
            query_embedding=query_emb,
            top_k=query.top_k,
            min_score=query.min_similarity_score,
            filter_document_ids=authorized_doc_ids,
        )

        # 4. Assemble Retrieved Chunks with Document Metadata
        retrieved_chunks: list[KnowledgeRetrievedChunk] = []
        for sr in search_results:
            if sr.chunk.document_id in doc_map:
                doc = doc_map[sr.chunk.document_id]
                retrieved_chunks.append(
                    KnowledgeRetrievedChunk(
                        chunk=sr.chunk,
                        similarity_score=sr.score,
                        document_title=doc.title,
                        source_type=doc.source_type,
                    )
                )

        return retrieved_chunks
