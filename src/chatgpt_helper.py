"""Helper functions for interacting with the OpenAI ChatGPT API."""

import json
import logging
import requests

from .config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

API_URL = "https://api.openai.com/v1/chat/completions"


def parse_query_chatgpt(text: str) -> dict:
    """Parse the query text via the OpenAI ChatGPT API."""
    api_key = OPENAI_API_KEY
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Extract origin, destination and time from the text. "
                    "Return JSON with keys 'from_stop', 'to_stop' and 'time'."
                ),
            },
            {"role": "user", "content": text},
        ],
    }

    logger.debug("Sending query to ChatGPT: %s", text)
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()
    try:
        parsed = json.loads(content)
        logger.debug("ChatGPT parsed query: %s", parsed)
        return parsed
    except json.JSONDecodeError:
        logger.warning("Unexpected ChatGPT response: %s", content)
        return {}


def classify_query_chatgpt(text: str) -> dict:
    """Classify the user text and extract request parameters via ChatGPT.

    The function returns a dictionary with at least the key ``endpoint`` which
    is one of ``"search"``, ``"departures"`` or ``"stops"``.  Additional keys
    provide the extracted parameters for the chosen endpoint.
    """
    api_key = OPENAI_API_KEY
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Decide which public transport API endpoint is best suited "
                    "for the user request. Choose between 'search', 'departures' "
                    "and 'stops'. Return JSON with an 'endpoint' key. If the "
                    "endpoint is 'search', also return 'from_stop', 'to_stop' "
                    "and optionally 'time'. If it is 'departures', return "
                    "'stop'. If it is 'stops', return 'query'."
                ),
            },
            {"role": "user", "content": text},
        ],
    }

    logger.debug("Classifying query via ChatGPT: %s", text)
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()
    try:
        parsed = json.loads(content)
        logger.debug("ChatGPT classified query: %s", parsed)
        return parsed
    except json.JSONDecodeError:
        logger.warning("Unexpected ChatGPT response: %s", content)
        return {}


def reformat_summary(text: str) -> str:
    """Return a ChatGPT reformatted version of ``text``.

    The function sends ``text`` to the OpenAI API and returns the resulting
    response as plain text. The API key is read from the ``OPENAI_API_KEY``
    environment variable.
    """
    api_key = OPENAI_API_KEY
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Reformat the following public transport summary to make "
                    "it concise and easy to read. Reply only with the "
                    "reformatted text."
                ),
            },
            {"role": "user", "content": text},
        ],
    }

    logger.debug("Sending summary to ChatGPT: %s", text)
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()
    logger.debug("ChatGPT reformatted summary: %s", content)
    return content


def narrative_trip_summary(result: dict) -> str:
    """Return a friendly ChatGPT summary for a trip search result."""
    from .summaries import format_search_result

    api_key = OPENAI_API_KEY
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    legs_text = format_search_result(result, legs_only=True)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Formuliere aus den folgenden Verbindungsdaten einen freundlichen Text. "
                    "Gib die Verbindungsdaten exakt wieder und sprich die Person in Du-Form an."
                ),
            },
            {"role": "user", "content": legs_text},
        ],
    }

    logger.debug("Sending narrative summary to ChatGPT: %s", legs_text)
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()
    logger.debug("ChatGPT narrative summary: %s", content)
    return content
