"""OpenAI-powered query parser."""

import json
from pathlib import Path
from typing import Optional

import openai

from .parser import Query
from .config import (
    get_openai_api_key,
    get_openai_max_tokens_param,
    get_openai_model,
)

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "parser_prompt.txt"


def load_prompt() -> str:
    """Return parser prompt template."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def parse_llm(text: str, model: Optional[str] = None) -> Query:
    """Parse a query via OpenAI API using the prompt template.

    The ``OPENAI_MODEL`` environment variable is used when ``model`` is not
    provided.
    """
    if model is None:
        model = get_openai_model()
    api_key = get_openai_api_key()

    prompt = load_prompt().format(text=text)
    client = openai.OpenAI(api_key=api_key)
    param = {get_openai_max_tokens_param(): 200}
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        **param,
    )
    content = response.choices[0].message.content.strip()
    data = json.loads(content)
    return Query(
        type=data.get("type", "unknown"),
        from_location=data.get("from"),
        to_location=data.get("to"),
        datetime=data.get("datetime"),
        line=None,
        language=data.get("language"),
    )
