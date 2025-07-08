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
    data: Dict[str, Any] = efa_api.trip_request(q.from_location, q.to_location, q.datetime)
    try:
        text = llm_formatter.format_trip(data, language=q.language or "de")
        return text if format == "text" else {"data": text}
    except Exception as exc:  # pragma: no cover - no tests
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/departures")
def departures(body: DeparturesRequest, format: str = Query("json")) -> Any:
    """Return upcoming departures for a stop."""
    data = efa_api.departure_monitor(body.stop, body.limit)
    return data if format == "text" else {"data": data}


@app.post("/stops")
def stops(body: StopsRequest, format: str = Query("json")) -> Any:
    """Return stop name suggestions."""
    data = efa_api.stop_finder(body.query)
    return data if format == "text" else {"data": data}

