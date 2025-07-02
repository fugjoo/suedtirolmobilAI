from typing import Dict, Optional
import re
import logging
import spacy

from .logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()

_nlp = None

def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("de_core_news_sm")
        except Exception:
            _nlp = spacy.blank("de")
    return _nlp

def parse_query(text: str) -> Dict[str, Optional[str]]:
    """Extract stops and time from a natural language query."""
    nlp = _get_nlp()
    logger.debug("Parsing text: %s", text)
    doc = nlp(text)
    stops = [token.text for token in doc if token.pos_ == "PROPN"]
    if not stops:
        # fallback if POS tagging is not available
        m_from = re.search(r"von\s+(\w+)", text, re.IGNORECASE)
        m_to = re.search(r"nach\s+(\w+)", text, re.IGNORECASE)
        if m_from:
            stops.append(m_from.group(1))
        if m_to:
            stops.append(m_to.group(1))

    time_match = re.search(r"([0-2]?\d[:.]\d{2})", text)
    time = time_match.group(1).replace('.', ':') if time_match else None

    result: Dict[str, Optional[str]] = {}
    if stops:
        result["from_stop"] = stops[0]
    if len(stops) > 1:
        result["to_stop"] = stops[1]
    if time:
        result["time"] = time
    logger.debug("Parsed parameters: %s", result)
    return result

