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


def get_mcp_port(default: int = 8080) -> int:
    """Return the port for the MCP server.

    The value is taken from the ``MCP_SERVER_PORT`` environment variable and
    falls back to ``default`` when not set or invalid.
    """
    value = os.getenv("MCP_SERVER_PORT")
    if value and value.isdigit():
        return int(value)
    return default


def get_mcp_auth_token() -> str:
    """Return the authentication token for the MCP server.

    The value is taken from the ``MCP_AUTH_TOKEN`` environment variable and
    defaults to an empty string.
    """
    return os.getenv("MCP_AUTH_TOKEN", "")
