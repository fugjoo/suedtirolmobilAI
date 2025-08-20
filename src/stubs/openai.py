"""Tiny stub of the :mod:`openai` package used for testing.

The real OpenAI client is replaced by this placeholder so that the module can
be imported and monkeypatched in the tests without requiring the external
dependency.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, List, Dict


class ChatCompletions:
    """Minimal chat completions handler."""

    def __init__(self) -> None:
        # ``client.chat.completions.create`` and ``client.chat.create`` both
        # resolve to this instance.
        self.completions = self

    def create(self, *args: Any, **kwargs: Any) -> SimpleNamespace:
        """Return a dummy response echoing the last message content.

        Parameters are accepted for interface compatibility.  The returned
        object mimics the structure accessed in ``choices[0].message.content``.
        """

        messages: List[Dict[str, str]] = kwargs.get("messages", [])
        content = messages[-1]["content"] if messages else ""
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )


class OpenAI:  # pragma: no cover - behaviour replaced in tests
    """Minimal stand-in for :class:`openai.OpenAI`."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the stub client."""
        self.chat = ChatCompletions()
