"""Utility functions to create human readable summaries."""

from typing import Any, Dict, List


def _plural(word: str, count: int) -> str:
    """Return pluralized word depending on count."""
    return word if count == 1 else f"{word}s"


def format_search_result(result: Dict[str, Any]) -> str:
    """Return a readable summary of a trip search result."""
    if not isinstance(result, dict):
        return str(result)

    from_stop = (
        result.get("from_stop")
        or result.get("origin", {}).get("name")
        or ""
    )
    to_stop = (
        result.get("to_stop")
        or result.get("destination", {}).get("name")
        or ""
    )

    raw_trips = result.get("trips")
    trips: List[Dict[str, Any]] = []
    if isinstance(raw_trips, list):
        trips = raw_trips
    elif isinstance(raw_trips, dict):
        trip_data = raw_trips.get("trip")
        if isinstance(trip_data, list):
            trips = trip_data
        elif isinstance(trip_data, dict):
            trips = [trip_data]
        elif raw_trips:
            trips = [raw_trips]

    if not trips:
        count = 0
    else:
        count = len(trips)

    header_parts = []
    if from_stop:
        header_parts.append(f"from {from_stop}")
    if to_stop:
        header_parts.append(f"to {to_stop}")
    header = " ".join(header_parts) if header_parts else "found"

    lines = [f"{count} {_plural('trip', count)} {header}:"] if trips else [f"0 trips {header}."]

    for trip in trips:
        legs = trip.get("legs") or trip.get("legList") or {}
        if isinstance(legs, dict):
            leg_items = legs.get("leg") or legs
        else:
            leg_items = legs
        if isinstance(leg_items, dict):
            leg_list = [leg_items]
        elif isinstance(leg_items, list):
            leg_list = leg_items
        else:
            leg_list = []

        start_time = ""
        end_time = ""
        line_names: List[str] = []
        if leg_list:
            first = leg_list[0]
            last = leg_list[-1]
            start_time = (
                (first.get("departure") or first.get("origin") or {}).get("time")
                or ""
            )
            end_time = (
                (last.get("arrival") or last.get("destination") or {}).get("time")
                or ""
            )
            for leg in leg_list:
                name = (
                    (leg.get("mode") or {}).get("name")
                    or (leg.get("mode") or {}).get("number")
                )
                if name:
                    line_names.append(name)
        else:
            start_time = (
                trip.get("departure", {}).get("time")
                or trip.get("origin", {}).get("time")
                or ""
            )
            end_time = (
                trip.get("arrival", {}).get("time")
                or trip.get("destination", {}).get("time")
                or ""
            )

        duration = trip.get("duration") or ""
        mode_str = " > ".join(line_names)
        parts = [p for p in [start_time, end_time] if p]
        time_range = " → ".join(parts)
        info = f"{time_range}" if time_range else ""
        if duration:
            info = f"{info} ({duration})" if info else duration
        if mode_str:
            info = f"{info} {mode_str}" if info else mode_str
        lines.append(f"- {info}".rstrip())

    return "\n".join(lines)


def format_departures_result(result: Dict[str, Any]) -> str:
    """Return a readable summary of departures."""
    if not isinstance(result, dict):
        return str(result)

    stop_name = (
        result.get("stop_name")
        or result.get("stopName")
        or result.get("stop", {}).get("name")
        or result.get("name")
        or ""
    )

    departures = (
        result.get("departures")
        or result.get("departureList")
        or result.get("stopEvents")
    )
    count = 0
    if isinstance(departures, list):
        count = len(departures)
    elif departures:
        count = 1

    suffix = f" for '{stop_name}'" if stop_name else ""
    return f"{count} {_plural('departure', count)}{suffix}."


def format_stops_result(result: Dict[str, Any]) -> str:
    """Return a readable summary of stop suggestions."""
    if not isinstance(result, dict):
        return str(result)

    # Gracefully handle missing or null fields in the nested structure
    stopfinder = result.get("stopFinder") or {}
    points_data = stopfinder.get("points") or {}
    points = points_data.get("point") or result.get("stops")
    names: List[str] = []
    count = 0
    if isinstance(points, list):
        count = len(points)
        for p in points:
            if isinstance(p, dict) and p.get("name"):
                names.append(p["name"])
    elif isinstance(points, dict):
        count = 1
        if points.get("name"):
            names.append(points["name"])

    if names:
        shown = ", ".join(names[:3])
        if len(names) > 3:
            shown += " ..."
        return f"{count} {_plural('stop', count)} found: {shown}"
    return f"{count} {_plural('stop', count)} found."
