"""Configuration helpers for suedtirolmobilAI."""

import os


def get_openai_model() -> str:
    """Return the OpenAI model name.

    The value is taken from the ``OPENAI_MODEL`` environment variable and
    defaults to ``gpt-3.5-turbo``.
    """
    return os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


def get_openai_api_key() -> str:
    """Return the OpenAI API key.

    Raises ``RuntimeError`` if the variable is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return api_key


def get_efa_base_url() -> str:
    """Return the Mentz EFA API base URL."""
    return os.getenv("EFA_BASE_URL", "https://efa.sta.bz.it/apb")


def get_api_url() -> str:
    """Return the API base URL used by the Telegram bot."""
    return os.getenv("API_URL", "http://localhost:8000")


def get_telegram_token(*, required: bool = False) -> str:
    """Return the Telegram bot token.

    When ``required`` is ``True`` a ``RuntimeError`` is raised if the variable
    is not set.
    """
    token = os.getenv("TELEGRAM_TOKEN")
    if required and not token:
        raise RuntimeError("TELEGRAM_TOKEN not set")
    return token or ""


def get_server_url() -> str:
    """Return the public server URL."""
    return os.getenv("SERVER_URL", "https://api.example.com")
