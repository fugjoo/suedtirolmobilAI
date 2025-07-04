"""Utility functions to create human readable summaries."""

from typing import Any, Dict, List


_TL = {
    "de": {
        "from": "Von",
        "to": "Nach",
        "departures_for": "Abfahrten {stop}:",
        "departures": "Abfahrten:",
        "direction": "Richtung",
        "platform": "Steig",
        "at": "um {time} Uhr",
        "on_foot": "zu Fu\u00df",
        "with": "mit {mode}",
        "stops_found": "Gefundene Haltestellen:",
        "arrival": "An:",
        "departure": "Ab:",
    },
    "en": {
        "from": "From",
        "to": "To",
        "departures_for": "Departures {stop}:",
        "departures": "Departures:",
        "direction": "Direction",
        "platform": "Platform",
        "at": "at {time}",
        "on_foot": "on foot",
        "with": "with {mode}",
        "stops_found": "Stops found:",
        "arrival": "Arr:",
        "departure": "Dep:",
    },
    "it": {
        "from": "Da",
        "to": "A",
        "departures_for": "Partenze {stop}:",
        "departures": "Partenze:",
        "direction": "Direzione",
        "platform": "Banchina",
        "at": "alle {time}",
        "on_foot": "a piedi",
        "with": "con {mode}",
        "stops_found": "Fermate trovate:",
        "arrival": "Arrivo:",
        "departure": "Partenza:",
    },
}


def _extract_time(data: Any) -> str:
    """Return a time string from different data structures."""
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        if data.get("time"):
            return str(data.get("time"))
        hour = data.get("hour")
        minute = data.get("minute")
        if hour is not None and minute is not None:
            try:
                hour_i = int(hour)
                minute_i = int(minute)
                return f"{hour_i:02d}:{minute_i:02d}"
            except (TypeError, ValueError):
                pass
    return ""


def _plural(word: str, count: int) -> str:
    """Return pluralized word depending on count."""
    return word if count == 1 else f"{word}s"


def format_search_result(
    result: Dict[str, Any], legs_only: bool = False, lang: str = "de"
) -> str:
    """Return a readable summary of a trip search result.

    Parameters
    ----------
    result: dict
        Parsed trip search response.
    legs_only: bool, optional
        If ``True`` only the individual trip legs are returned without the
        introductory "Von"/"Nach" lines.
    """
    if not isinstance(result, dict):
        return str(result)

    tl = _TL.get(lang, _TL["en"])

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
            header_parts.append(f"{tl['from'].lower()} {from_stop}")
        if to_stop:
            header_parts.append(f"{tl['to'].lower()} {to_stop}")
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
    if leg_list and not legs_only:
        first_leg = leg_list[0]
        origin = first_leg.get("origin") or first_leg.get("departure") or {}
        dest = first_leg.get("destination") or first_leg.get("arrival") or {}
        points = first_leg.get("points")
        if not origin and isinstance(points, list) and points:
            origin = points[0]
        if not dest and isinstance(points, list) and points:
            dest = points[-1]
        start_name = origin.get("name") or from_stop
        start_time = _extract_time(origin.get("time")) or _extract_time(origin.get("dateTime"))
        mode_name = (
            (first_leg.get("mode") or {}).get("name")
            or (first_leg.get("mode") or {}).get("number")
            or ""
        )
        if not mode_name or "fuß" in mode_name.lower() or "walk" in mode_name.lower():
            mode_desc = tl["on_foot"]
        else:
            mode_desc = tl["with"].format(mode=mode_name)
        origin_line = f"{tl['from']}: {start_name}"
        if start_time:
            origin_line += " " + tl["at"].format(time=start_time) + f" {mode_desc}"
        else:
            origin_line += f" {mode_desc}"
        lines.append(origin_line)
        dest_name = dest.get("name") or to_stop
        lines.append(f"{tl['to']}: {dest_name}")
    elif not legs_only:
        start_name = from_stop
        lines.append(f"{tl['from']}: {start_name}")
        if to_stop:
            lines.append(f"{tl['to']}: {to_stop}")

    if leg_list and not legs_only:
        lines.append("")

    for idx, leg in enumerate(leg_list):
        origin = leg.get("origin") or leg.get("departure") or {}
        dest = leg.get("destination") or leg.get("arrival") or {}
        points = leg.get("points")
        if not origin and isinstance(points, list) and points:
            origin = points[0]
        if not dest and isinstance(points, list) and points:
            dest = points[-1]
        o_name = origin.get("name", "")
        o_time = _extract_time(origin.get("time")) or _extract_time(origin.get("dateTime"))
        d_name = dest.get("name", "")
        d_time = _extract_time(dest.get("time")) or _extract_time(dest.get("dateTime"))
        line_name = (
            (leg.get("mode") or {}).get("name")
            or (leg.get("mode") or {}).get("number")
            or ""
        )
        if not line_name or "fuß" in line_name.lower() or "walk" in line_name.lower():
            if legs_only:
                line_desc = tl["on_foot"]
            else:
                line_desc = "zu Fuß"
        else:
            if legs_only:
                line_desc = line_name
            else:
                line_desc = tl["with"].format(mode=line_name)
            direction = (leg.get("mode") or {}).get("destination") or ""
            if direction:
                line_desc += f" {tl['direction']} {direction}"
        if legs_only:
            lines.append(line_desc)
            start_line = f"{o_time}: {o_name}" if o_time else o_name
            origin_platform = origin.get("platform") or origin.get("platformName")
            if origin_platform:
                start_line += f" von {tl['platform']} {origin_platform}"
            lines.append(start_line)
            end_line = f"{d_time}: {d_name}" if d_time else d_name
            platform = dest.get("platform") or dest.get("platformName")
            if platform:
                end_line += f" auf {tl['platform']} {platform}"
            lines.append(end_line)
        else:
            dep_line = f"{tl['departure']} {o_name}"
            if o_time:
                dep_line += " " + tl["at"].format(time=o_time) + f" {line_desc}"
            else:
                dep_line += f" {line_desc}"
            origin_platform = origin.get("platform") or origin.get("platformName")
            if origin_platform:
                dep_line += f" von {tl['platform']} {origin_platform}"
            arr_line = f"{tl['arrival']} {d_name}"
            if d_time:
                arr_line += " " + tl["at"].format(time=d_time)
            platform = dest.get("platform") or dest.get("platformName")
            if platform:
                arr_line += f" auf {tl['platform']} {platform}"
            lines.append(dep_line)
            lines.append(arr_line)
        if idx < len(leg_list) - 1:
            lines.append("")

    return "\n".join(lines)


