"""
Knowledge API Router — REST endpoints for documents, semantic search, RAG, and memory.
"""

from __future__ import annotations

from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.agents.memory.domain.enums import MemoryType
from backend.agents.memory.hierarchy.enums import MemoryTier
from backend.agents.memory.hierarchy.models import HierarchicalMemoryRecord
from backend.agents.memory.hierarchy.service import HierarchicalMemoryService
from backend.hrms.domain.actor import Actor
from backend.knowledge.application.knowledge_service import KnowledgeService
from backend.knowledge.domain.enums import (
    DocumentStatus,
    DocumentType,
    KnowledgeClassification,
    SourceType,
)
from backend.knowledge.domain.models import (
    KnowledgeAnswer,
    KnowledgeDocument,
    KnowledgeQualityReport,
    KnowledgeRetrievalQuery,
    KnowledgeRetrievedChunk,
)
from backend.security.api.dependencies import get_current_actor

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge Brain"])
memory_router = APIRouter(prefix="/api/v1/memory", tags=["Memory Hierarchy"])


class DocumentUploadRequest(BaseModel):
    title: str
    content: str
    description: str = ""
    source_type: SourceType = SourceType.HR_POLICY
    document_type: DocumentType = DocumentType.POLICY
    classification: KnowledgeClassification = KnowledgeClassification.INTERNAL
    mime_type: str = "text/plain"
    auto_publish: bool = True


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=50)
    min_score: float = Field(default=0.50, ge=0.0, le=1.0)


class RAGAnswerRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)


class WriteMemoryRequest(BaseModel):
    tier: MemoryTier
    content: str
    memory_type: MemoryType = MemoryType.OBSERVATION
    classification: KnowledgeClassification = KnowledgeClassification.INTERNAL
    agent_id: str | None = None
    team_id: str | None = None
    employee_id: str | None = None
    importance_score: float = 1.0


# ── Knowledge Endpoints ────────────────────────────────────────────────────────


@router.post("/documents", response_model=KnowledgeDocument, status_code=status.HTTP_201_CREATED)
async def upload_document(
    req: DocumentUploadRequest,
    actor: Actor = Depends(get_current_actor),
) -> KnowledgeDocument:
    svc = KnowledgeService.get_instance()
    doc = await svc.upload_and_index_document(
        organization_id=actor.organization_id,
        title=req.title,
        content_bytes=req.content.encode("utf-8"),
        owner_id=actor.actor_id,
        mime_type=req.mime_type,
        source_type=req.source_type,
        document_type=req.document_type,
        classification=req.classification,
        description=req.description,
        auto_publish=req.auto_publish,
    )
    return doc


@router.get("/documents", response_model=Sequence[KnowledgeDocument])
async def list_documents(
    status_filter: DocumentStatus | None = None,
    actor: Actor = Depends(get_current_actor),
) -> Sequence[KnowledgeDocument]:
    svc = KnowledgeService.get_instance()
    return await svc.document_repo.list_documents(actor.organization_id, status=status_filter)


@router.get("/documents/{document_id}", response_model=KnowledgeDocument)
async def get_document(
    document_id: str,
    actor: Actor = Depends(get_current_actor),
) -> KnowledgeDocument:
    svc = KnowledgeService.get_instance()
    doc = await svc.document_repo.get_document(actor.organization_id, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc


@router.post("/documents/{document_id}/archive", response_model=KnowledgeDocument)
async def archive_document(
    document_id: str,
    reason: str = "Manual archival",
    actor: Actor = Depends(get_current_actor),
) -> KnowledgeDocument:
    svc = KnowledgeService.get_instance()
    return await svc.archive_document(actor.organization_id, document_id, reason=reason)


@router.post("/search", response_model=Sequence[KnowledgeRetrievedChunk])
async def search_knowledge(
    req: SearchRequest,
    actor: Actor = Depends(get_current_actor),
) -> Sequence[KnowledgeRetrievedChunk]:
    svc = KnowledgeService.get_instance()
    query = KnowledgeRetrievalQuery(
        query_text=req.query,
        organization_id=actor.organization_id,
        actor_id=actor.actor_id,
        actor_roles=list(actor.roles),
        top_k=req.top_k,
        min_similarity_score=req.min_score,
    )
    return await svc.retrieve_chunks(query)


@router.post("/answer", response_model=KnowledgeAnswer)
async def get_rag_answer(
    req: RAGAnswerRequest,
    actor: Actor = Depends(get_current_actor),
) -> KnowledgeAnswer:
    svc = KnowledgeService.get_instance()
    query = KnowledgeRetrievalQuery(
        query_text=req.question,
        organization_id=actor.organization_id,
        actor_id=actor.actor_id,
        actor_roles=list(actor.roles),
        top_k=req.top_k,
    )
    return await svc.answer_rag_query(query)


@router.get("/quality", response_model=KnowledgeQualityReport)
async def get_quality_report(
    actor: Actor = Depends(get_current_actor),
) -> KnowledgeQualityReport:
    svc = KnowledgeService.get_instance()
    return await svc.get_quality_report(actor.organization_id)


# ── Memory Endpoints ──────────────────────────────────────────────────────────


@memory_router.post("", response_model=HierarchicalMemoryRecord, status_code=status.HTTP_201_CREATED)
async def write_memory(
    req: WriteMemoryRequest,
    actor: Actor = Depends(get_current_actor),
) -> HierarchicalMemoryRecord:
    mem_svc = HierarchicalMemoryService.get_instance()
    return await mem_svc.write_memory(
        organization_id=actor.organization_id,
        tier=req.tier,
        content=req.content,
        memory_type=req.memory_type,
        classification=req.classification,
        agent_id=req.agent_id,
        team_id=req.team_id,
        employee_id=req.employee_id,
        importance_score=req.importance_score,
    )


@memory_router.get("", response_model=Sequence[HierarchicalMemoryRecord])
async def read_memories(
    tier: MemoryTier = MemoryTier.ORGANIZATION,
    team_id: str | None = None,
    employee_id: str | None = None,
    actor: Actor = Depends(get_current_actor),
) -> Sequence[HierarchicalMemoryRecord]:
    mem_svc = HierarchicalMemoryService.get_instance()
    return await mem_svc.read_memories(
        organization_id=actor.organization_id,
        tier=tier,
        requesting_actor_id=actor.actor_id,
        agent_teams=[team_id] if team_id else None,
        employee_id=employee_id,
    )
