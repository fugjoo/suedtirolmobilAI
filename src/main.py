"""FastAPI application exposing endpoints for trip search and departures."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from . import nlp_parser, efa_api, chatgpt_helper
from .summaries import (
    format_search_result,
    format_departures_result,
    format_stops_result,
)
from .logging_utils import setup_logging

logger = logging.getLogger(__name__)

app = FastAPI()
app.mount(
    "/.well-known",
    StaticFiles(directory=Path(__file__).resolve().parent.parent / ".well-known"),
    name="well-known",
)

class SearchRequest(BaseModel):
    text: str

class DMRequest(BaseModel):
    stop: str
    limit: int = 10


class StopFinderRequest(BaseModel):
    query: str


class ParseRequest(BaseModel):
    """Input model for the /parse endpoint."""

    text: str


class TripRequest(BaseModel):
    """Input model for the /trip endpoint."""

    from_stop: str
    to_stop: str
    time: Optional[str] = None
    lang: Optional[str] = None

@app.post("/search")
def search(req: SearchRequest, format: Optional[str] = None, chatgpt: bool = False):
    """Handle trip searches based on natural language input.

    Expects a :class:`SearchRequest` containing the user text. Setting
    ``format="json"`` returns the raw JSON result. With ``chatgpt=True`` a
    narrative text summary is produced. ``format="text"`` yields a plain text
    summary of all legs, while the default response lists just the individual
    legs.
    """
    logger.info("/search text='%s'", req.text)
    if chatgpt:
        params = chatgpt_helper.parse_query_chatgpt(req.text)
    else:
        params = nlp_parser.parse_query(req.text)
    if not params:
        raise HTTPException(status_code=400, detail="No parameters extracted")
    result = efa_api.search_efa(params)
    logger.debug("/search result: %s", result)
    if format == "json":
        return result
    lang = params.get("lang") or nlp_parser.detect_language(req.text)
    if chatgpt:
        text = chatgpt_helper.narrative_trip_summary(result, lang=lang)
        return PlainTextResponse(text)
    if format == "text":
        text = format_search_result(result, legs_only=False, lang=lang)
        return PlainTextResponse(text)
    # default plain-text response lists the individual legs
    text = format_search_result(result, legs_only=True, lang=lang)
    return PlainTextResponse(text)


@app.post("/departures")
def departures(req: DMRequest, format: str = "json", chatgpt: bool = False):
    """Return upcoming departures for the given stop."""
    logger.info("/departures stop='%s' limit=%s", req.stop, req.limit)
    if not req.stop:
        raise HTTPException(status_code=400, detail="Missing stop name")
    lang = nlp_parser.detect_language(req.stop)
    result = efa_api.dm_request(req.stop, req.limit, lang)
    logger.debug("/departures result: %s", result)
    if format == "text":
        text = format_departures_result(result, lang=lang)
        if chatgpt:
            text = chatgpt_helper.reformat_summary(text)
        return PlainTextResponse(text)
    return result


@app.post("/stops")
def stops(req: StopFinderRequest, format: str = "json", chatgpt: bool = False):
    """Return stop suggestions for the given query."""
    logger.info("/stops query='%s'", req.query)
    if not req.query:
        raise HTTPException(status_code=400, detail="Missing query")
    lang = nlp_parser.detect_language(req.query)
    result = efa_api.stopfinder_request(req.query, lang)
    logger.debug("/stops result: %s", result)
    if format == "text":
        text = format_stops_result(result, lang=lang)
        if chatgpt:
            text = chatgpt_helper.reformat_summary(text)
        return PlainTextResponse(text)
    return result


@app.post("/parse")
def parse(req: ParseRequest):
    """Parse a user request via the language model."""

    logger.info("/parse text='%s'", req.text)
    info = chatgpt_helper.parse_request_llm(req.text)
    if not info:
        raise HTTPException(status_code=400, detail="Parse failed")
    return info


@app.post("/trip")
def trip(req: TripRequest, format: Optional[str] = None, chatgpt: bool = False):
    """Return trip results for explicit parameters."""

    params: Dict[str, Any] = {
        "from_stop": req.from_stop,
        "to_stop": req.to_stop,
    }
    if req.time:
        params["time"] = req.time
    if req.lang:
        params["lang"] = req.lang
    logger.info("/trip params: %s", params)
    result = efa_api.search_efa(params)
    if format == "json":
        return result
    lang = req.lang or nlp_parser.detect_language(req.from_stop)
    if chatgpt:
        text = chatgpt_helper.format_trip_response_llm(result, lang=lang)
        return PlainTextResponse(text)
    if format == "text":
        text = format_search_result(result, legs_only=False, lang=lang)
        return PlainTextResponse(text)
    text = format_search_result(result, legs_only=True, lang=lang)
    return PlainTextResponse(text)

# Run via ``python -m src.main`` for debugging without auto-reload.
if __name__ == "__main__" and __package__:
    setup_logging()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

