"""
Supabase Cloud Database Client Integration.
Persists:
- Chat Messages (AI Workspace Chat, CEO Mobile Chat, Command Center)
- Multi-Agent Orchestration Telemetry & Execution Traces
- Standing Enterprise Workflows & DAG State
"""

from __future__ import annotations
import os
import json
import datetime
from typing import Any, Dict, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xupugosdaxcvbpdeokac.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

HEADERS = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}


class SupabaseDB:
    """Async wrapper for Supabase REST endpoints."""

    @staticmethod
    async def save_chat_message(
        channel: str,
        role: str,
        content: str,
        session_id: str = "default_session",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Persist a chat message to Supabase."""
        if not SUPABASE_SERVICE_ROLE_KEY:
            return False
        url = f"{SUPABASE_URL}/rest/v1/chat_messages"
        payload = {
            "session_id": session_id,
            "channel": channel,
            "role": role,
            "content": content,
            "metadata": json.dumps(metadata or {}),
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(url, headers=HEADERS, json=payload)
                return res.status_code in (200, 201)
        except Exception:
            return False

    @staticmethod
    async def log_orchestration_run(wf_record: Dict[str, Any]) -> bool:
        """Log full multi-agent orchestration execution trace to Supabase."""
        if not SUPABASE_SERVICE_ROLE_KEY:
            return False
        url = f"{SUPABASE_URL}/rest/v1/orchestration_runs"
        payload = {
            "query_id": wf_record.get("query_id"),
            "query": wf_record.get("query"),
            "initiator": wf_record.get("initiator"),
            "channel": wf_record.get("channel"),
            "intent": wf_record.get("intent"),
            "status": wf_record.get("status"),
            "duration_ms": wf_record.get("duration_ms", 0),
            "llm_provider": wf_record.get("llm_provider"),
            "final_answer": wf_record.get("final_answer", ""),
            "nodes_json": json.dumps(wf_record.get("nodes", [])),
            "created_at": wf_record.get("timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat())
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(url, headers=HEADERS, json=payload)
                return res.status_code in (200, 201)
        except Exception:
            return False

    @staticmethod
    async def get_orchestration_history(limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """Fetch orchestration history from Supabase."""
        if not SUPABASE_SERVICE_ROLE_KEY:
            return None
        url = f"{SUPABASE_URL}/rest/v1/orchestration_runs?select=*&order=created_at.desc&limit={limit}"
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(url, headers=HEADERS)
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return None
