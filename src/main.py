from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from . import nlp_parser, efa_api

app = FastAPI()

class SearchRequest(BaseModel):
    text: str

class DMRequest(BaseModel):
    stop: str
    limit: int = 10


class StopFinderRequest(BaseModel):
    query: str

@app.post("/search")
def search(req: SearchRequest):
    params = nlp_parser.parse_query(req.text)
    if not params:
        raise HTTPException(status_code=400, detail="No parameters extracted")
    return efa_api.search_efa(params)


@app.post("/departures")
def departures(req: DMRequest):
    """Return upcoming departures for the given stop."""
    if not req.stop:
        raise HTTPException(status_code=400, detail="Missing stop name")
    return efa_api.dm_request(req.stop, req.limit)


@app.post("/stops")
def stops(req: StopFinderRequest):
    """Return stop suggestions for the given query."""
    if not req.query:
        raise HTTPException(status_code=400, detail="Missing query")
    return efa_api.stop_finder(req.query)

# Run via ``python -m src.main`` for debugging without auto-reload.
if __name__ == "__main__" and __package__:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

