# AI-Powered Intelligent HRMS — RAG Security, Citations & Document Intelligence

## 1. RAG Ingestion & Query Security Pipeline

```text
[Document Upload] (PDF / DOCX / TXT)
       │
       ▼
[MIME & Path Sanitization] (Magic byte inspection + anti-path traversal)
       │
       ▼
[Classification & Tenant Tagging] (Strict organization_id & sensitivity label)
       │
       ▼
[Text Chunking & Embedding] (1,024-token chunks with 10% overlap)
       │
       ▼
[Vector Store Partition] (Isolated by tenant_id & department_scope)
       │
       ▼
[Query Time: Authorization Pre-Filter] (Verify actor roles BEFORE similarity search)
       │
       ▼
[Vector Cosine Retrieval]
       │
       ▼
[Context Prompt Firewall] (Neutralize prompt injections in untrusted document text)
       │
       ▼
[LLM Reasoning & Verifiable Citation Generation]
```

---

## 2. Citation Requirements
Every AI-generated answer derived from company knowledge must provide verifiable source citations:
- **`document_id`**: Canonical document registry identifier.
- **`document_title`**: Official document name (e.g. `Policy POL-BEN-LV-01: Parental Leave`).
- **`version`**: Document version (e.g. `v3.2`).
- **`page_or_section`**: Explicit page number or section header.
- **`chunk_id`**: Unique vector index chunk identifier.

*Hallucinated or fabricated citations are strictly prohibited by runtime validator.*
