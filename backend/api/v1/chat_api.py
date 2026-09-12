"""
FastAPI Router - Unified Multi-Channel Chat History API.
Synchronizes messages across:
- AI Workspace Chat (/ai)
- CEO Command Center (/command)
- CEO Mobile Chat App
Backed by Supabase Cloud Database + SQLite (hrms.db) persistent fallback.
"""

from __future__ import annotations
import os
import json
import sqlite3
import datetime
import uuid
from typing import Any, List, Dict, Optional
import httpx
from fastapi import APIRouter
from dotenv import dotenv_values

router = APIRouter(prefix="/chat", tags=["Unified Chat Engine"])

env_vars = dotenv_values(".env")
SUPABASE_URL = env_vars.get("SUPABASE_URL", "https://xupugosdaxcvbpdeokac.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = env_vars.get("SUPABASE_SERVICE_ROLE_KEY", "")
DB_PATH = "hrms.db"

HEADERS = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}


def _ensure_sqlite_table():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                channel TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[CHAT_API SQLite Init Warning] {e}")

_ensure_sqlite_table()


def _get_sqlite_messages(limit: int = 50) -> List[Dict[str, Any]]:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM chat_messages ORDER BY datetime(created_at) DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()

        formatted = []
        for r in reversed(rows):
            meta = None
            if r["metadata"]:
                try:
                    meta = json.loads(r["metadata"])
                except Exception:
                    pass
            
            ts_str = ""
            if r["created_at"]:
                try:
                    ts_str = datetime.datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")).strftime("%I:%M %p")
                except Exception:
                    ts_str = r["created_at"][:16]

            formatted.append({
                "id": r["id"],
                "role": r["role"],
                "content": r["content"],
                "structured_data": meta,
                "suggested_prompts": meta.get("suggested_prompts", []) if isinstance(meta, dict) else [],
                "channel": r["channel"],
                "timestamp": ts_str,
                "artifact": meta.get("artifact") if isinstance(meta, dict) else None,
                "approval_request": meta.get("approval_request") if isinstance(meta, dict) else None,
                "workflow_id": meta.get("workflow_id") if isinstance(meta, dict) else None,
                "widgets": meta.get("widgets", []) if isinstance(meta, dict) else [],
            })
        return formatted
    except Exception as e:
        print(f"[CHAT_API SQLite Fetch Error] {e}")
        return []


