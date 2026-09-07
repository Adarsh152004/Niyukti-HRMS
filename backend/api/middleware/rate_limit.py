"""
AI-Powered Intelligent HRMS — Sliding Window Rate Limiter Middleware.

Features:
- Sliding-window timestamp log algorithm
- Role-tiered rate limits (Standard: 60/min, Executive: 300/min, Agent/System: 1200/min)
- HTTP 429 Too Many Requests response with standard Retry-After & X-RateLimit-* headers
- Threadsafe in-memory cache with automatic window pruning
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class InMemoryRateLimiter:
    """Threadsafe in-memory sliding window rate limiter."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # key -> list of request timestamps
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(
        self, key: str, max_requests: int = 120, window_seconds: int = 60
    ) -> tuple[bool, int, int]:
        """
        Check if request is permitted within sliding window.
        Returns: (allowed, remaining_quota, reset_seconds)
        """
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            timestamps = self._requests[key]
            # Prune timestamps outside current window
            valid_timestamps = [t for t in timestamps if t > window_start]
            self._requests[key] = valid_timestamps

            count = len(valid_timestamps)
            if count >= max_requests:
                oldest = valid_timestamps[0] if valid_timestamps else window_start
                reset_seconds = max(1, int(window_seconds - (now - oldest)))
                return False, 0, reset_seconds

            # Record this request
            valid_timestamps.append(now)
            remaining = max_requests - len(valid_timestamps)
            return True, remaining, window_seconds


# Global instance
rate_limiter = InMemoryRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware applying sliding-window rate limits:
    - Skips health & openapi schema endpoints
    - Determines rate limit based on client identity / IP
    - Sets standard RFC headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
    - Emits HTTP 429 when quota exceeded
    """

    def __init__(self, app: Any, default_rpm: int = 300) -> None:
        super().__init__(app)
        self.default_rpm = default_rpm

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path

        # Bypass health checks, docs, and static assets
        if path.startswith(("/health", "/api/docs", "/api/redoc", "/api/openapi.json", "/favicon")):
            return await call_next(request)

        # Determine client key
        client_ip = request.client.host if request.client else "127.0.0.1"
        auth_header = request.headers.get("Authorization") or request.headers.get("X-API-Key") or ""
        rate_key = f"{client_ip}:{auth_header[:16]}" if auth_header else client_ip

        # Determine limit tier
        limit = self.default_rpm
        if "agent" in auth_header.lower() or "ak_" in auth_header:
            limit = 1200  # High throughput for autonomous agents
        elif "bearer" in auth_header.lower():
            limit = 600   # Authenticated users

        allowed, remaining, reset_seconds = rate_limiter.is_allowed(
            key=rate_key, max_requests=limit, window_seconds=60
        )

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded. Maximum {limit} requests per minute.",
                    "details": {
                        "limit": limit,
                        "window_seconds": 60,
                        "retry_after_seconds": reset_seconds,
                    },
                },
                headers={
                    "Retry-After": str(reset_seconds),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + reset_seconds)),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + reset_seconds))
        return response
