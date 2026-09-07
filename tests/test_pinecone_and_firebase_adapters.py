"""
Tests for Pinecone Vector Store and Firebase Notification Adapters.
"""

from __future__ import annotations

import pytest

from backend.integrations.providers.firebase_notifications import FirebaseNotificationAdapter
from backend.integrations.providers.pinecone_vector_store import PineconeVectorStoreAdapter


@pytest.mark.asyncio
async def test_pinecone_vector_store_upsert_and_similarity_query():
    adapter = PineconeVectorStoreAdapter(api_key="mock-pinecone-key")
    org_id = "org-pinecone-test"

    vectors = [
        {"id": "doc-policy-remote", "values": [0.9, 0.1, 0.0, 0.0], "metadata": {"category": "POLICY", "topic": "remote_work"}},
        {"id": "doc-policy-leave", "values": [0.1, 0.9, 0.0, 0.0], "metadata": {"category": "POLICY", "topic": "annual_leave"}},
        {"id": "doc-payroll-rules", "values": [0.0, 0.1, 0.9, 0.0], "metadata": {"category": "PAYROLL", "topic": "allowance"}},
    ]

    count = await adapter.upsert_vectors(org_id, vectors)
    assert count == 3

    # Query matching remote work vector
    query_vec = [0.85, 0.15, 0.0, 0.0]
    results = await adapter.query_vectors(org_id, query_vec, top_k=2)

    assert len(results) >= 1
    assert results[0]["id"] == "doc-policy-remote"
    assert results[0]["score"] > 0.9


@pytest.mark.asyncio
async def test_firebase_push_notification_dispatch():
    adapter = FirebaseNotificationAdapter(project_id="test-hrms-firebase")

    # 1. Device notification
    dev_msg_id = await adapter.send_to_device(
        device_token="fcm_device_token_xyz_123",
        title="Leave Request Approved",
        body="Your annual leave from Sep 1 to Sep 5 was approved by HR.",
        data={"leave_id": "lv-555"},
    )
    assert dev_msg_id.startswith("fcm-msg-")

    # 2. Topic broadcast
    topic_msg_id = await adapter.send_to_topic(
        topic="org_101_all_employees",
        title="Town Hall Reminder",
        body="Quarterly All-Hands starts in 30 minutes.",
    )
    assert topic_msg_id.startswith("fcm-topic-msg-")

    history = adapter.get_sent_messages()
    assert len(history) == 2
