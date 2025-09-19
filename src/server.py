"""Runtime entrypoint that exposes EFA tools over the Model Context Protocol."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Sequence

from mcp.server import FastMCP
from pydantic import Field

from .efa_client import (
    DepartureBoard,
    EfaApiError,
    EfaClient,
    EfaError,
    StopFinderResponse,
    TripEndpoint,
    TripPlan,
)

logging.basicConfig(level=logging.INFO)

_INSTRUCTIONS = (
    "Tools for searching stops, monitoring departures, and planning journeys "
    "using the Südtirolmobil EFA backend."
)

_client = EfaClient()


@asynccontextmanager
async def _lifespan(_: FastMCP):
    try:
        yield
    finally:
        await _client.aclose()


def _format_messages(messages: Sequence) -> str:
    parts: list[str] = []
    for message in messages:
        text = getattr(message, "text", None)
        code = getattr(message, "code", None)
        module = getattr(message, "module", None)
        if text:
            parts.append(text)
        elif code is not None:
            parts.append(f"{module or 'EFA'}:{code}")
    return "; ".join(parts)


def _handle_errors(exc: EfaError) -> RuntimeError:
    if isinstance(exc, EfaApiError) and getattr(exc, "messages", None):
        details = _format_messages(exc.messages)
        if details:
            return RuntimeError(f"{exc}: {details}")
    return RuntimeError(str(exc))


server = FastMCP(name="suedtirolmobilAI", instructions=_INSTRUCTIONS, lifespan=_lifespan)


@server.tool(
    name="stop.find",
    description="Find stops, addresses or POIs in the Südtirolmobil network.",
)
async def stop_find(
    query: Annotated[str, Field(description="Free text query to identify stops or locations.")],
    limit: Annotated[int | None, Field(default=20, ge=1, le=100, description="Maximum number of candidates to return.")] = 20,
    location_types: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="Optional list of location types (e.g. 'stop', 'poi', 'address') to include.",
        ),
    ] = None,
    best_only: Annotated[
        bool,
        Field(default=False, description="If true only return entries flagged as best matches."),
    ] = False,
) -> StopFinderResponse:
    try:
        return await _client.stop_finder(
            query=query,
            limit=limit,
            location_types=location_types or None,
            best_only=best_only,
        )
    except EfaError as exc:  # pragma: no cover - defensive
        raise _handle_errors(exc) from exc


@server.tool(
    name="departures.board",
    description="Return the next departures for a stop using the EFA departure monitor.",
)
async def departures_board(
    stop_id: Annotated[str, Field(description="Identifier of the stop (stopId/stateless id from stop.find).")],
    when: Annotated[
        datetime | None,
        Field(default=None, description="Desired departure time in ISO format; defaults to now."),
    ] = None,
    limit: Annotated[int, Field(default=10, ge=1, le=40, description="Maximum number of events to return.")] = 10,
    include_realtime: Annotated[
        bool,
        Field(default=True, description="Whether to request realtime delay information."),
    ] = True,
) -> DepartureBoard:
    try:
        return await _client.departures(
            stop_id=stop_id,
            when=when,
            limit=limit,
            include_realtime=include_realtime,
        )
    except EfaError as exc:  # pragma: no cover - defensive
        raise _handle_errors(exc) from exc


@server.tool(
    name="trip.plan",
    description="Plan journeys between two stops within the Südtirolmobil network.",
)
async def trip_plan(
    origin: Annotated[TripEndpoint, Field(description="Origin stop specification.")],
    destination: Annotated[TripEndpoint, Field(description="Destination stop specification.")],
    via: Annotated[TripEndpoint | None, Field(default=None, description="Optional via stop.")] = None,
    departure_time: Annotated[
        datetime | None,
        Field(
            default=None,
            description="Departure (or arrival if arrive_by is true) time in ISO format."
            " Naive values are interpreted in the Europe/Rome timezone.",
        ),
    ] = None,
    arrive_by: Annotated[bool, Field(default=False, description="Treat the provided time as arrival time.")] = False,
    max_trips: Annotated[int, Field(default=5, ge=1, le=10, description="Number of journeys to retrieve.")] = 5,
    include_realtime: Annotated[
        bool,
        Field(default=True, description="Whether to include realtime adjustments when available."),
    ] = True,
) -> TripPlan:
    try:
        return await _client.plan_trip(
            origin=origin,
            destination=destination,
            via=via,
            departure_time=departure_time,
            arrive_by=arrive_by,
            max_trips=max_trips,
            include_realtime=include_realtime,
        )
    except EfaError as exc:  # pragma: no cover - defensive
        raise _handle_errors(exc) from exc


if __name__ == "__main__":
    server.run(transport="stdio")
