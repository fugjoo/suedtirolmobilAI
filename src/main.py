from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from . import nlp_parser, efa_api

app = FastAPI()

class SearchRequest(BaseModel):
    text: str

@app.post("/search")
def search(req: SearchRequest):
    params = nlp_parser.parse_query(req.text)
    if not params:
        raise HTTPException(status_code=400, detail="No parameters extracted")
    return efa_api.search_efa(params)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

