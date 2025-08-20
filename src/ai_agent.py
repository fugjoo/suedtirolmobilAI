"""Simple AI agent using OpenAI for responses and MCP for tools."""

import json
import logging
import os
from typing import Dict, Any

import anyio
from mcp.client.session import ClientSession
from mcp.client.websocket import websocket_client
import openai

from .config import get_openai_model, get_openai_max_tokens

API_URL = os.getenv("API_URL", "http://localhost:8000")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAgent:
    """Agent capable of chatting via OpenAI and calling MCP tools."""

    def respond(self, session_id: str, user_input: str) -> str:
        """Return a reply to ``user_input``.

        If the message starts with ``/`` it is treated as an MCP command and
        routed through :meth:`call_mcp`.  Otherwise the text is sent to the
        OpenAI ChatCompletions API and the generated response is returned.
        """
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0]
            text = parts[1] if len(parts) > 1 else ""
            return self.call_mcp(cmd, {"session_id": session_id, "text": text})

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=get_openai_model(),
            messages=[{"role": "user", "content": user_input}],
            max_tokens=get_openai_max_tokens(),
        )
        return response.choices[0].message.content.strip()

    def call_mcp(self, command: str, payload: Dict[str, Any]) -> str:
        """Call an MCP tool via WebSocket.

        A user-friendly message is returned if the API server is unreachable.
        """

        async def _call() -> str:
            async with websocket_client(API_URL) as (read, write):
                session = ClientSession(read, write)
                await session.initialize()
                result = await session.call_tool(command.lstrip("/"), payload)
            texts = [c.text for c in result.content if hasattr(c, "text")]
            combined = "\n".join(texts)
            try:
                data = json.loads(combined)
            except ValueError:
                data = combined
            if isinstance(data, dict) and "data" in data:
                content = data["data"]
                return content if isinstance(content, str) else json.dumps(
                    content, indent=2, ensure_ascii=False
                )
            return data if isinstance(data, str) else json.dumps(
                data, indent=2, ensure_ascii=False
            )

        try:
            return anyio.run(_call)
        except Exception as exc:  # pragma: no cover - network
            logger.error("Request failed: %s", exc)
            return "Service temporarily unavailable. Please try again later."


agent = AIAgent()
