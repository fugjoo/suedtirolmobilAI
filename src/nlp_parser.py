"""Simple NLP parser and classifier for public transport queries."""

from typing import Dict, Optional
import re
import logging
import spacy
from langdetect import detect, DetectorFactory

logger = logging.getLogger(__name__)


DetectorFactory.seed = 0

_nlp_cache: Dict[str, spacy.Language] = {}

LANG_MODELS = {
    "de": "de_core_news_sm",
    "en": "en_core_web_sm",
    "it": "it_core_news_sm",
}

LANG_REGEX = {
    "de": {
        "from": re.compile(r"von\s+(.+?)(?=\s+nach\b|$)", re.IGNORECASE),
        "to": re.compile(r"nach\s+(.+?)(?=\s+um\b|\?|\.|$)", re.IGNORECASE),
    },
    "en": {
        "from": re.compile(r"from\s+(.+?)(?=\s+to\b|$)", re.IGNORECASE),
        "to": re.compile(r"to\s+(.+?)(?=\s+at\b|\?|\.|$)", re.IGNORECASE),
    },
    "it": {
        "from": re.compile(r"da\s+(.+?)(?=\s+a\b|$)", re.IGNORECASE),
        "to": re.compile(r"\ba\s+(.+?)(?=\s+alle?\b|\?|\.|$)", re.IGNORECASE),
    },
}

_RE_TIME = re.compile(r"([0-2]?\d[:.]\d{2})")
_RE_TIME_ALT = re.compile(r"(?:um\s*)?(\d{1,2})\s*uhr(?:\s*(\d{1,2}))?", re.IGNORECASE)
_RE_TIME_TOKEN = re.compile(r"[0-2]?\d[:.]\d{2}")

def _detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"


def detect_language(text: str) -> str:
    """Public wrapper to detect the language of ``text``."""
    return _detect_language(text)

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
    stops = [t.text for t in doc if t.pos_ in {"PROPN", "NOUN"}]
    if not stops:
        stops = [t.text for t in doc if t.text and t.text[0].isupper()]

    # Filter out tokens that look like a time expression
    stops = [s for s in stops if not _RE_TIME_TOKEN.fullmatch(s)]

    m_from = regex["from"].search(text)
    m_to = regex["to"].search(text)

    if not m_from or not m_to:
        for alt_lang, alt_regex in LANG_REGEX.items():
            if alt_lang == lang:
                continue
            if not m_from:
                m_from = alt_regex["from"].search(text)
            if not m_to:
                m_to = alt_regex["to"].search(text)
            if m_from and m_to:
                break

    if m_from:
        from_stop = m_from.group(1).strip(" ,.")
    elif m_to:
        before = text[:m_to.start()].strip()
        if before:
            from_stop = before.split()[-1].strip(" ,.")
        elif stops:
            from_stop = stops.pop(0)
        else:
            from_stop = None
    elif stops:
        from_stop = stops.pop(0)
    else:
        from_stop = None

    if m_to:
        to_stop = m_to.group(1).strip(" ,.")
    elif stops:
        to_stop = stops.pop(0)
    else:
        to_stop = None

    time_match = _RE_TIME.search(text)
    if time_match:
        time = time_match.group(1).replace('.', ':')
    else:
        alt_match = _RE_TIME_ALT.search(text)
        if alt_match:
            hour = alt_match.group(1)
            minute = alt_match.group(2) or "00"
            try:
                h = int(hour)
                m = int(minute)
                time = f"{h:02d}:{m:02d}"
            except ValueError:
                time = None
        else:
            time = None

    result: Dict[str, Optional[str]] = {}
    if from_stop:
        result["from_stop"] = from_stop
    if to_stop:
        result["to_stop"] = to_stop
    if time:
        result["time"] = time
    result["lang"] = lang
    logger.debug("Parsed parameters: %s", result)
    return result


# --- new helper for endpoint detection ---

_KEYWORDS_DEPARTURES = {
    "de": ["abfahrt", "abfahrten"],
    "en": ["departure", "departures"],
    "it": ["partenza", "partenze"],
}

_KEYWORDS_STOPS = {
    "de": ["haltestelle", "haltestellen", "stop", "stops"],
    "en": ["stop", "stops", "station", "stations"],
    "it": ["fermata", "fermate"],
}

# Common suffixes indicating a stop or station.  If a text ends with one of
# these, ``classify_request`` treats the full text as a stop name.
_STOP_SUFFIXES = [
    "bahnhof",
    "busbahnhof",
    "station",
    "stazione",
]


def classify_request(text: str) -> Dict[str, str]:
    """Classify the user request and detect the language.

    The returned dictionary contains an ``endpoint`` key with one of
    ``"search"``, ``"departures"`` or ``"stops"``.  Additional parameters
    may be included for the chosen endpoint, similar to the ChatGPT helper.
    """

    lang = _detect_language(text)
    text_l = text.lower()

    for kw in _KEYWORDS_DEPARTURES.get(lang, []):
        if kw in text_l:
            return {"endpoint": "departures", "stop": text, "lang": lang}

    for kw in _KEYWORDS_STOPS.get(lang, []):
        if kw in text_l:
            return {"endpoint": "stops", "query": text, "lang": lang}

    # direct pattern "<stop1>-<stop2>" handled before more expensive parsing
    m_hyphen = re.fullmatch(r"\s*(.+?)\s*[-–]\s*(.+?)\s*", text)
    if m_hyphen:
        return {
            "endpoint": "search",
            "from_stop": m_hyphen.group(1).strip(),
            "to_stop": m_hyphen.group(2).strip(),
            "lang": lang,
        }

    params = parse_query(text)
    stops = [params.get("from_stop"), params.get("to_stop")]
    stops = [s for s in stops if s]

    if len(stops) == 1:
        return {"endpoint": "departures", "stop": stops[0], "lang": params.get("lang", lang)}

    if len(stops) == 2:
        for stop in stops:
            if any(stop.lower().endswith(suf) for suf in _STOP_SUFFIXES):
                return {"endpoint": "departures", "stop": text, "lang": params.get("lang", lang)}

    params["endpoint"] = "search"
    return params

