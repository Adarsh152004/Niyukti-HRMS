"""
Knowledge Service — Master façade orchestrating all knowledge brain operations.
"""

from __future__ import annotations

from backend.ai.gateway.router import AIGatewayRouter
from backend.knowledge.application.access_service import KnowledgeAccessService
from backend.knowledge.application.evaluation_service import KnowledgeEvaluationService
from backend.knowledge.application.indexing_service import KnowledgeIndexingService
from backend.knowledge.application.ingestion_service import DocumentIngestionService
from backend.knowledge.application.quality_service import KnowledgeQualityService
from backend.knowledge.application.rag_service import KnowledgeRAGService
from backend.knowledge.application.retention_service import KnowledgeRetentionService
from backend.knowledge.application.retrieval_service import KnowledgeRetrievalService
from backend.knowledge.application.versioning_service import KnowledgeVersioningService
from backend.knowledge.domain.enums import (
    DocumentType,
    KnowledgeClassification,
    SourceType,
)
from backend.knowledge.domain.models import (
    KnowledgeAccessPolicy,
    KnowledgeAnswer,
    KnowledgeDocument,
    KnowledgeQualityReport,
    KnowledgeRetrievalQuery,
    KnowledgeRetrievedChunk,
)
from backend.knowledge.infrastructure.database.repositories import (
    InMemoryKnowledgeAccessPolicyRepository,
    InMemoryKnowledgeChunkRepository,
    InMemoryKnowledgeDocumentRepository,
    InMemoryKnowledgeIndexRecordRepository,
)
from backend.knowledge.infrastructure.embeddings.gateway_embedding_adapter import (
    GatewayEmbeddingAdapter,
)
from backend.knowledge.infrastructure.parsers.pdf_parser import PDFDocumentParser
from backend.knowledge.infrastructure.parsers.text_parser import TextDocumentParser
from backend.knowledge.infrastructure.vectorstores.in_memory_vector_store import (
    InMemoryVectorStore,
)
from backend.knowledge.ports.document_parser import DocumentParserPort
from backend.knowledge.ports.embedding_provider import EmbeddingProviderPort
from backend.knowledge.ports.repositories import (
    KnowledgeAccessPolicyRepositoryPort,
    KnowledgeChunkRepositoryPort,
    KnowledgeDocumentRepositoryPort,
    KnowledgeIndexRecordRepositoryPort,
)
from backend.knowledge.ports.vector_store import VectorStorePort


class KnowledgeService:
    """Master service controller for Knowledge Brain and RAG operations."""

    _instance: KnowledgeService | None = None

    def __init__(
        self,
        document_repo: KnowledgeDocumentRepositoryPort | None = None,
        chunk_repo: KnowledgeChunkRepositoryPort | None = None,
        policy_repo: KnowledgeAccessPolicyRepositoryPort | None = None,
        index_record_repo: KnowledgeIndexRecordRepositoryPort | None = None,
        embedding_provider: EmbeddingProviderPort | None = None,
        vector_store: VectorStorePort | None = None,
        parsers: list[DocumentParserPort] | None = None,
    ) -> None:
        self.document_repo = document_repo or InMemoryKnowledgeDocumentRepository()
        self.chunk_repo = chunk_repo or InMemoryKnowledgeChunkRepository()
        self.policy_repo = policy_repo or InMemoryKnowledgeAccessPolicyRepository()
        self.index_record_repo = index_record_repo or InMemoryKnowledgeIndexRecordRepository()
        self.embedding_provider = embedding_provider or GatewayEmbeddingAdapter()
        self.vector_store = vector_store or InMemoryVectorStore.get_instance()
        self.parsers = parsers or [TextDocumentParser(), PDFDocumentParser()]

        # Initialize core application services
        self.access_service = KnowledgeAccessService(policy_repo=self.policy_repo)
        self.indexing_service = KnowledgeIndexingService(
            chunk_repo=self.chunk_repo,
            index_record_repo=self.index_record_repo,
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
        )
        self.ingestion_service = DocumentIngestionService(
            document_repo=self.document_repo,
            policy_repo=self.policy_repo,
            indexing_service=self.indexing_service,
            parsers=self.parsers,
        )
        self.retrieval_service = KnowledgeRetrievalService(
            document_repo=self.document_repo,
            access_service=self.access_service,
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
        )
        self.rag_service = KnowledgeRAGService(
            retrieval_service=self.retrieval_service,
            ai_gateway_router=AIGatewayRouter.get_instance(),
        )
        self.versioning_service = KnowledgeVersioningService(
            document_repo=self.document_repo,
            indexing_service=self.indexing_service,
            parsers=self.parsers,
        )
        self.retention_service = KnowledgeRetentionService(
            document_repo=self.document_repo,
            chunk_repo=self.chunk_repo,
            vector_store=self.vector_store,
        )
        self.quality_service = KnowledgeQualityService(document_repo=self.document_repo)
        self.evaluation_service = KnowledgeEvaluationService(retrieval_service=self.retrieval_service)

    @classmethod
    def get_instance(cls) -> KnowledgeService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # Convenience Façade Methods
    async def upload_and_index_document(
        self,
        organization_id: str,
        title: str,
        content_bytes: bytes,
        owner_id: str,
        mime_type: str = "text/plain",
        source_type: SourceType = SourceType.HR_POLICY,
        document_type: DocumentType = DocumentType.POLICY,
        classification: KnowledgeClassification = KnowledgeClassification.INTERNAL,
        description: str = "",
        auto_publish: bool = True,
    ) -> KnowledgeDocument:
        return await self.ingestion_service.ingest_document(
            organization_id=organization_id,
            title=title,
            content_bytes=content_bytes,
            owner_id=owner_id,
            mime_type=mime_type,
            source_type=source_type,
            document_type=document_type,
            classification=classification,
            description=description,
            auto_publish=auto_publish,
        )

    async def retrieve_chunks(self, query: KnowledgeRetrievalQuery) -> list[KnowledgeRetrievedChunk]:
        return await self.retrieval_service.retrieve_authorized_chunks(query)

    async def answer_rag_query(self, query: KnowledgeRetrievalQuery) -> KnowledgeAnswer:
        return await self.rag_service.answer_query(query)

    async def configure_access_policy(self, policy: KnowledgeAccessPolicy) -> KnowledgeAccessPolicy:
        return await self.policy_repo.save_policy(policy)

    async def archive_document(self, organization_id: str, document_id: str, reason: str = "") -> KnowledgeDocument:
        return await self.retention_service.archive_document(organization_id, document_id, reason)

    async def get_quality_report(self, organization_id: str) -> KnowledgeQualityReport:
        return await self.quality_service.generate_quality_report(organization_id)
