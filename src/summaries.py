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
        header_parts = []
        if from_stop:
            header_parts.append(f"from {from_stop}")
        if to_stop:
            header_parts.append(f"to {to_stop}")
        header = " ".join(header_parts) if header_parts else "found"
        return f"0 trips {header}."

    trip = trips[0]
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

    lines: List[str] = []

    for idx, leg in enumerate(leg_list):
        origin = leg.get("origin") or leg.get("departure") or {}
        dest = leg.get("destination") or leg.get("arrival") or {}
        points = leg.get("points")
        if not origin and isinstance(points, list) and points:
            origin = points[0]
        if not dest and isinstance(points, list) and points:
            dest = points[-1]
        o_name = origin.get("name", "")
        o_time = origin.get("time") or (origin.get("dateTime") or {}).get("time", "")
        d_name = dest.get("name", "")
        d_time = dest.get("time") or (dest.get("dateTime") or {}).get("time", "")
        line_name = (
            (leg.get("mode") or {}).get("name")
            or (leg.get("mode") or {}).get("number")
            or ""
        )
        if not line_name or "fuß" in line_name.lower() or "walk" in line_name.lower():
            line_desc = "zu Fuß"
        else:
            line_desc = f"mit {line_name}"
            direction = (leg.get("mode") or {}).get("destination") or ""
            if direction:
                line_desc += f" Richtung {direction}"
        dep_line = f"Ab: {o_name}"
        if o_time:
            dep_line += f" um {o_time} Uhr {line_desc}"
        else:
            dep_line += f" {line_desc}"
        origin_platform = origin.get("platform") or origin.get("platformName")
        if origin_platform:
            dep_line += f" von Steig {origin_platform}"
        arr_line = f"An: {d_name}"
        if d_time:
            arr_line += f" um {d_time} Uhr"
        platform = dest.get("platform") or dest.get("platformName")
        if platform:
            arr_line += f" auf Steig {platform}"
        lines.append(dep_line)
        lines.append(arr_line)
        if idx < len(leg_list) - 1:
            lines.append("")

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

    raw_departures = (
        result.get("departures")
        or result.get("departureList")
        or result.get("stopEvents")
    )
    if isinstance(raw_departures, dict):
        dep_items = raw_departures.get("departure") or raw_departures.get("stopEvent") or raw_departures
    else:
        dep_items = raw_departures

    departures: List[Dict[str, Any]] = []
    if isinstance(dep_items, list):
        departures = dep_items
    elif isinstance(dep_items, dict):
        departures = [dep_items]

    if not departures:
        suffix = f" for '{stop_name}'" if stop_name else ""
        return f"0 departures{suffix}."

    lines = [f"Abfahrten für {stop_name}:"] if stop_name else ["Abfahrten:"]

    for dep in departures:
        time = (
            dep.get("time")
            or dep.get("departure", {}).get("time")
            or (dep.get("dateTime") or {}).get("time")
            or ""
        )
        line_info = dep.get("servingLine") or dep.get("line") or {}
        line_name = line_info.get("name") or ""
        line_number = line_info.get("number") or ""
        line_display = line_name
        if line_number and line_number not in line_display:
            line_display = f"{line_display} {line_number}".strip()
        direction = line_info.get("direction") or line_info.get("destination") or ""
        platform = dep.get("platformName") or dep.get("platform")

        parts = []
        if line_display:
            parts.append(line_display)
        if direction:
            parts.append(f"Richtung {direction}")
        if platform:
            parts.append(f"Steig {platform}")
        if time:
            parts.append(f"um {time} Uhr")

        entry = " ".join(parts)
        lines.append(entry.strip())

    return "\n".join(lines)


def format_stops_result(result: Dict[str, Any]) -> str:
    """Return a readable summary of stop suggestions."""
    if not isinstance(result, dict):
        return str(result)

    # Gracefully handle missing or null fields in the nested structure
    stopfinder = result.get("stopFinder")
    if not isinstance(stopfinder, dict):
        stopfinder = {}

    points_data = stopfinder.get("points")
    if isinstance(points_data, dict):
        points = points_data.get("point")
    elif isinstance(points_data, list):
        points = points_data
    else:
        points = None

    if not points:
        points = result.get("stops")
    results: List[Dict[str, Any]] = []
    if isinstance(points, list):
        for p in points:
            if not isinstance(p, dict) or not p.get("name"):
                continue
            entry = p["name"]
            any_type = p.get("anyType") or p.get("type")
            if any_type:
                entry += f" ({any_type})"
            try:
                quality = int(p.get("quality"))
            except (TypeError, ValueError):
                quality = -1
            results.append({"entry": entry, "quality": quality, "type": any_type or ""})
    elif isinstance(points, dict):
        if points.get("name"):
            entry = points["name"]
            any_type = points.get("anyType") or points.get("type")
            if any_type:
                entry += f" ({any_type})"
            try:
                quality = int(points.get("quality"))
            except (TypeError, ValueError):
                quality = -1
            results.append({"entry": entry, "quality": quality, "type": any_type or ""})

    if not results:
        return "0 stops found."

    type_order = {"stop": 0, "location": 1, "address": 2, "street": 3}
    results.sort(key=lambda r: (type_order.get(r["type"], 99), r["entry"]))

    best_idx = None
    if any(r["quality"] >= 0 for r in results):
        best_idx = max(range(len(results)), key=lambda i: results[i]["quality"]) 

    lines = ["Gefundene Haltestellen:"]
    for idx, r in enumerate(results):
        line = r["entry"]
        if best_idx is not None and idx == best_idx:
            line += " [beste]"
        lines.append(line)

    return "\n".join(lines)
