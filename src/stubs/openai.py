"""Tiny stub of the :mod:`openai` package used for testing.

The real OpenAI client is replaced by this placeholder so that the module can
be imported and monkeypatched in the tests without requiring the external
dependency.
"""

from __future__ import annotations


class OpenAI:  # pragma: no cover - behaviour replaced in tests
    def __init__(self, *args, **kwargs) -> None:  # noqa: D401 - trivial
        pass
