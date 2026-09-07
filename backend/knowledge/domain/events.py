"""
Knowledge Domain Events — Emitted to EventBus for ingestion, indexing, retrieval, and retention workflows.
"""

from __future__ import annotations

from backend.runtime.events import Event


class KnowledgeDocumentUploaded(Event):
    def __init__(self, organization_id: str, document_id: str, title: str, uploader_id: str) -> None:
        super().__init__(
            event_type="knowledge.document.uploaded",
            source="knowledge.ingestion",
            payload={
                "organization_id": organization_id,
                "document_id": document_id,
                "title": title,
                "uploader_id": uploader_id,
            },
        )


class KnowledgeDocumentIndexed(Event):
    def __init__(self, organization_id: str, document_id: str, version: int, chunk_count: int) -> None:
        super().__init__(
            event_type="knowledge.document.indexed",
            source="knowledge.indexing",
            payload={
                "organization_id": organization_id,
                "document_id": document_id,
                "version": version,
                "chunk_count": chunk_count,
            },
        )


class KnowledgeDocumentPublished(Event):
    def __init__(self, organization_id: str, document_id: str, version: int, publisher_id: str) -> None:
        super().__init__(
            event_type="knowledge.document.published",
            source="knowledge.lifecycle",
            payload={
                "organization_id": organization_id,
                "document_id": document_id,
                "version": version,
                "publisher_id": publisher_id,
            },
        )


class KnowledgeDocumentArchived(Event):
    def __init__(self, organization_id: str, document_id: str, reason: str) -> None:
        super().__init__(
            event_type="knowledge.document.archived",
            source="knowledge.lifecycle",
            payload={
                "organization_id": organization_id,
                "document_id": document_id,
                "reason": reason,
            },
        )


class KnowledgeDocumentExpired(Event):
    def __init__(self, organization_id: str, document_id: str) -> None:
        super().__init__(
            event_type="knowledge.document.expired",
            source="knowledge.retention",
            payload={"organization_id": organization_id, "document_id": document_id},
        )


class KnowledgeDocumentReindexed(Event):
    def __init__(self, organization_id: str, document_id: str, version: int) -> None:
        super().__init__(
            event_type="knowledge.document.reindexed",
            source="knowledge.indexing",
            payload={"organization_id": organization_id, "document_id": document_id, "version": version},
        )


class KnowledgeRetrievalPerformed(Event):
    def __init__(
        self,
        organization_id: str,
        actor_id: str,
        agent_id: str | None,
        retrieved_count: int,
        query_text: str,
    ) -> None:
        # Note: Query is truncated and PII-sanitized before embedding in payload
        super().__init__(
            event_type="knowledge.retrieval.performed",
            source="knowledge.retrieval",
            payload={
                "organization_id": organization_id,
                "actor_id": actor_id,
                "agent_id": agent_id,
                "retrieved_count": retrieved_count,
                "query_preview": query_text[:60],
            },
        )


class KnowledgeRetrievalDenied(Event):
    def __init__(self, organization_id: str, actor_id: str, document_id: str, reason: str) -> None:
        super().__init__(
            event_type="knowledge.retrieval.denied",
            source="knowledge.access",
            payload={
                "organization_id": organization_id,
                "actor_id": actor_id,
                "document_id": document_id,
                "reason": reason,
            },
        )


class KnowledgeAnswerGenerated(Event):
    def __init__(self, organization_id: str, actor_id: str, citation_count: int, abstained: bool) -> None:
        super().__init__(
            event_type="knowledge.answer.generated",
            source="knowledge.rag",
            payload={
                "organization_id": organization_id,
                "actor_id": actor_id,
                "citation_count": citation_count,
                "abstained": abstained,
            },
        )
