"""Minimal server implementation to satisfy tests."""

from __future__ import annotations

from typing import Callable
import asyncio


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


class _StdioServer:
    """Very small stand-in for ``mcp.server.stdio_server``.

    The real library provides an asynchronous server that communicates over
    standard input and output.  For the purposes of these exercises we only
    need an object with a ``run`` coroutine so that ``src.mcp_server`` can be
    executed without raising an import error.  The implementation below simply
    awaits on an empty sleep to yield control back to the event loop and then
    returns immediately.
    """

    async def run(self, _server: Server) -> None:
        await asyncio.sleep(0)


# ``src.mcp_server`` expects ``stdio_server`` to be an object with a ``run``
# coroutine.  Expose an instance here to mirror the real API.
stdio_server = _StdioServer()
