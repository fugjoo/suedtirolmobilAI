"""Lightweight MCP client shims used by the tests."""

from .session import ClientSession
from .websocket import websocket_client

__all__ = ["ClientSession", "websocket_client"]
