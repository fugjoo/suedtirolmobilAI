"""Format EFA responses using OpenAI."""

import json
import os
from pathlib import Path
from typing import Any, Dict

import openai

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "formatter_prompt.txt"


def load_prompt() -> str:
    """Return formatter prompt template."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def format_trip(data: Dict[str, Any], language: str = "de", model: str = "gpt-3.5-turbo") -> str:
    """Return ChatGPT-formatted trip description."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    prompt = load_prompt().format(data=json.dumps(data, ensure_ascii=False), language=language)
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()