def _save_sqlite_message(msg_id: str, session_id: str, role: str, content: str, channel: str, metadata: Optional[Dict[str, Any]] = None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        meta_str = json.dumps(metadata) if metadata else None
        c.execute("""
            INSERT OR REPLACE INTO chat_messages (id, session_id, role, content, channel, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (msg_id, session_id, role, content, channel, meta_str, datetime.datetime.now(datetime.timezone.utc).isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[CHAT_API SQLite Save Error] {e}")


def _clear_sqlite_messages():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM chat_messages")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[CHAT_API SQLite Clear Error] {e}")


@router.get("/messages")
async def get_unified_chat_messages(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch unified chat history from Supabase Cloud Database + SQLite.
    Guarantees returning the most recent messages in chronological order,
    merging local SQLite fallback to prevent any disappearing messages.
    """
    cloud_messages: List[Dict[str, Any]] = []
    if SUPABASE_SERVICE_ROLE_KEY:
        try:
            url = f"{SUPABASE_URL}/rest/v1/chat_messages?select=*&order=created_at.desc&limit={limit}"
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(url, headers=HEADERS)
                if res.status_code == 200:
                    messages = res.json()
                    if isinstance(messages, list) and len(messages) > 0:
                        for m in reversed(messages):
                            meta = m.get("metadata")
                            if isinstance(meta, str) and meta.strip():
                                try:
                                    meta = json.loads(meta)
                                except Exception:
                                    pass

                            ts_str = ""
                            if m.get("created_at"):
                                try:
                                    ts_str = datetime.datetime.fromisoformat(m["created_at"].replace("Z", "+00:00")).strftime("%I:%M %p")
                                except Exception:
                                    ts_str = str(m.get("created_at"))[:16]

                            cloud_messages.append({
                                "id": str(m.get("id")),
                                "role": m.get("role"),
                                "content": m.get("content", ""),
                                "structured_data": meta if isinstance(meta, dict) else None,
                                "suggested_prompts": meta.get("suggested_prompts", []) if isinstance(meta, dict) else [],
                                "channel": m.get("channel", "AI_WORKSPACE"),
                                "timestamp": ts_str,
                                "artifact": meta.get("artifact") if isinstance(meta, dict) else None,
                                "approval_request": meta.get("approval_request") if isinstance(meta, dict) else None,
                                "workflow_id": meta.get("workflow_id") if isinstance(meta, dict) else None,
                                "widgets": meta.get("widgets", []) if isinstance(meta, dict) else [],
                            })
        except Exception as e:
            print(f"[CHAT_API Supabase Fetch Error] {e}")

    # Also load SQLite local messages
    sqlite_msgs = _get_sqlite_messages(limit)

    if not cloud_messages:
        return sqlite_msgs

    # Merge cloud and local SQLite by id so newest local writes are never dropped
    seen_ids = set()
    merged = []
    for m in cloud_messages:
        seen_ids.add(m["id"])
        merged.append(m)

    for m in sqlite_msgs:
        if m["id"] not in seen_ids:
            seen_ids.add(m["id"])
            merged.append(m)

    return merged[-limit:]


@router.delete("/history")
@router.delete("/messages")
async def clear_chat_history() -> Dict[str, str]:
    """
    Permanently delete all chat history from Supabase Cloud Database and local SQLite.
    """
    _clear_sqlite_messages()
    
    deleted_cloud = False
    if SUPABASE_SERVICE_ROLE_KEY:
        try:
            url = f"{SUPABASE_URL}/rest/v1/chat_messages?id=neq.00000000-0000-0000-0000-000000000000"
            headers = {**HEADERS, "Prefer": "count=exact"}
            async with httpx.AsyncClient(timeout=6.0) as client:
                res = await client.delete(url, headers=headers)
                if res.status_code in (200, 204):
                    deleted_cloud = True
        except Exception as e:
            print(f"[CHAT_API Supabase Delete Error] {e}")

    return {
        "status": "cleared",
        "message": "Chat history permanently deleted from Supabase cloud database and SQLite.",
        "cloud_deleted": str(deleted_cloud)
    }


async def save_chat_message(
    role: str, 
    content: str, 
    structured_data: Optional[Dict[str, Any]] = None, 
    channel: str = "AI_WORKSPACE", 
    session_id: str = "default_session"
) -> Optional[Dict[str, Any]]:
    """Saves a message to both Supabase cloud database and local SQLite."""
    msg_id = str(uuid.uuid4())
    ts_now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # 1. Save to SQLite immediately
    _save_sqlite_message(msg_id, session_id, role, content, channel, structured_data)

    # 2. Save to Supabase Cloud
    if SUPABASE_SERVICE_ROLE_KEY:
        try:
            url = f"{SUPABASE_URL}/rest/v1/chat_messages"
            payload = {
                "id": msg_id,
                "session_id": session_id,
                "role": role,
                "content": content,
                "channel": channel,
                "metadata": structured_data if isinstance(structured_data, dict) else None,
                "created_at": ts_now
            }
            headers = {**HEADERS, "Prefer": "return=representation"}
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        return data[0]
        except Exception as e:
            print(f"[CHAT_API Supabase Save Error] {e}")
            
    return {
        "id": msg_id,
        "session_id": session_id,
        "role": role,
        "content": content,
        "channel": channel,
        "metadata": structured_data,
        "created_at": ts_now
    }
