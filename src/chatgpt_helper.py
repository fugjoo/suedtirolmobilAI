"""Helper functions for interacting with the OpenAI ChatGPT API."""

import json
import logging
import requests

from .config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

API_URL = "https://api.openai.com/v1/chat/completions"

# System prompts in different languages for narrative summaries
_PROMPTS = {
    "de": (
        "Formuliere aus den folgenden Verbindungsdaten einen h\u00f6flichen "
        "Vorschlag. Beginne mit einem Satz wie 'Du k\u00f6nntest von A nach B "
        "fahren.' Danach liste strukturiert die Verbindungen mit "
        "Abfahrts- und Ankunftszeiten auf. Gib die Daten exakt wieder und "
        "sprich die Person in Du-Form an."
    ),
    "en": (
        "Create a polite suggestion from the trip details. Start with a "
        "sentence such as 'You could travel from A to B.' Then list the "
        "connections with departure and arrival times in a structured way. "
        "Repeat all details exactly and address the person informally."
    ),
    "it": (
        "Formula un suggerimento cortese usando i seguenti dati di viaggio. "
        "Inizia con una frase come 'Potresti andare da A a B.' Quindi elenca "
        "in modo chiaro le connessioni con orari di partenza e arrivo. "
        "Riporta i dati esattamente e rivolgiti alla persona in modo "
        "informale."
    ),
}


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


def classify_query_chatgpt(text: str, history=None) -> dict:
    """Classify the user text and extract request parameters via ChatGPT.

    Parameters
    ----------
    text: str
        The latest user input.
    history: list[str] | None, optional
        Previous user messages to provide conversation context.

    Returns
    -------
    dict
        Parsed request information containing at least the key ``endpoint``.
    """
    api_key = OPENAI_API_KEY
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    messages = [
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
        }
    ]
    if history:
        for msg in history[-5:]:
            messages.append({"role": "user", "content": msg})
    messages.append({"role": "user", "content": text})

    payload = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "messages": messages,
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


def narrative_trip_summary(result: dict, lang: str = "de") -> str:
    """Return a friendly ChatGPT summary for a trip search result.

    Parameters
    ----------
    result: dict
        Parsed trip search response.
    lang: str, optional
        Language code for the summary. Defaults to ``"de"``.
    """
    from .summaries import format_search_result

    api_key = OPENAI_API_KEY
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    legs_text = format_search_result(result, legs_only=True, lang=lang)

    from_stop = (
        result.get("from_stop")
        or (result.get("origin") or {}).get("name")
    )
    to_stop = (
        result.get("to_stop")
        or (result.get("destination") or {}).get("name")
    )
    if from_stop or to_stop:
        if lang == "de":
            intro = f"von {from_stop or ''} nach {to_stop or ''}".strip()
        elif lang == "it":
            intro = f"da {from_stop or ''} a {to_stop or ''}".strip()
        else:
            intro = f"from {from_stop or ''} to {to_stop or ''}".strip()
        legs_text = f"{intro}\n{legs_text}".strip()

    prompt = _PROMPTS.get(lang, _PROMPTS["en"])

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "messages": [
            {"role": "system", "content": prompt},
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


def _load_prompt(name: str) -> str:
    """Return the contents of a prompt template."""
    from pathlib import Path

    path = Path(__file__).resolve().parent.parent / "prompts" / name
    with path.open(encoding="utf-8") as fh:
        return fh.read()


def parse_request_llm(text: str) -> dict:
    """Parse a natural language request using an external prompt."""
    api_key = OPENAI_API_KEY
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    prompt = _load_prompt("extract_search_parameters.txt")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
    }

    logger.debug("LLM parsing text: %s", text)
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()
    try:
        parsed = json.loads(content)
        logger.debug("LLM parsed request: %s", parsed)
        return parsed
    except json.JSONDecodeError:
        logger.warning("Unexpected LLM response: %s", content)
        return {}


def format_trip_response_llm(result: dict, lang: str = "de") -> str:
    """Return an LLM formatted summary of a trip search result."""
    api_key = OPENAI_API_KEY
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    prompt = _load_prompt("format_trip_response.txt").format(language=lang)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(result, ensure_ascii=False)},
        ],
    }

    logger.debug("Requesting LLM trip summary")
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()
    logger.debug("LLM trip summary: %s", content)
    return content
