import json
import os
import sys

import anyio
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src import services, mcp_server
from src.services import StopsRequest


def test_list_tools_contains_stops():
    tools = anyio.run(mcp_server.list_tools)
    names = [t.name for t in tools]
    assert "stops" in names


def test_call_tool_delegates(monkeypatch):
    def fake_search(req: services.SearchRequest, fmt: str = "json"):
        assert req.text == "hello"
        return {"ok": True}

    monkeypatch.setattr(mcp_server, "search_service", fake_search)
    monkeypatch.setattr(services.request_logger, "log_entry", lambda *a, **k: None)

    result = anyio.run(lambda: mcp_server.call_tool("search", {"text": "hello"}))
    assert json.loads(result[0].text) == {"ok": True}


def test_stops_service(monkeypatch):
    def fake_stop_finder(query: str, language: str = "de"):
        return {"stopFinder": {"points": [{"name": "Bozen"}]}}

    monkeypatch.setattr(services.efa_api, "stop_finder", fake_stop_finder)
    monkeypatch.setattr(services.request_logger, "log_entry", lambda *a, **k: None)

    body = StopsRequest(query="Bo")
    data = services.stops_service(body)
    assert data["data"]["stopFinder"]["points"][0]["name"] == "Bozen"
