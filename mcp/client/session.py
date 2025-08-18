"""Minimal client session for HTTP-based MCP interactions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable


@dataclass
class _TextContent:
    """Simplified text content container."""

    text: str


class _Result:
    """Response wrapper mimicking the real MCP result object."""

    def __init__(self, text: str) -> None:
        self.content = [_TextContent(text=text)]


class ClientSession:
    """Very small subset of the real MCP ``ClientSession`` API."""

    def __init__(
        self,
        read: Callable[[], Awaitable[str]],
        write: Callable[[Any], Awaitable[None]],
    ) -> None:
        self._read = read
        self._write = write

    async def initialize(self) -> None:
        """Initialize the session. This is a no-op in the stub."""

    async def call_tool(self, name: str, payload: Any) -> _Result:
        """Send a tool call and return the server response."""
        await self._write({"name": name, "payload": payload})
        text = await self._read()
        return _Result(text)
