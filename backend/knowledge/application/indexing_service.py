"""
Knowledge Indexing Service — Deterministic chunking, embedding generation, and vector indexing.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from backend.knowledge.domain.enums import IndexStatus
from backend.knowledge.domain.models import (
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeIndexRecord,
)
from backend.knowledge.ports.document_parser import ParsedDocument
from backend.knowledge.ports.embedding_provider import EmbeddingProviderPort
from backend.knowledge.ports.repositories import (
    KnowledgeChunkRepositoryPort,
    KnowledgeIndexRecordRepositoryPort,
)
from backend.knowledge.ports.vector_store import VectorStorePort

logger = logging.getLogger(__name__)


class KnowledgeIndexingService:
    """Chunks parsed documents, creates vector embeddings, and synchronizes vector store."""

    def __init__(
        self,
        chunk_repo: KnowledgeChunkRepositoryPort,
        index_record_repo: KnowledgeIndexRecordRepositoryPort,
        embedding_provider: EmbeddingProviderPort,
        vector_store: VectorStorePort,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> None:
        self.chunk_repo = chunk_repo
        self.index_record_repo = index_record_repo
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_parsed_document(
        self,
        document: KnowledgeDocument,
        version_number: int,
        parsed_doc: ParsedDocument,
    ) -> list[KnowledgeChunk]:
        """Split document sections into deterministic chunks with metadata."""
        chunks: list[KnowledgeChunk] = []
        chunk_idx = 0

        for section in parsed_doc.sections:
            sec_text = section.content.strip()
            if not sec_text:
                continue

            # Word-based chunking with overlap
            words = sec_text.split()
            if len(words) <= self.chunk_size:
                chunks.append(
                    KnowledgeChunk(
                        document_id=document.document_id,
                        document_version=version_number,
                        organization_id=document.organization_id,
                        chunk_index=chunk_idx,
                        content=sec_text,
                        token_count=len(words),
                        char_length=len(sec_text),
                        section_title=section.section_title,
                        page_number=section.page_number,
                        classification=document.classification,
                    )
                )
                chunk_idx += 1
            else:
                step = self.chunk_size - self.chunk_overlap
                for i in range(0, len(words), step):
                    chunk_words = words[i : i + self.chunk_size]
                    chunk_text = " ".join(chunk_words)
                    chunks.append(
                        KnowledgeChunk(
                            document_id=document.document_id,
                            document_version=version_number,
                            organization_id=document.organization_id,
                            chunk_index=chunk_idx,
                            content=chunk_text,
                            token_count=len(chunk_words),
                            char_length=len(chunk_text),
                            section_title=section.section_title,
                            page_number=section.page_number,
                            classification=document.classification,
                        )
                    )
                    chunk_idx += 1

        return chunks

    async def index_document_version(
        self,
        document: KnowledgeDocument,
        version_number: int,
        parsed_doc: ParsedDocument,
    ) -> Sequence[KnowledgeChunk]:
        """Chunk, embed, and index a document version."""
        logger.info(f"Indexing document [{document.document_id}] v{version_number} for org [{document.organization_id}]")

        # 1. Chunk document
        chunks = self.chunk_parsed_document(document, version_number, parsed_doc)
        if not chunks:
            logger.warning(f"No content chunks extracted for document [{document.document_id}]")
            return []

        # 2. Generate embeddings
        texts = [c.content for c in chunks]
        embeddings = await self.embedding_provider.embed_documents(texts)
        for c, emb in zip(chunks, embeddings, strict=False):
            c.embedding = emb

        # 3. Purge previous chunks for same version to maintain idempotency
        await self.vector_store.delete_chunks_for_document(
            organization_id=document.organization_id,
            document_id=document.document_id,
            version_number=version_number,
        )
        await self.chunk_repo.delete_chunks(
            organization_id=document.organization_id,
            document_id=document.document_id,
            version_number=version_number,
        )

        # 4. Save chunks to metadata repository and vector store
        saved_chunks = await self.chunk_repo.save_chunks(chunks)
        await self.vector_store.upsert_chunks(saved_chunks)

        # 5. Record index sync
        index_rec = KnowledgeIndexRecord(
            document_id=document.document_id,
            version_number=version_number,
            organization_id=document.organization_id,
            chunk_count=len(saved_chunks),
            status=IndexStatus.INDEXED,
        )
        await self.index_record_repo.save_index_record(index_rec)

        return saved_chunks
