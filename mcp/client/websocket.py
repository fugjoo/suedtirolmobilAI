"""HTTP-based stand-in for the MCP WebSocket client."""

from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Tuple

import httpx


@asynccontextmanager
async def websocket_client(
    base_url: str,
) -> Tuple[Callable[[], Awaitable[str]], Callable[[Any], Awaitable[None]]]:
    """Yield simple read/write callables using HTTP requests."""
    async with httpx.AsyncClient(base_url=base_url) as client:
        holder = {"response": ""}

        async def write(data: Any) -> None:
            name = data.get("name")
            payload = data.get("payload")
            resp = await client.post(f"/{name}", json=payload)
            resp.raise_for_status()
            holder["response"] = resp.text

        async def read() -> str:
            return holder["response"]

        yield read, write
