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
    stops = [t.text for t in doc if t.pos_ == "PROPN"]

    # Filter out tokens that look like a time expression
    stops = [s for s in stops if not re.fullmatch(r"[0-2]?\d[:.]\d{2}", s)]

    m_from = re.search(r"von\s+(\w+)", text, re.IGNORECASE)
    m_to = re.search(r"nach\s+(\w+)", text, re.IGNORECASE)

    if m_from:
        from_stop = m_from.group(1)
    elif stops:
        from_stop = stops.pop(0)
    else:
        from_stop = None

    if m_to:
        to_stop = m_to.group(1)
    elif stops:
        to_stop = stops.pop(0)
    else:
        to_stop = None

    time_match = re.search(r"([0-2]?\d[:.]\d{2})", text)
    time = time_match.group(1).replace('.', ':') if time_match else None

    result: Dict[str, Optional[str]] = {}
    if from_stop:
        result["from_stop"] = from_stop
    if to_stop:
        result["to_stop"] = to_stop
    if time:
        result["time"] = time
    logger.debug("Parsed parameters: %s", result)
    return result

