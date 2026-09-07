"""
Enterprise Runtime — Middleware chain.

Provides a composable middleware pipeline for processing requests/commands
before they reach business logic. Analogous to ASGI middleware but framework-agnostic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any

# A handler is any async callable that processes a context dict and returns a result
Handler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class Middleware(ABC):
    """
    Abstract middleware component.

    Middleware components form a chain. Each component may:
    - inspect and enrich the context before passing it downstream
    - short-circuit the chain (e.g., on auth failure)
    - post-process the result before returning it upstream
    """

    @abstractmethod
    async def process(
        self,
        context: dict[str, Any],
        next_handler: Handler,
    ) -> dict[str, Any]:
        """
        Process the context, optionally calling next_handler to continue the chain.

        Args:
            context: Mutable dictionary carrying request/command metadata.
            next_handler: The next middleware or final handler in the chain.

        Returns:
            Result dictionary returned by the downstream handler (potentially modified).
        """
        ...


class MiddlewareChain:
    """
    Composable middleware pipeline.

    Usage::

        chain = MiddlewareChain()
        chain.add(AuthenticationMiddleware())
        chain.add(AuthorizationMiddleware())
        chain.add(AuditMiddleware())
        result = await chain.execute(context, final_handler)
    """

    def __init__(self) -> None:
        self._middlewares: list[Middleware] = []

    def add(self, middleware: Middleware) -> MiddlewareChain:
        """Append a middleware to the end of the chain. Returns self for chaining."""
        self._middlewares.append(middleware)
        return self

    async def execute(
        self,
        context: dict[str, Any],
        handler: Handler,
    ) -> dict[str, Any]:
        """Execute all middleware in order, then call the final handler."""

        async def build_chain(index: int) -> Handler:
            if index >= len(self._middlewares):
                return handler

            middleware = self._middlewares[index]
            inner_handler = await build_chain(index + 1)

            async def _next(ctx: dict[str, Any]) -> dict[str, Any]:
                return await middleware.process(ctx, inner_handler)

            return _next

        entry = await build_chain(0)
        return await entry(context)
