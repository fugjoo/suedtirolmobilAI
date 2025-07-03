from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional
import logging

from . import nlp_parser, efa_api, chatgpt_helper
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
def search(req: SearchRequest, format: Optional[str] = None, chatgpt: bool = False):
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
    if chatgpt:
        text = chatgpt_helper.narrative_trip_summary(result)
        return PlainTextResponse(text)
    if format == "text":
        text = format_search_result(result, legs_only=False)
        return PlainTextResponse(text)
    # default plain-text response lists the individual legs
    text = format_search_result(result, legs_only=True)
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
        text = format_departures_result(result)
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
        text = format_stops_result(result)
        if chatgpt:
            text = chatgpt_helper.reformat_summary(text)
        return PlainTextResponse(text)
    return result

# Run via ``python -m src.main`` for debugging without auto-reload.
if __name__ == "__main__" and __package__:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

