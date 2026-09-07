"""
Knowledge Brain & Memory CLI commands.
"""

from __future__ import annotations

import asyncio

import typer

from backend.agents.memory.hierarchy.enums import MemoryTier
from backend.agents.memory.hierarchy.service import HierarchicalMemoryService
from backend.knowledge.application.knowledge_service import KnowledgeService
from backend.knowledge.domain.models import KnowledgeRetrievalQuery

knowledge_app = typer.Typer(name="knowledge", help="Knowledge Brain management commands")
memory_app = typer.Typer(name="memory", help="Memory hierarchy management commands")


@knowledge_app.command("list")
def list_documents_cmd(org_id: str = typer.Option(..., "--org-id", "-o", help="Organization ID")) -> None:
    """List all knowledge documents for an organization."""
    svc = KnowledgeService.get_instance()
    docs = asyncio.run(svc.document_repo.list_documents(org_id))
    typer.echo(f"=== Knowledge Documents ({len(docs)}) ===")
    for d in docs:
        typer.echo(
            f"[{d.document_id}] {d.title} (v{d.current_version}) - Status: {d.status.value}, Classification: {d.classification.value}"
        )


@knowledge_app.command("search")
def search_knowledge_cmd(
    query: str = typer.Argument(..., help="Search text query"),
    org_id: str = typer.Option(..., "--org-id", "-o", help="Organization ID"),
    actor_id: str = typer.Option("cli-user", "--actor-id", "-a", help="Actor ID"),
    role: str = typer.Option("ADMIN", "--role", "-r", help="Actor Role"),
) -> None:
    """Search knowledge documents with vector similarity."""
    svc = KnowledgeService.get_instance()
    retrieval_query = KnowledgeRetrievalQuery(
        query_text=query,
        organization_id=org_id,
        actor_id=actor_id,
        actor_roles=[role],
        top_k=3,
    )
    chunks = asyncio.run(svc.retrieve_chunks(retrieval_query))
    typer.echo(f"=== Search Results for '{query}' ({len(chunks)}) ===")
    for c in chunks:
        typer.echo(f"Score: {c.similarity_score:.3f} | Doc: {c.document_title} | Section: {c.chunk.section_title or 'General'}")
        typer.echo(f"Excerpt: {c.chunk.content[:160]}...\n")


@knowledge_app.command("answer")
def answer_knowledge_cmd(
    question: str = typer.Argument(..., help="Question to answer using RAG"),
    org_id: str = typer.Option(..., "--org-id", "-o", help="Organization ID"),
    actor_id: str = typer.Option("cli-user", "--actor-id", "-a", help="Actor ID"),
    role: str = typer.Option("ADMIN", "--role", "-r", help="Actor Role"),
) -> None:
    """Answer question with grounded RAG and citations."""
    svc = KnowledgeService.get_instance()
    retrieval_query = KnowledgeRetrievalQuery(
        query_text=question,
        organization_id=org_id,
        actor_id=actor_id,
        actor_roles=[role],
        top_k=3,
    )
    ans = asyncio.run(svc.answer_rag_query(retrieval_query))
    typer.echo("=== RAG Answer ===")
    typer.echo(ans.answer)
    typer.echo(f"\nConfidence: {ans.confidence:.2f} | Abstained: {ans.abstain}")
    if ans.citations:
        typer.echo("--- Citations ---")
        for cit in ans.citations:
            typer.echo(f"- [{cit.document_title} v{cit.document_version}] {cit.snippet}")


@memory_app.command("list")
def list_memory_cmd(
    org_id: str = typer.Option(..., "--org-id", "-o", help="Organization ID"),
    tier: str = typer.Option("ORGANIZATION", "--tier", "-t", help="Memory Tier (AGENT, TEAM, ORGANIZATION, EMPLOYEE)"),
) -> None:
    """List memory records by tier."""
    mem_svc = HierarchicalMemoryService.get_instance()
    mem_tier = MemoryTier(tier.upper())
    records = asyncio.run(
        mem_svc.read_memories(
            organization_id=org_id,
            tier=mem_tier,
            requesting_actor_id="cli-admin",
        )
    )
    typer.echo(f"=== Memory Tier [{tier.upper()}] ({len(records)} records) ===")
    for r in records:
        typer.echo(f"[{r.memory_id}] {r.content[:120]} (Type: {r.memory_type.value})")
