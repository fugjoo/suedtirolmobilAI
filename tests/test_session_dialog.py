import os
import sys
import anyio
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src import mcp_server, parser


def test_update_query_dialog(monkeypatch):
    """Simulate a dialogue via the MCP server."""
    sid = "s1"
    monkeypatch.setattr(mcp_server.request_logger, "log_entry", lambda *a, **k: None)
    monkeypatch.setattr(mcp_server.SESSION_MANAGER, "_execute_query", lambda q: {})

    def fake_parse(text: str) -> parser.Query:
        mapping = {
            "von A nach B um 18:00": parser.Query("trip", "A", "B", "2025-01-01T18:00"),
            "doch von C": parser.Query("unknown", from_location="C"),
            "20 Uhr": parser.Query("unknown", datetime="2025-01-01T20:00"),
            "ohne Bus": parser.Query("unknown", bus=False),
            "letzte Verbindung": parser.Query("unknown", last_connection=True),
        }
        return mapping[text]

    monkeypatch.setattr(mcp_server.parser, "parse", fake_parse)
    anyio.run(lambda: mcp_server.call_tool("reset_session", {"session_id": sid}))

    anyio.run(lambda: mcp_server.call_tool("update_query", {"session_id": sid, "text": "von A nach B um 18:00"}))
    q = mcp_server.SESSION_MANAGER._queries[sid]
    assert q.from_location == "A" and q.to_location == "B" and q.datetime == "2025-01-01T18:00"

    anyio.run(lambda: mcp_server.call_tool("update_query", {"session_id": sid, "text": "doch von C"}))
    q = mcp_server.SESSION_MANAGER._queries[sid]
    assert q.from_location == "C" and q.to_location == "B"

    anyio.run(lambda: mcp_server.call_tool("update_query", {"session_id": sid, "text": "20 Uhr"}))
    q = mcp_server.SESSION_MANAGER._queries[sid]
    assert q.datetime == "2025-01-01T20:00"

    anyio.run(lambda: mcp_server.call_tool("update_query", {"session_id": sid, "text": "ohne Bus"}))
    q = mcp_server.SESSION_MANAGER._queries[sid]
    assert q.bus is False

    anyio.run(lambda: mcp_server.call_tool("update_query", {"session_id": sid, "text": "letzte Verbindung"}))
    q = mcp_server.SESSION_MANAGER._queries[sid]
    assert q.last_connection is True
