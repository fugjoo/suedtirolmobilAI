"""Handlers that normalize raw EFA payloads into application level schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

from .schemas import Departure, NormalizedError, RealtimeInfo, StopLocation


def _ensure_iterable(points: Any) -> Iterable[MutableMapping[str, Any]]:
    if points is None:
        return []
    if isinstance(points, Mapping):
        return [points]  # type: ignore[list-item]
    return points  # type: ignore[return-value]


def normalize_stop_finder(payload: Mapping[str, Any]) -> List[StopLocation]:
    """Normalize the response coming from the EFA stopFinder endpoint."""

    stop_finder = payload.get("stopFinder", {})
    points = stop_finder.get("points", {}).get("point")
    point_items = list(_ensure_iterable(points))

    best_score = max((int(item.get("matchQuality", 0)) for item in point_items), default=0)
    normalized: List[StopLocation] = []

    for item in point_items:
        ref = item.get("ref", {})
        coord = item.get("coord", {})
        match_score = int(item.get("matchQuality", 0))
        normalized.append(
            StopLocation(
                id=str(ref.get("id") or ref.get("extId") or ref.get("gid")),
                gid=ref.get("gid"),
                name=ref.get("name", ""),
                type=str(ref.get("type", "stop")),
                latitude=float(coord.get("lat")),
                longitude=float(coord.get("lon")),
                match_score=match_score,
                is_best_match=match_score == best_score,
                products=item.get("productCategories", []),
            )
        )

    return normalized


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


def normalize_departure_monitor(payload: Mapping[str, Any]) -> List[Departure]:
    """Normalize a departureMonitor/arrivalMonitor response."""

    monitor = payload.get("monitor", {})
    entries = list(_ensure_iterable(monitor.get("journeys")))
    movement_type = str(monitor.get("type", "departures")).lower()

    normalized: List[Departure] = []
    for entry in entries:
        planned_time = _parse_datetime(entry.get("scheduledTime"))
        realtime_time = _parse_datetime(entry.get("realtimeTime"))
        realtime_source = entry.get("realtimeSource")
        realtime_updated = _parse_datetime(entry.get("lastUpdated"))

        delay_seconds: int = 0
        is_realtime = bool(entry.get("realtime", False) and realtime_time)
        if planned_time and realtime_time:
            delay_seconds = int((realtime_time - planned_time).total_seconds())
        remarks = entry.get("remarks") or []

        normalized.append(
            Departure(
                id=str(entry.get("id")),
                line=str(entry.get("servingLine", {}).get("name")),
                direction=str(entry.get("direction")),
                planned_time=planned_time,
                estimated_time=realtime_time,
                platform=entry.get("platform"),
                movement_type="arrival" if movement_type == "arrivals" else "departure",
                realtime=RealtimeInfo(
                    is_realtime=is_realtime,
                    delay_seconds=delay_seconds,
                    source=realtime_source,
                    updated_at=realtime_updated,
                ),
                remarks=list(remarks),
            )
        )

    return normalized


_ERROR_CATEGORY_MAP: Dict[str, str] = {
    "H430": "not_found",
    "H895": "not_found",
    "H730": "unavailable",
    "H931": "unavailable",
    "H922": "invalid_request",
}

_DEFAULT_MESSAGES: Dict[str, str] = {
    "H430": "Stop could not be resolved",
    "H730": "Upstream realtime data source is temporarily unavailable",
    "H922": "The request contained invalid parameters",
}


def map_error_response(payload: Mapping[str, Any]) -> NormalizedError:
    """Map a raw error payload into a :class:`NormalizedError`."""

    error_block = payload.get("error") or payload.get("serviceError")
    if not error_block:
        raise ValueError("Payload does not contain an error section")

    code = str(error_block.get("code") or error_block.get("id") or "UNKNOWN")
    message = error_block.get("message") or error_block.get("text") or ""

    category = _ERROR_CATEGORY_MAP.get(code, "unknown")
    default_message = _DEFAULT_MESSAGES.get(code, "Unexpected response from EFA backend")
    final_message = message.strip() or default_message

    details = {
        key: value
        for key, value in error_block.items()
        if key not in {"code", "id", "message", "text"}
    }

    return NormalizedError(code=code, category=category, message=final_message, details=details)