def format_departures_result(result: Dict[str, Any], lang: str = "de") -> str:
    """Return a readable summary of departures."""
    if not isinstance(result, dict):
        return str(result)

    tl = _TL.get(lang, _TL["en"])

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

    lines = [tl["departures_for"].format(stop=stop_name)] if stop_name else [tl["departures"]]

    for dep in departures:
        planned_time = (
            _extract_time(dep.get("dateTime"))
            or _extract_time(dep.get("time"))
            or _extract_time((dep.get("departure") or {}).get("time"))
        )
        real_time = (
            _extract_time(dep.get("realDateTime"))
            or _extract_time((dep.get("departure") or {}).get("realDateTime"))
            or planned_time
        )
        delay = dep.get("servingLine", {}).get("delay")
        if delay is None and real_time and planned_time and real_time != planned_time:
            try:
                r_h, r_m = map(int, real_time.split(":"))
                p_h, p_m = map(int, planned_time.split(":"))
                delay = r_h * 60 + r_m - (p_h * 60 + p_m)
            except (ValueError, TypeError):
                delay = None
        try:
            delay = int(delay) if delay is not None else 0
        except (TypeError, ValueError):
            delay = 0
        if delay:
            sign = "+" if delay > 0 else "-"
            time = f"{real_time} ({planned_time} {sign}{abs(delay)})"
        else:
            time = real_time
        line_info = dep.get("servingLine") or dep.get("line") or {}
        line_name_part = line_info.get("name")
        line_number_part = line_info.get("number")
        line_parts = [p for p in (line_name_part, line_number_part) if p]
        line_name = " ".join(line_parts)
        direction = line_info.get("direction") or line_info.get("destination") or ""
        platform = dep.get("platformName") or dep.get("platform")

        parts = []
        if time:
            parts.append(time)
        if line_name:
            parts.append(line_name)
        if direction:
            parts.append(f"{tl['direction']} {direction}")
        if platform:
            parts.append(f"{tl['platform']} {platform}")

        entry = " ".join(parts)
        lines.append(entry.strip())

    return "\n".join(lines)


def format_stops_result(result: Dict[str, Any], lang: str = "de") -> str:
    """Return a readable summary of stop suggestions."""
    if not isinstance(result, dict):
        return str(result)

    tl = _TL.get(lang, _TL["en"])

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
    entries: List[Dict[str, Any]] = []
    best_entry = None
    best_quality = -1
    if isinstance(points, list):
        iterable = points
    elif isinstance(points, dict):
        iterable = [points]
    else:
        iterable = []

    for p in iterable:
        if not isinstance(p, dict) or not p.get("name"):
            continue
        entry_text = p["name"]
        any_type = p.get("anyType") or p.get("type") or ""
        if any_type:
            entry_text += f" ({any_type})"
        try:
            quality = int(p.get("quality"))
        except (TypeError, ValueError):
            quality = -1
        entry = {"text": entry_text, "type": any_type, "quality": quality}
        entries.append(entry)
        if quality > best_quality:
            best_quality = quality
            best_entry = entry

    if not entries:
        return "0 stops found."
    entries.sort(key=lambda e: e["type"])
    best_idx = entries.index(best_entry) if best_entry in entries else None

    lines = [tl["stops_found"]]
    for idx, entry in enumerate(entries):
        if best_idx is not None and idx == best_idx:
            lines.append(f"[TOP] {entry['text']}")
        else:
            lines.append(entry["text"])
    return "\n".join(lines)
