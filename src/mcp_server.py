"""Model Context Protocol server exposing transport tools."""

from __future__ import annotations

from typing import Any, Dict, Sequence, List

import json
from pydantic import BaseModel
from mcp import types
from mcp.server import Server

from .services import (
    DeparturesRequest,
    SearchRequest,
    StopsRequest,
    departures_service,
    search_service,
    stops_service,
)
from . import request_logger, parser


class SessionManager:
    """Manage ``parser.Query`` objects for multiple sessions."""

    def __init__(self) -> None:
        self._queries: Dict[str, parser.Query] = {}

    def _execute_query(self, q: parser.Query) -> Any:
        """Return EFA data for ``q`` using the high-level services."""
        if q.from_location and q.to_location:
            text = compose_text(q)
            return search_service(SearchRequest(text=text))
        if q.from_location:
            req = DeparturesRequest(stop=q.from_location, language=q.language or "de")
            return departures_service(req)
        return {}

    def update_query(self, session_id: str, text: str) -> Any:
        """Merge ``text`` into the session query and return fresh results."""
        new_q = parser.parse(text)
        old_q = self._queries.get(session_id, parser.Query("unknown"))
        merged = merge_queries(old_q, new_q)
        self._queries[session_id] = merged
        return self._execute_query(merged)

    def reset_session(self, session_id: str) -> Any:
        """Remove stored state for ``session_id``."""
        self._queries.pop(session_id, None)
        return {}


def merge_queries(old: parser.Query, new: parser.Query) -> parser.Query:
    """Merge two queries, preferring values from ``new``."""
    return parser.Query(
        new.type if new.type != "unknown" else old.type,
        new.from_location or old.from_location,
        new.to_location or old.to_location,
        new.datetime or old.datetime,
        new.language or old.language,
        new.bus if new.bus is not None else old.bus,
        new.zug if new.zug is not None else old.zug,
        new.seilbahn if new.seilbahn is not None else old.seilbahn,
        new.long_distance if new.long_distance is not None else old.long_distance,
        new.datetime_mode or old.datetime_mode,
        new.last_connection or old.last_connection,
    )


SESSION_MANAGER = SessionManager()


def compose_text(q: parser.Query) -> str:
    """Return a canonical text representation of ``q``."""
    words = {
        "de": {"from": "von", "to": "nach", "departures": "Abfahrten", "at": "um"},
        "it": {"from": "da", "to": "a", "departures": "Partenze", "at": "alle"},
        "en": {"from": "from", "to": "to", "departures": "Departures", "at": "at"},
    }.get(q.language or "de")
    parts: List[str] = []
    if q.from_location and q.to_location:
        parts.append(f"{words['from']} {q.from_location} {words['to']} {q.to_location}")
    elif q.from_location:
        parts.append(f"{words['departures']} {q.from_location}")
    if q.datetime:
        try:
            parts.append(f"{words['at']} " + q.datetime.split("T")[1])
        except Exception:
            pass
    return " ".join(parts)


class UpdateQueryRequest(BaseModel):
    """Request body for ``update_query``."""

    session_id: str
    text: str


class ResetSessionRequest(BaseModel):
    """Request body for ``reset_session``."""

    session_id: str

server = Server("suedtirolmobilAI")


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """Expose available transport tools."""
    return [
        types.Tool(
            name="search",
            description="Parse a text query and return EFA results",
            inputSchema=SearchRequest.model_json_schema(),
        ),
        types.Tool(
            name="departures",
            description="Return upcoming departures for a stop",
            inputSchema=DeparturesRequest.model_json_schema(),
        ),
        types.Tool(
            name="stops",
            description="Return stop name suggestions",
            inputSchema=StopsRequest.model_json_schema(),
        ),
        types.Tool(
            name="update_query",
            description="Update session query with new text",
            inputSchema=UpdateQueryRequest.model_json_schema(),
        ),
        types.Tool(
            name="reset_session",
            description="Reset session state",
            inputSchema=ResetSessionRequest.model_json_schema(),
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent]:
    """Dispatch tool calls to the service layer."""
    args = dict(arguments)
    request_logger.log_entry({"tool": name, "arguments": args})
    fmt = args.pop("format", "json")
    try:
        if name == "search":
            result = search_service(SearchRequest(**args), fmt)
        elif name == "departures":
            result = departures_service(DeparturesRequest(**args), fmt)
        elif name == "stops":
            result = stops_service(StopsRequest(**args), fmt)
        elif name == "update_query":
            req = UpdateQueryRequest(**args)
            result = SESSION_MANAGER.update_query(req.session_id, req.text)
        elif name == "reset_session":
            req = ResetSessionRequest(**args)
            result = SESSION_MANAGER.reset_session(req.session_id)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as exc:
        request_logger.log_entry({"tool": name, "error": str(exc)})
        raise

    text = result if isinstance(result, str) else json.dumps(result)
    return [types.TextContent(type="text", text=text)]


if __name__ == "__main__":  # pragma: no cover - manual start
    import asyncio
    from mcp.server import stdio_server

    asyncio.run(stdio_server.run(server))
