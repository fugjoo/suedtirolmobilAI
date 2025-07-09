"""FastAPI application for transport queries."""

from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from . import efa_api, parser, llm_parser, llm_formatter

app = FastAPI()


class SearchRequest(BaseModel):
    """Request body for /search."""

    text: str


class DeparturesRequest(BaseModel):
    """Request body for /departures."""

    stop: str
    limit: int = 10


class StopsRequest(BaseModel):
    """Request body for /stops."""

    query: str


@app.post("/search")
def search(body: SearchRequest, format: str = Query("json")) -> Any:
    """Parse a text query for a trip and return EFA results."""
    q = parser.parse(body.text)
    if q.type != "trip" or not q.from_location or not q.to_location:
        try:
            q = llm_parser.parse_llm(body.text)
        except Exception as exc:  # pragma: no cover - no tests
            raise HTTPException(status_code=400, detail=str(exc))

    from_data = efa_api.stop_finder(q.from_location)
    points = from_data.get("stopFinder", {}).get("points", [])
    if not points:
        raise HTTPException(status_code=404, detail="origin not found")
    from_point = points[0]
    q.from_location = from_point.get("name", q.from_location)
    from_stateless = from_point.get("stateless")

    to_data = efa_api.stop_finder(q.to_location)
    points = to_data.get("stopFinder", {}).get("points", [])
    if not points:
        raise HTTPException(status_code=404, detail="destination not found")
    to_point = points[0]
    q.to_location = to_point.get("name", q.to_location)
    to_stateless = to_point.get("stateless")

    data: Dict[str, Any] = efa_api.trip_request(
        q.from_location,
        q.to_location,
        q.datetime,
        origin_stateless=from_stateless,
        destination_stateless=to_stateless,
    )
    short_data = llm_formatter.extract_trip_info(data)
    try:
        text = llm_formatter.format_trip(data, language=q.language or "de")
        if format == "text":
            return text
        return {
            "input": body.text,
            "from": from_point,
            "to": to_point,
            "llmData": short_data,
            "data": text,
        }
    except Exception as exc:  # pragma: no cover - no tests
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/departures")
def departures(body: DeparturesRequest, format: str = Query("json")) -> Any:
    """Return upcoming departures for a stop."""
    sf_data = efa_api.stop_finder(body.stop)
    points = sf_data.get("stopFinder", {}).get("points", [])
    if not points:
        raise HTTPException(status_code=404, detail="stop not found")
    point = points[0]
    verified = point.get("name", body.stop)
    stateless = point.get("stateless")
    data = efa_api.departure_monitor(verified, body.limit, stateless=stateless)
    short_data = llm_formatter.extract_departure_info(data)
    try:
        text = llm_formatter.format_departures(data, language="de")
        if format == "text":
            return text
        return {
            "input": body.stop,
            "stop": point,
            "llmData": short_data,
            "data": text,
        }
    except Exception as exc:  # pragma: no cover - no tests
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/stops")
def stops(body: StopsRequest, format: str = Query("json")) -> Any:
    """Return stop name suggestions."""
    data = efa_api.stop_finder(body.query)
    return data if format == "text" else {"data": data}

