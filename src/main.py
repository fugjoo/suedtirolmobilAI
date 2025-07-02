from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import logging

from . import nlp_parser, efa_api
from .summaries import (
    format_search_result,
    format_departures_result,
    format_stops_result,
)
from .logging_utils import setup_logging

# Configure logging; debug mode is controlled solely via CLI arguments
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

class SearchRequest(BaseModel):
    text: str

class DMRequest(BaseModel):
    stop: str
    limit: int = 10


class StopFinderRequest(BaseModel):
    query: str

@app.post("/search")
def search(req: SearchRequest, format: str = "json"):
    logger.info("/search text='%s'", req.text)
    params = nlp_parser.parse_query(req.text)
    if not params:
        raise HTTPException(status_code=400, detail="No parameters extracted")
    result = efa_api.search_efa(params)
    logger.debug("/search result: %s", result)
    if format == "text":
        # Pass legs_only explicitly for clarity and to aid testing
        return PlainTextResponse(format_search_result(result, legs_only=False))
    if format == "legs":
        return PlainTextResponse(format_search_result(result, legs_only=True))
    return result


@app.post("/departures")
def departures(req: DMRequest, format: str = "json"):
    """Return upcoming departures for the given stop."""
    logger.info("/departures stop='%s' limit=%s", req.stop, req.limit)
    if not req.stop:
        raise HTTPException(status_code=400, detail="Missing stop name")
    result = efa_api.dm_request(req.stop, req.limit)
    logger.debug("/departures result: %s", result)
    if format == "text":
        return PlainTextResponse(format_departures_result(result))
    return result


@app.post("/stops")
def stops(req: StopFinderRequest, format: str = "json"):
    """Return stop suggestions for the given query."""
    logger.info("/stops query='%s'", req.query)
    if not req.query:
        raise HTTPException(status_code=400, detail="Missing query")
    result = efa_api.stopfinder_request(req.query)
    logger.debug("/stops result: %s", result)
    if format == "text":
        return PlainTextResponse(format_stops_result(result))
    return result

# Run via ``python -m src.main`` for debugging without auto-reload.
if __name__ == "__main__" and __package__:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

