"""
AI-Powered Intelligent HRMS — Real-time WebSocket Connection & Broadcast Hub.

Features:
- Multi-tenant connection tracking
- Channel-based subscriptions (e.g. tenant-wide events, specific workflow, specific agent)
- Async broadcast with stale connection pruning
- JSON message framing
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketHub:
    """Manages active WebSocket connections with multi-tenant and channel routing."""

    def __init__(self) -> None:
        # channel_name -> set of active WebSockets
        self._channels: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, channel: str = "global") -> None:
        """Accept WebSocket connection and register to channel."""
        await websocket.accept()
        async with self._lock:
            self._channels[channel].add(websocket)
        logger.info(f"WebSocket connected to channel '{channel}'. Total in channel: {len(self._channels[channel])}")

    async def disconnect(self, websocket: WebSocket, channel: str = "global") -> None:
        """Unregister and cleanup disconnected WebSocket."""
        async with self._lock:
            if channel in self._channels:
                self._channels[channel].discard(websocket)
                if not self._channels[channel]:
                    del self._channels[channel]
        logger.info(f"WebSocket disconnected from channel '{channel}'.")

    async def broadcast_to_channel(self, channel: str, message: dict[str, Any]) -> int:
        """Broadcast payload to all clients connected to a channel."""
        payload_str = json.dumps(message)
        dead_connections: list[WebSocket] = []
        sent_count = 0

        async with self._lock:
            sockets = list(self._channels.get(channel, set()))

        for ws in sockets:
            try:
                await ws.send_text(payload_str)
                sent_count += 1
            except Exception:
                dead_connections.append(ws)

        if dead_connections:
            async with self._lock:
                for dead_ws in dead_connections:
                    self._channels[channel].discard(dead_ws)

        return sent_count

    async def broadcast_tenant_event(self, tenant_id: str, event_type: str, data: dict[str, Any]) -> int:
        """Convenience method for broadcasting events to a tenant's global channel."""
        payload = {
            "type": event_type,
            "tenant_id": tenant_id,
            "data": data,
        }
        return await self.broadcast_to_channel(f"tenant:{tenant_id}", payload)


# Global singleton instance
ws_hub = WebSocketHub()
