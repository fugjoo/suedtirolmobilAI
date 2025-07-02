from typing import Dict, Optional
import re
import logging
import spacy
from langdetect import detect, DetectorFactory

from .logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()

DetectorFactory.seed = 0

_nlp_cache: Dict[str, spacy.Language] = {}

LANG_MODELS = {
    "de": "de_core_news_sm",
    "en": "en_core_web_sm",
    "it": "it_core_news_sm",
}

LANG_REGEX = {
    "de": {
        "from": re.compile(r"von\s+(\w+)", re.IGNORECASE),
        "to": re.compile(r"nach\s+(\w+)", re.IGNORECASE),
    },
    "en": {
        "from": re.compile(r"from\s+(\w+)", re.IGNORECASE),
        "to": re.compile(r"to\s+(\w+)", re.IGNORECASE),
    },
    "it": {
        "from": re.compile(r"da\s+(\w+)", re.IGNORECASE),
        "to": re.compile(r"\ba\s+(\w+)", re.IGNORECASE),
    },
}

_RE_TIME = re.compile(r"([0-2]?\d[:.]\d{2})")
_RE_TIME_TOKEN = re.compile(r"[0-2]?\d[:.]\d{2}")

def _detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"

def _get_nlp(lang: str) -> spacy.Language:
    if lang in _nlp_cache:
        return _nlp_cache[lang]
    model = LANG_MODELS.get(lang)
    if model:
        try:
            nlp = spacy.load(model)
        except OSError:
            nlp = spacy.blank(lang)
    else:
        nlp = spacy.blank(lang)
    _nlp_cache[lang] = nlp
    return nlp

def parse_query(text: str) -> Dict[str, Optional[str]]:
    """Extract stops and time from a natural language query."""
    lang = _detect_language(text)
    nlp = _get_nlp(lang)
    regex = LANG_REGEX.get(lang, LANG_REGEX.get("en"))

    logger.debug("Parsing text (%s): %s", lang, text)
    doc = nlp(text)
    stops = [t.text for t in doc if t.pos_ == "PROPN"]

    # Filter out tokens that look like a time expression
    stops = [s for s in stops if not _RE_TIME_TOKEN.fullmatch(s)]

    m_from = regex["from"].search(text)
    m_to = regex["to"].search(text)

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

    time_match = _RE_TIME.search(text)
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

