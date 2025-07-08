"""Very small rule-based parser for transport queries."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Query:
    """Parsed query information."""

    type: str
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    datetime: Optional[str] = None
    line: Optional[str] = None


TRIP_RE = re.compile(r"von (?P<from>\w+) nach (?P<to>\w+)(?: um (?P<time>\d{1,2}:\d{2}))?", re.I)
DEPT_RE = re.compile(r"abfahrten? (?P<stop>\w+)", re.I)


def parse(text: str) -> Query:
    """Parse a German language query."""
    match = TRIP_RE.search(text)
    if match:
        dt = match.group("time")
        iso = None
        if dt:
            iso = f"2025-01-01T{dt}"
        return Query("trip", match.group("from"), match.group("to"), iso)

    match = DEPT_RE.search(text)
    if match:
        return Query("departure", from_location=match.group("stop"))

    return Query("unknown")
