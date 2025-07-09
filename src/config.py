"""Configuration helpers for suedtirolmobilAI."""

import os


def get_openai_model() -> str:
    """Return the OpenAI model name.

    The value is taken from the ``OPENAI_MODEL`` environment variable and
    defaults to ``gpt-3.5-turbo``.
    """
    return os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
