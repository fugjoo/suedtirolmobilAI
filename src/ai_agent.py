"""Simple conversational AI agent with per-session memory."""

from __future__ import annotations

import os
from typing import Dict, List, Optional

import openai

from .config import get_openai_model, get_openai_max_tokens

# Mapping of session identifiers to lists of message dictionaries
MEMORY: Dict[str, List[Dict[str, str]]] = {}


def respond(
    session_id: str,
    message: str,
    *,
    max_turns: int = 5,
    model: Optional[str] = None,
) -> str:
    """Return assistant reply for ``message`` using conversation memory.

    The user message is appended to the stored message history for
    ``session_id``. Only the most recent ``max_turns`` turns (user +
    assistant messages) are kept. The full history is sent to the OpenAI
    chat completion API and the assistant's reply is stored and returned.

    Args:
        session_id: Conversation identifier.
        message: Latest user message.
        max_turns: Number of turns to retain. Defaults to ``5``.
        model: Optional OpenAI model name. If omitted, the value from
            :func:`get_openai_model` is used.

    Returns:
        The assistant's reply as plain text.
    """

    if model is None:
        model = get_openai_model()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    history = MEMORY.setdefault(session_id, [])
    history.append({"role": "user", "content": message})

    max_messages = max_turns * 2
    if len(history) > max_messages:
        del history[:-max_messages]

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=history,
        max_tokens=get_openai_max_tokens(),
    )
    reply = response.choices[0].message.content

    history.append({"role": "assistant", "content": reply})
    if len(history) > max_messages:
        del history[:-max_messages]

    return reply


def reset(session_id: str) -> None:
    """Clear stored conversation history for ``session_id``."""

    MEMORY.pop(session_id, None)
