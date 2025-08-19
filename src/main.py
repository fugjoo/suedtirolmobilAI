"""FastAPI application exposing transport tools."""

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from .mcp_server import server

app = FastAPI()


@app.post("/{tool_name}", response_class=PlainTextResponse)
async def call_tool(tool_name: str, payload: Dict[str, Any]) -> str:
    """Invoke an MCP tool and return its text output."""
    if server._call_tool_fn is None:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="server not initialized")
    try:
        result = await server._call_tool_fn(tool_name, payload)
    except Exception as exc:  # pragma: no cover - runtime
        raise HTTPException(status_code=500, detail=str(exc))
    texts: List[str] = [getattr(item, "text", "") for item in result]
    return "\n".join(texts)
