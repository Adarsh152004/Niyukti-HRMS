"""
Firebase Firestore Client Integration.
Provides real-time notifications, presence alerts, and event broadcasts.
"""

from __future__ import annotations
import os
import datetime
from typing import Any, Dict, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import dotenv_values

_app = None
_db = None

def get_firestore_client():
    global _app, _db
    if _db is not None:
        return _db
    
    env_vars = dotenv_values(".env")
    cred_path = env_vars.get("FIREBASE_CREDENTIALS_PATH")
    
    if not cred_path or not os.path.exists(cred_path):
        return None
        
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            _app = firebase_admin.initialize_app(cred)
        else:
            _app = firebase_admin.get_app()
        _db = firestore.client()
        return _db
    except Exception as e:
        print(f"[FIREBASE INITIALIZATION ERROR]: {e}")
        return None


class FirebaseService:
    @staticmethod
    async def send_notification(
        user_id: str,
        title: str,
        body: str,
        category: str = "WORKFLOW",
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a real-time notification document to Firestore."""
        db = get_firestore_client()
        if db is None:
            print(f"[FIREBASE OFFLINE] Notification -> User: {user_id} | {title}: {body}")
            return False

        try:
            doc_ref = db.collection("notifications").document()
            doc_ref.set({
                "id": doc_ref.id,
                "user_id": user_id,
                "title": title,
                "body": body,
                "category": category,
                "data": data or {},
                "read": False,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
            print(f"[FIREBASE LIVE NOTIFICATION] -> ID: {doc_ref.id} | User: {user_id} | Title: {title}")
            return True
        except Exception as e:
            print(f"[FIREBASE SEND ERROR]: {e}")
            return False
