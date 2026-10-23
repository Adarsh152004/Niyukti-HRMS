"""
MongoDB Atlas Client Integration.
Stores flexible document data:
- Company Hierarchy, Organizations, Departments
- Client CRM, Contacts, Requirements, Quotations
- Projects, Milestones, Tasks
"""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_CONNECTION_STRING", "")
DB_NAME = "hrms_enterprise"

_client: Optional[AsyncIOMotorClient] = None


def get_mongo_db():
    global _client
    if not MONGO_URI or "<db_username>" in MONGO_URI:
        return None
    if _client is None:
        try:
            _client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        except Exception:
            return None
    return _client[DB_NAME]


class MongoDB:
    @staticmethod
    async def insert_document(collection: str, doc: Dict[str, Any]) -> bool:
        db = get_mongo_db()
        if db is None:
            return False
        try:
            await db[collection].insert_one(doc)
            return True
        except Exception:
            return False

    @staticmethod
    async def find_documents(collection: str, query: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        db = get_mongo_db()
        if db is None:
            return []
        try:
            cursor = db[collection].find(query).limit(limit)
            docs = await cursor.to_list(length=limit)
            for d in docs:
                if "_id" in d:
                    d["_id"] = str(d["_id"])
            return docs
        except Exception:
            return []
