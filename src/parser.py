"""Very small rule-based parser for transport queries."""

import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Query:
    """Parsed query information."""

    type: str
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    datetime: Optional[str] = None
    language: Optional[str] = None
    include: Optional[List[str]] = None
    exclude: Optional[List[str]] = None
    long_distance: Optional[bool] = False


# relative date keywords
DATE_ONLY_RE = re.compile(
    r"^(heute|morgen|gestern|n(?:\xc3\xa4|ae)chsten sonntag|am wochenende)(?:\s+um\s+(?P<time>\d{1,2}:\d{2}))?$",
    re.I,
)
TRIP_RE = re.compile(
    r"von (?P<from>\w+) nach (?P<to>\w+)(?: um (?P<time>\d{1,2}:\d{2}))?",
    re.I,
)
# also handle "Bozen - Meran" style queries
TRIP_DASH_RE = re.compile(
    r"(?P<from>\w+)\s*[-\u2013]\s*(?P<to>\w+)(?:\s+um\s+(?P<time>\d{1,2}:\d{2}))?",
    re.I,
)
DEPT_RE = re.compile(r"abfahrten? (?P<stop>\w+)", re.I)
INCLUDE_RE = re.compile(r"mit (?P<modes>bus(?: und seilbahn)?)", re.I)
EXCLUDE_RE = re.compile(r"ohne (?P<modes>zug|fernverkehr)", re.I)


def relative_iso(text: str, time_str: Optional[str] = None) -> Optional[str]:
    """Return ISO timestamp for relative date keywords."""
    lower = text.lower()
    now = datetime.now()
    date = None
    if "heute" in lower:
        date = now.date()
    elif "morgen" in lower:
        date = now.date() + timedelta(days=1)
    elif "gestern" in lower:
        date = now.date() - timedelta(days=1)
    elif "n\xc3\xa4chsten sonntag" in lower or "naechsten sonntag" in lower:
        days = (6 - now.weekday()) % 7
        if days == 0:
            days = 7
        date = now.date() + timedelta(days=days)
    elif "am wochenende" in lower:
        days = (5 - now.weekday()) % 7
        if days <= 0:
            days += 7
        date = now.date() + timedelta(days=days)
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
    """Parse a German language query."""
    include_modes = []
    exclude_modes = []
    if m := INCLUDE_RE.search(text):
        modes = m.group("modes").lower()
        if "bus" in modes:
            include_modes.append("Bus")
        if "seilbahn" in modes:
            include_modes.append("Seilbahn")
    if m := EXCLUDE_RE.search(text):
        mode = m.group("modes").lower()
        if "zug" in mode:
            exclude_modes.append("Zug")
        if "fernverkehr" in mode:
            exclude_modes.append("Fernverkehr")

    if m := DATE_ONLY_RE.match(text.strip()):
        iso = relative_iso(text, m.group("time"))
        return Query(
            "unknown",
            datetime=iso,
            language="de",
            include=include_modes or None,
            exclude=exclude_modes or None,
        )

    match = TRIP_RE.search(text)
    if not match:
        match = TRIP_DASH_RE.search(text)
    if match:
        dt = match.group("time")
        iso = relative_iso(text, dt) if dt or DATE_ONLY_RE.search(text) else None
        if iso is None and dt:
            iso = f"2025-01-01T{dt}"
        return Query(
            "trip",
            match.group("from"),
            match.group("to"),
            iso,
            language="de",
            include=include_modes or None,
            exclude=exclude_modes or None,
            long_distance=False,
        )

    match = DEPT_RE.search(text)
    if match:
        return Query(
            "departure",
            from_location=match.group("stop"),
            language="de",
            include=include_modes or None,
            exclude=exclude_modes or None,
            long_distance=False,
        )

    return Query(
        "unknown",
        language="de",
        include=include_modes or None,
        exclude=exclude_modes or None,
        long_distance=False,
    )
