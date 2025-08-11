from typing import Any

from fastapi import FastAPI, Query

from .services import (
    DeparturesRequest,
    SearchRequest,
    StopsRequest,
    departures_service,
    search_service,
    stops_service,
)

app = FastAPI()


@app.post("/search")
def search(body: SearchRequest, format: str = Query("json")) -> Any:
    """Parse a text query and return EFA results."""
    return search_service(body, format)


@app.post("/departures")
def departures(body: DeparturesRequest, format: str = Query("json")) -> Any:
    """Return upcoming departures for a stop."""
    return departures_service(body, format)


@app.post("/stops")
def stops(body: StopsRequest, format: str = Query("json")) -> Any:
    """Return stop name suggestions."""
    return stops_service(body, format)
