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

    trips = result.get("trips")
    count = 0
    if isinstance(trips, list):
        count = len(trips)
    elif isinstance(trips, dict):
        trip_data = trips.get("trip")
        if isinstance(trip_data, list):
            count = len(trip_data)
        elif trip_data:
            count = 1
        else:
            count = len(trips)

    if not from_stop and not to_stop:
        return f"{count} {_plural('trip', count)} found."
    if not from_stop:
        return f"{count} {_plural('trip', count)} to {to_stop}."
    if not to_stop:
        return f"{count} {_plural('trip', count)} from {from_stop}."
    return f"{count} {_plural('trip', count)} from {from_stop} to {to_stop}."


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
