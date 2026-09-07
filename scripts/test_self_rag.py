import sys
import os
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import asyncio

from backend.ai.self_rag_engine import execute_self_rag

async def main():
    q = "What is our company headcount and department breakdown?"
    print("Testing question:", q)
    res = await execute_self_rag(q)
    print("\n=== Self-RAG ANSWER ===")
    print(res["answer"])
    print("=======================")
    print("Support:", res.get("issup"), "| Useful:", res.get("isuse"))

if __name__ == "__main__":
    asyncio.run(main())
