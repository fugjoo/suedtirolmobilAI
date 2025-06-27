"""Natural language parsing using OpenAI GPT."""

from __future__ import annotations

import logging
from typing import Dict

import json
import openai

from . import config

logger = logging.getLogger(__name__)
openai.api_key = config.OPENAI_API_KEY


SYSTEM_PROMPT = (
    "You are a helpful assistant that extracts travel information from user requests. "
    "Return a JSON object with 'start', 'ziel', 'datum', and 'uhrzeit' fields."
)


def parse_user_input(text: str) -> Dict[str, str]:
    """Use OpenAI to parse user input into query parameters."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]
    logger.debug("Sending prompt to OpenAI: %s", messages)
    response = openai.ChatCompletion.create(
        model=config.OPENAI_MODEL,
        messages=messages,
        temperature=0,
    )
    content = response.choices[0].message["content"]
    logger.debug("OpenAI response: %s", content)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.error("Could not decode JSON from OpenAI response")
        return {}
