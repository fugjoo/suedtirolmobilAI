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
    TripRequest,
    DepartureMonitorRequest,
    StopFinderRequest,
    departures_service,
    search_service,
    stops_service,
    trip_service,
    departure_monitor_service,
    stop_finder_service,
)
from . import request_logger

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
            name="trip_request",
            description="Direct trip request via EFA",
            inputSchema=TripRequest.model_json_schema(),
        ),
        types.Tool(
            name="departure_monitor",
            description="Direct departure monitor request",
            inputSchema=DepartureMonitorRequest.model_json_schema(),
        ),
        types.Tool(
            name="stop_finder",
            description="Direct stop finder request",
            inputSchema=StopFinderRequest.model_json_schema(),
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
        elif name == "trip_request":
            result = trip_service(TripRequest(**args))
        elif name == "departure_monitor":
            result = departure_monitor_service(DepartureMonitorRequest(**args))
        elif name == "stop_finder":
            result = stop_finder_service(StopFinderRequest(**args))
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
