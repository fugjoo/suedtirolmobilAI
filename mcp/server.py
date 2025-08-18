"""Minimal server implementation to satisfy tests."""

from __future__ import annotations

from typing import Callable


class Server:
    """Very small imitation of :class:`mcp.server.Server`."""

    def __init__(self, _name: str) -> None:
        self._list_tools_fn: Callable | None = None
        self._call_tool_fn: Callable | None = None

    def list_tools(self):
        def decorator(func: Callable) -> Callable:
            self._list_tools_fn = func
            return func

        return decorator

    def call_tool(self):
        def decorator(func: Callable) -> Callable:
            self._call_tool_fn = func
            return func

        return decorator
