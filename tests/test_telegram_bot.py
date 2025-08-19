import os
import sys
import types
from contextlib import asynccontextmanager

import anyio

@asynccontextmanager
async def failing_ws(*args, **kwargs):
    raise ConnectionError("boom")
    yield


def test_call_api_connection_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "mcp.client.websocket", types.SimpleNamespace(websocket_client=failing_ws))
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from src import telegram_bot
    result = anyio.run(lambda: telegram_bot.call_api("/search", "1", "test"))
    assert "service temporarily unavailable" in result.lower()
