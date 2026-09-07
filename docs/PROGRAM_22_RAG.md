# Program 22: RAG Knowledge Brain, Verifiable Citations & Security

## 1. End-to-End Document Ingestion & Retrieval Pipeline

```text
UPLOAD → OBJECT STORAGE → FILE VALIDATION → PARSING → CHUNKING → CLASSIFICATION
   ↓
EMBEDDING → VECTOR STORAGE (pgvector) → PRE-RETRIEVAL ROLE CHECK → RERANKING
   ↓
PROMPT FIREWALL (Injection Sanitization) → VERIFIABLE CITATION → LLM CONTEXT
```

---

## 2. Citation Integrity
Every AI answer derived from corporate policies provides:
- Document Title (e.g., *Policy POL-BEN-LV-01: Parental Leave*)
- Document Version (e.g., *v3.2*)
- Exact Page / Section (e.g., *Section 4.1, Page 4*)
