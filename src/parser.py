"""Very small rule-based parser for transport queries.

This module supports short queries in German, Italian and English.
"""

import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Query:
    """Parsed query information.

    ``bus``, ``zug`` and ``seilbahn`` toggle the respective transport modes.
    ``datetime_mode`` controls whether ``datetime`` refers to a departure
    (``"dep"``) or arrival time (``"arr"").
    """

    type: str
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    datetime: Optional[str] = None
    language: Optional[str] = None
    bus: bool = True
    zug: bool = True
    seilbahn: bool = True
    long_distance: Optional[bool] = False
    datetime_mode: str = "dep"


# relative date keywords
DATE_ONLY_RE = re.compile(
    r"^(heute|morgen|gestern|n(?:\xc3\xa4|ae)chsten sonntag|am wochenende)(?:\s+um\s+(?P<time>\d{1,2}:\d{2}))?$",
    re.I,
)
TRIP_RE = re.compile(
    r"(?:von|from|da) (?P<from>\w+) (?:nach|to|a) (?P<to>\w+)(?: um (?P<time>\d{1,2}:\d{2}))?",
    re.I,
)
# also handle "Bozen - Meran" style queries
TRIP_DASH_RE = re.compile(
    r"(?P<from>\w+)\s*[-\u2013]\s*(?P<to>\w+)(?:\s+um\s+(?P<time>\d{1,2}:\d{2}))?",
    re.I,
)
DEPT_RE = re.compile(r"(?:abfahrten?|departures?|partenze) (?P<stop>\w+)", re.I)
ARRIVAL_WORDS = {"ankommen", "ankunft", "arrive", "arrival", "arrivo"}
DEPARTURE_WORDS = {"abfahren", "abfahrt", "depart", "departure", "partenza"}

WITH_WORDS = {"mit", "with", "con"}
WITHOUT_WORDS = {"ohne", "without", "senza"}
ONLY_WORDS = {"nur", "only", "solo"}
BUS_TERMS = {"bus", "autobus"}
TRAIN_TERMS = {"zug", "train", "treno"}
SEILBAHN_TERMS = {"seilbahn", "cable car", "cablecar", "funivia"}
LONG_DISTANCE_TERMS = {
    "fernverkehr",
    "long distance",
    "long-distance",
    "longdistance",
    "lunga distanza",
}


TODAY_WORDS = {"heute", "today", "oggi"}
TOMORROW_WORDS = {"morgen", "tomorrow", "domani"}
YESTERDAY_WORDS = {"gestern", "yesterday", "ieri"}
NEXT_SUNDAY_WORDS = {
    "n\u00e4chsten sonntag",
    "naechsten sonntag",
    "next sunday",
    "domenica prossima",
    "prossima domenica",
}
WEEKEND_WORDS = {
    "am wochenende",
    "this weekend",
    "next weekend",
    "at the weekend",
    "nel weekend",
    "nel fine settimana",
    "fine settimana",
    "weekend",
}

# map weekday phrases to weekday numbers
WEEKDAY_WORDS = {
    0: {"montag", "am montag", "monday", "on monday", "lunedi", "luned\u00ec"},
    1: {"dienstag", "am dienstag", "tuesday", "on tuesday", "martedi", "marted\u00ec"},
    2: {
        "mittwoch",
        "am mittwoch",
        "wednesday",
        "on wednesday",
        "mercoledi",
        "mercoled\u00ec",
    },
    3: {
        "donnerstag",
        "am donnerstag",
        "thursday",
        "on thursday",
        "giovedi",
        "gioved\u00ec",
    },
    4: {"freitag", "am freitag", "friday", "on friday", "venerdi", "venerd\u00ec"},
    5: {
        "samstag",
        "am samstag",
        "saturday",
        "on saturday",
        "sabato",
    },
    6: {"sonntag", "am sonntag", "sunday", "on sunday", "domenica"},
}

# map "next <weekday>" phrases to weekday numbers
NEXT_WEEKDAY_WORDS = {
    0: {
        "n\u00e4chsten montag",
        "naechsten montag",
        "next monday",
        "lunedi prossimo",
        "prossimo lunedi",
    },
    1: {
        "n\u00e4chsten dienstag",
        "naechsten dienstag",
        "next tuesday",
        "martedi prossimo",
        "prossimo martedi",
    },
    2: {
        "n\u00e4chsten mittwoch",
        "naechsten mittwoch",
        "next wednesday",
        "mercoledi prossimo",
        "prossimo mercoledi",
    },
    3: {
        "n\u00e4chsten donnerstag",
        "naechsten donnerstag",
        "next thursday",
        "giovedi prossimo",
        "prossimo giovedi",
    },
    4: {
        "n\u00e4chsten freitag",
        "naechsten freitag",
        "next friday",
        "venerdi prossimo",
        "prossimo venerdi",
    },
    5: {
        "n\u00e4chsten samstag",
        "naechsten samstag",
        "next saturday",
        "sabato prossimo",
        "prossimo sabato",
    },
    6: {
        "n\u00e4chsten sonntag",
        "naechsten sonntag",
        "next sunday",
        "domenica prossima",
        "prossima domenica",
    },
}


