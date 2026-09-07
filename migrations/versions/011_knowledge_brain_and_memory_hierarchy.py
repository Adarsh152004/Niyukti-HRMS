"""Knowledge Brain and Memory Hierarchy Tables

Revision ID: 011_knowledge_brain_and_memory_hierarchy
Revises: 010_agent_safety_control_plane
Create Date: 2026-08-27 16:45:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "011_knowledge_brain_and_memory_hierarchy"
down_revision = "010_agent_safety_control_plane"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Knowledge Documents ────────────────────────────────────────────────
    op.create_table(
        "knowledge_documents",
        sa.Column("document_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(64), nullable=False),
        sa.Column("document_type", sa.String(64), nullable=False),
        sa.Column("classification", sa.String(64), nullable=False),
        sa.Column("owner_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, default="UPLOADED"),
        sa.Column("current_version", sa.Integer(), nullable=False, default=1),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("mime_type", sa.String(64), nullable=False),
        sa.Column("storage_reference", sa.String(512), nullable=False),
        sa.Column("language", sa.String(16), nullable=False, default="en"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── 2. Knowledge Document Versions ────────────────────────────────────────
    op.create_table(
        "knowledge_document_versions",
        sa.Column("version_id", sa.String(64), primary_key=True),
        sa.Column("document_id", sa.String(64), nullable=False, index=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("storage_reference", sa.String(512), nullable=False),
        sa.Column("author_id", sa.String(64), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── 3. Knowledge Chunks ───────────────────────────────────────────────────
    op.create_table(
        "knowledge_chunks",
        sa.Column("chunk_id", sa.String(64), primary_key=True),
        sa.Column("document_id", sa.String(64), nullable=False, index=True),
        sa.Column("document_version", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False, default=0),
        sa.Column("char_length", sa.Integer(), nullable=False, default=0),
        sa.Column("section_title", sa.String(255), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("classification", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── 4. Knowledge Access Policies ──────────────────────────────────────────
    op.create_table(
        "knowledge_access_policies",
        sa.Column("policy_id", sa.String(64), primary_key=True),
        sa.Column("document_id", sa.String(64), nullable=False, index=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("scope_type", sa.String(64), nullable=False),
        sa.Column("allowed_roles", sa.JSON(), nullable=False, default=list),
        sa.Column("allowed_departments", sa.JSON(), nullable=False, default=list),
        sa.Column("allowed_capabilities", sa.JSON(), nullable=False, default=list),
        sa.Column("allowed_employee_ids", sa.JSON(), nullable=False, default=list),
        sa.Column("max_classification", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── 5. Hierarchical Memory Records ────────────────────────────────────────
    op.create_table(
        "hierarchical_memory_records",
        sa.Column("memory_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("tier", sa.String(32), nullable=False, index=True),
        sa.Column("memory_type", sa.String(64), nullable=False),
        sa.Column("classification", sa.String(64), nullable=False),
        sa.Column("agent_id", sa.String(64), nullable=True, index=True),
        sa.Column("team_id", sa.String(64), nullable=True, index=True),
        sa.Column("employee_id", sa.String(64), nullable=True, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("importance_score", sa.Float(), nullable=False, default=1.0),
        sa.Column("source_reference", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta_data", sa.JSON(), nullable=False, default=dict),
    )


def downgrade() -> None:
    op.drop_table("hierarchical_memory_records")
    op.drop_table("knowledge_access_policies")
    op.drop_table("knowledge_chunks")
    op.drop_table("knowledge_document_versions")
    op.drop_table("knowledge_documents")
