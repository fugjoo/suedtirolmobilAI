"""Very small rule-based parser for transport queries."""

import re
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Query:
    """Parsed query information."""

    type: str
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    datetime: Optional[str] = None
    line: Optional[str] = None
    language: Optional[str] = None
    include: Optional[List[str]] = None
    exclude: Optional[List[str]] = None
    long_distance: Optional[bool] = None


TRIP_RE = re.compile(
    r"von (?P<from>\w+) nach (?P<to>\w+)(?: um (?P<time>\d{1,2}:\d{2}))?",
    re.I,
)
DEPT_RE = re.compile(r"abfahrten? (?P<stop>\w+)", re.I)
INCLUDE_RE = re.compile(r"mit (?P<modes>bus(?: und seilbahn)?)", re.I)
EXCLUDE_RE = re.compile(r"ohne (?P<modes>zug|fernverkehr)", re.I)



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

    match = TRIP_RE.search(text)
    if match:
        dt = match.group("time")
        iso = None
        if dt:
            iso = f"2025-01-01T{dt}"
        return Query(
            "trip",
            match.group("from"),
            match.group("to"),
            iso,
            language="de",
            include=include_modes or None,
            exclude=exclude_modes or None,
            long_distance=None if "Fernverkehr" not in exclude_modes else False,
        )

    match = DEPT_RE.search(text)
    if match:
        return Query(
            "departure",
            from_location=match.group("stop"),
            language="de",
            include=include_modes or None,
            exclude=exclude_modes or None,
            long_distance=None if "Fernverkehr" not in exclude_modes else False,
        )

    return Query(
        "unknown",
        language="de",
        include=include_modes or None,
        exclude=exclude_modes or None,
        long_distance=None if "Fernverkehr" not in exclude_modes else False,
    )
