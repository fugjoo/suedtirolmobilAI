"""Configuration helpers for suedtirolmobilAI."""

import os


def get_openai_model() -> str:
    """Return the OpenAI model name.

    The value is taken from the ``OPENAI_MODEL`` environment variable and
    defaults to ``gpt-3.5-turbo``.
    """
    return os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


def get_openai_max_tokens(default: int = 100) -> int:
    """Return the maximum number of tokens for OpenAI replies.

    The value is taken from the ``OPENAI_MAX_TOKENS`` environment variable
    and falls back to ``default`` when not set or invalid.
    """
    value = os.getenv("OPENAI_MAX_TOKENS")
    if value and value.isdigit():
        return int(value)
    return default