def relative_iso(text: str, time_str: Optional[str] = None) -> Optional[str]:
    """Return ISO timestamp for relative date keywords across languages."""
    lower = text.lower()
    now = datetime.now()
    date = None
    if any(word in lower for word in TODAY_WORDS):
        date = now.date()
    elif any(word in lower for word in TOMORROW_WORDS):
        date = now.date() + timedelta(days=1)
    elif any(word in lower for word in YESTERDAY_WORDS):
        date = now.date() - timedelta(days=1)
    elif any(word in lower for word in NEXT_SUNDAY_WORDS):
        days = (6 - now.weekday()) % 7
        if days == 0:
            days = 7
        date = now.date() + timedelta(days=days)
    elif any(word in lower for word in WEEKEND_WORDS):
        days = (5 - now.weekday()) % 7
        if days <= 0:
            days += 7
        date = now.date() + timedelta(days=days)
    else:
        for wd, terms in NEXT_WEEKDAY_WORDS.items():
            if any(term in lower for term in terms):
                days = (wd - now.weekday()) % 7
                if days == 0:
                    days = 7
                date = now.date() + timedelta(days=days)
                break
        if date is None:
            for wd, terms in WEEKDAY_WORDS.items():
                if any(term in lower for term in terms):
                    days = (wd - now.weekday()) % 7
                    if days == 0:
                        days = 7
                    date = now.date() + timedelta(days=days)
                    break
    if date is None:
        return None
    if time_str:
        try:
            t_value = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return None
    else:
        t_value = now.time().replace(second=0, microsecond=0)
    return datetime.combine(date, t_value).strftime("%Y-%m-%dT%H:%M")



def parse(text: str) -> Query:
    """Parse a short query in German, Italian or English."""
    lower = text.lower()
    bus = True
    zug = True
    seilbahn = True
    long_distance = False
    datetime_mode = "arr" if any(w in lower for w in ARRIVAL_WORDS) else "dep"

    for w in WITHOUT_WORDS:
        if any(f"{w} {t}" in lower for t in BUS_TERMS):
            bus = False
        if any(f"{w} {t}" in lower for t in TRAIN_TERMS):
            zug = False
        if any(f"{w} {t}" in lower for t in SEILBAHN_TERMS):
            seilbahn = False
        if any(f"{w} {t}" in lower for t in LONG_DISTANCE_TERMS):
            long_distance = False

    for w in WITH_WORDS:
        if any(f"{w} {t}" in lower for t in BUS_TERMS):
            bus = True
        if any(f"{w} {t}" in lower for t in TRAIN_TERMS):
            zug = True
        if any(f"{w} {t}" in lower for t in SEILBAHN_TERMS):
            seilbahn = True
        if any(f"{w} {t}" in lower for t in LONG_DISTANCE_TERMS):
            long_distance = True

    for w in ONLY_WORDS:
        if any(f"{w} {t}" in lower for t in BUS_TERMS):
            bus = True
            zug = False
            seilbahn = False
        if any(f"{w} {t}" in lower for t in TRAIN_TERMS):
            bus = False
            zug = True
            seilbahn = False
        if any(f"{w} {t}" in lower for t in SEILBAHN_TERMS):
            bus = False
            zug = False
            seilbahn = True
        if any(f"{w} {t}" in lower for t in LONG_DISTANCE_TERMS):
            bus = False
            zug = False
            seilbahn = False
            long_distance = True

    tokens = set(lower.split())
    has_bus = any(t in tokens for t in BUS_TERMS)
    has_train = any(t in tokens for t in TRAIN_TERMS)
    has_seilbahn = any(t in tokens for t in SEILBAHN_TERMS)
    has_long_distance = any(t in tokens for t in LONG_DISTANCE_TERMS)

    if has_bus and not has_train and not has_seilbahn and not has_long_distance:
        bus = True
        zug = False
        seilbahn = False
    elif has_train and not has_bus and not has_seilbahn and not has_long_distance:
        bus = False
        zug = True
        seilbahn = False
    elif has_seilbahn and not has_bus and not has_train and not has_long_distance:
        bus = False
        zug = False
        seilbahn = True
    elif has_long_distance and not has_bus and not has_train and not has_seilbahn:
        bus = False
        zug = False
        seilbahn = False
        long_distance = True

    if m := DATE_ONLY_RE.match(text.strip()):
        iso = relative_iso(text, m.group("time"))
        if iso is None:
            iso = datetime.now().strftime("%Y-%m-%dT%H:%M")
        return Query(
            "unknown",
            datetime=iso,
            language="de",
            bus=bus,
            zug=zug,
            seilbahn=seilbahn,
            long_distance=long_distance,
            datetime_mode=datetime_mode,
        )

    match = TRIP_RE.search(text)
    if not match:
        match = TRIP_DASH_RE.search(text)
    if match:
        dt_val = match.group("time")
        iso = relative_iso(text, dt_val)
        if iso is None:
            if dt_val:
                iso = f"2025-01-01T{dt_val}"
            else:
                iso = datetime.now().strftime("%Y-%m-%dT%H:%M")
        return Query(
            "trip",
            match.group("from"),
            match.group("to"),
            iso,
            language="de",
            bus=bus,
            zug=zug,
            seilbahn=seilbahn,
            long_distance=long_distance,
            datetime_mode=datetime_mode,
        )

    match = DEPT_RE.search(text)
    if match:
        return Query(
            "departure",
            from_location=match.group("stop"),
            language="de",
            bus=bus,
            zug=zug,
            seilbahn=seilbahn,
            long_distance=long_distance,
            datetime_mode=datetime_mode,
        )

    return Query(
        "unknown",
        language="de",
        bus=bus,
        zug=zug,
        seilbahn=seilbahn,
        long_distance=long_distance,
        datetime_mode=datetime_mode,
    )
