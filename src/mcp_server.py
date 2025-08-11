"""Model Context Protocol server exposing transport tools."""

from __future__ import annotations

from typing import Any, Dict, Sequence, List

import json
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
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent]:
    """Dispatch tool calls to the service layer."""
    args = dict(arguments)
    fmt = args.pop("format", "json")
    if name == "search":
        result = search_service(SearchRequest(**args), fmt)
    elif name == "departures":
        result = departures_service(DeparturesRequest(**args), fmt)
    elif name == "stops":
        result = stops_service(StopsRequest(**args), fmt)
    else:
        raise ValueError(f"Unknown tool: {name}")

    text = result if isinstance(result, str) else json.dumps(result)
    return [types.TextContent(type="text", text=text)]


if __name__ == "__main__":  # pragma: no cover - manual start
    import asyncio
    from mcp.server import stdio_server

    asyncio.run(stdio_server.run(server))
