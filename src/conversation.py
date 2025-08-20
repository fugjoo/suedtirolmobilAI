"""ChatGPT interaction helpers using the MCP server."""

from typing import Callable, Dict, List, Optional
import os
import openai

from .config import get_openai_model, get_openai_max_tokens


# Keywords that should trigger an MCP call
MCP_KEYWORDS = {"departures", "departure", "trip", "stops", "stop"}


def call_mcp(text: str) -> str:  # pragma: no cover - real network call
    """Return data from the MCP server for ``text``.

    The default implementation is a placeholder that should be replaced by a
    real MCP client.  Tests monkeypatch this function.
    """
    raise RuntimeError("MCP client not configured")


def _needs_mcp(text: str) -> bool:
    """Return ``True`` if ``text`` indicates that MCP data is required."""
    lower = text.lower()
    return any(keyword in lower for keyword in MCP_KEYWORDS)


def respond(
    messages: List[Dict[str, str]],
    *,
    call_mcp_fn: Callable[[str], str] = call_mcp,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """Return a ChatGPT response for ``messages``.

    ``messages`` should be a list of chat messages compatible with the OpenAI
    Chat Completions API.  The last message is assumed to contain the user's
    latest request.  When simple heuristics indicate that MCP data could
    improve the answer, ``call_mcp_fn`` is invoked with that text.  The
    returned information is appended to the conversation as a system message
    before querying ChatGPT.  Any network errors from the MCP call result in a
    user friendly fallback message.
    """
    if not messages:
        return ""

    if model is None:
        model = get_openai_model()
    if max_tokens is None:
        max_tokens = get_openai_max_tokens()

    last_text = messages[-1].get("content", "")
    if _needs_mcp(last_text):
        try:
            data = call_mcp_fn(last_text)
        except Exception:  # pragma: no cover - network
            return "Service temporarily unavailable. Please try again later."
        messages = list(messages) + [
            {"role": "system", "content": f"MCP data:\n{data}"}
        ]

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()
