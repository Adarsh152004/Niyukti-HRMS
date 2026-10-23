# Program 21: AI Runtime, LLM Gateway & Provider Cascade

## 1. Multi-Provider Gateway & Key Management
- **Environment Resolution**: Reads `GEMINI_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`, `OPENAI_API_KEY`, and `ANTHROPIC_API_KEY` from `.env`.
- **Primary Live Provider**: Google Gemini (`gemini-1.5-flash`).
- **Secondary Live Provider**: Groq (`llama-3.3-70b-versatile`).
- **Safe Offline Fallback**: `MockLLMProvider` ensuring 100% deterministic test execution.

---

## 2. Context Window & Token Budgeting

$$\text{Total Budget} = 8,192 \text{ Tokens}$$

| Context Slice | Allocation (Tokens) | Priority | Truncation Behavior |
|---|---|---|---|
| System & Security Rules | 1,024 | 1 (Highest) | Never Truncate |
| Actor & Tenant Context | 512 | 1 (Highest) | Never Truncate |
| Active Policy Constraints | 1,024 | 1 (Highest) | Never Truncate |
| User Prompt | 1,024 | 2 (High) | Never Truncate |
| RAG Citations & Chunks | 2,048 | 3 (Medium) | Cosine Relevance Truncation |
| Agent Memory (7-Tier) | 1,536 | 4 (Standard) | Semantic Recency Truncation |
| Tool Schemas & Output | 1,024 | 5 (Standard) | Output Compression |
