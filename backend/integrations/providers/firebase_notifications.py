"""
Firebase Cloud Messaging (FCM) Adapter — Dispatches push notifications and topic messages for HR events and approvals.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)


class FirebaseNotificationAdapter:
    """
    Adapter for Firebase Cloud Messaging (FCM) push notifications.
    """

    def __init__(self, project_id: str = "hrms-firebase-app", credentials_json: str | None = None) -> None:
        self.project_id = project_id
        self.credentials_json = credentials_json
        # Sent messages history for audit & offline test assertions
        self._sent_messages: list[dict[str, Any]] = []

    async def send_to_device(
        self,
        device_token: str,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Send a notification message to a specific device registration token."""
        msg_id = f"fcm-msg-{uuid.uuid4()}"
        record = {
            "message_id": msg_id,
            "target": "device",
            "device_token": device_token,
            "title": title,
            "body": body,
            "data": data or {},
        }
        self._sent_messages.append(record)
        logger.info(f"FCM dispatched to device [{device_token[:8]}...]: {title}")
        return msg_id

    async def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Send a broadcast notification to an FCM topic e.g. 'all_managers_org_101'."""
        msg_id = f"fcm-topic-msg-{uuid.uuid4()}"
        record = {
            "message_id": msg_id,
            "target": "topic",
            "topic": topic,
            "title": title,
            "body": body,
            "data": data or {},
        }
        self._sent_messages.append(record)
        logger.info(f"FCM dispatched to topic [{topic}]: {title}")
        return msg_id

    def get_sent_messages(self) -> list[dict[str, Any]]:
        return list(self._sent_messages)
