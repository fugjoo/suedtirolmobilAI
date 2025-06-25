from fastapi import FastAPI
from pydantic import BaseModel

from src.main import handle_request

app = FastAPI()

class Query(BaseModel):
    text: str

@app.post("/query")
def query_endpoint(query: Query):
    """Return Fahrplan results for the given text."""
    return handle_request(query.text)

@app.get("/")
def read_root():
    return {"status": "ok"}
