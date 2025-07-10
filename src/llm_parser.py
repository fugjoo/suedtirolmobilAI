"""OpenAI-powered query parser."""

import json
import os
from datetime import datetime
import re
from pathlib import Path
from typing import Optional

import openai

from .parser import Query, relative_iso
from .config import get_openai_model

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "parser_prompt.txt"


def load_prompt() -> str:
    """Return parser prompt template."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def _normalize_datetime(dt_value: Optional[str], text: str) -> str:
    """Return ISO timestamp from a datetime field or fallback text."""
    now = datetime.now()
    if dt_value:
        time_match = re.search(r"\d{1,2}:\d{2}", dt_value)
        iso = relative_iso(dt_value, time_match.group(0) if time_match else None)
        if iso:
            return iso
        try:
            dt = datetime.fromisoformat(dt_value)
        except ValueError:
            pass
        else:
            if dt.year != now.year:
                dt = dt.replace(year=now.year)
            return dt.strftime("%Y-%m-%dT%H:%M")
    iso = relative_iso(text)
    if iso:
        return iso
    return now.strftime("%Y-%m-%dT%H:%M")


def parse_llm(text: str, model: Optional[str] = None) -> Query:
    """Parse a query via OpenAI API using the prompt template.

    The ``OPENAI_MODEL`` environment variable is used when ``model`` is not
    provided.
    """
    if model is None:
        model = get_openai_model()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    prompt = load_prompt().format(text=text)
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200,
    )
    content = response.choices[0].message.content.strip()
    data = json.loads(content)
    data["datetime"] = _normalize_datetime(data.get("datetime"), text)
    return Query(
        type=data.get("type", "unknown"),
        from_location=data.get("from"),
        to_location=data.get("to"),
        datetime=data.get("datetime"),
        language=data.get("language"),
        bus=data.get("bus", True),
        zug=data.get("zug", True),
        seilbahn=data.get("seilbahn", True),
        long_distance=data.get("long_distance", False),
        datetime_mode=data.get("datetime_mode", "dep"),
    )
