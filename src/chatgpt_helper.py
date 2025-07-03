import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

API_URL = "https://api.openai.com/v1/chat/completions"


def parse_query_chatgpt(text: str) -> dict:
    """Parse the query text via the OpenAI ChatGPT API."""
    api_key = os.getenv("OPENAI_API_KEY")
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


def reformat_summary(text: str) -> str:
    """Return a ChatGPT reformatted version of ``text``.

    The function sends ``text`` to the OpenAI API and returns the resulting
    response as plain text. The API key is read from the ``OPENAI_API_KEY``
    environment variable.
    """
    api_key = os.getenv("OPENAI_API_KEY")
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

