"""Simple wrapper for the Mentz EFA API."""

from typing import Optional, Dict, Any
import requests

from .config import get_efa_base_url

BASE_URL = get_efa_base_url()


def build_trip_params(
    origin: str,
    destination: str,
    datetime: Optional[str] = None,
    origin_stateless: Optional[str] = None,
    destination_stateless: Optional[str] = None,
    *,
    language: str = "de",
) -> Dict[str, Any]:
    """Return parameters for a trip request."""
    params: Dict[str, Any] = {"outputFormat": "JSON", "language": language}
    if origin_stateless:
        params["name_origin"] = origin_stateless
        params["type_origin"] = "stop"
    else:
        params["name_origin"] = origin
        params["type_origin"] = "any"

    if destination_stateless:
        params["name_destination"] = destination_stateless
        params["type_destination"] = "stop"
    else:
        params["name_destination"] = destination
        params["type_destination"] = "any"

    if datetime:
        date, time = datetime.split("T")
        params["itdDate"] = date
        params["itdTime"] = time
    return params


def build_departure_params(
    stop: str,
    limit: int = 5,
    stateless: Optional[str] = None,
    *,
    language: str = "de",
) -> Dict[str, Any]:
    """Return parameters for a departure monitor request."""
    params: Dict[str, Any] = {
        "mode": "direct",
        "limit": limit,
        "outputFormat": "JSON",
        "language": language,
    }
    if stateless:
        params["name_dm"] = stateless
        params["type_dm"] = "stop"
    else:
        params["name_dm"] = stop
        params["type_dm"] = "stop"
    return params


def trip_request(
    origin: str,
    destination: str,
    datetime: Optional[str] = None,
    origin_stateless: Optional[str] = None,
    destination_stateless: Optional[str] = None,
    *,
    language: str = "de",
) -> Dict[str, Any]:
    """Request a trip from origin to destination."""
    params = build_trip_params(
        origin,
        destination,
        datetime,
        origin_stateless=origin_stateless,
        destination_stateless=destination_stateless,
        language=language,
    )
    response = requests.get(f"{BASE_URL}/XML_TRIP_REQUEST2", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def departure_monitor(
    stop: str,
    limit: int = 5,
    stateless: Optional[str] = None,
    *,
    language: str = "de",
) -> Dict[str, Any]:
    """Return upcoming departures for a stop."""
    params = build_departure_params(
        stop, limit, stateless=stateless, language=language
    )
    response = requests.get(f"{BASE_URL}/XML_DM_REQUEST", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def stop_finder(query: str, *, language: str = "de") -> Dict[str, Any]:
    """Find stop name suggestions for a query."""
    params = {
        "name_sf": query,
        "odvSugMacro": "true",
        "outputFormat": "JSON",
        "language": language,
    }
    response = requests.get(f"{BASE_URL}/XML_STOPFINDER_REQUEST", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def best_point(points: Any) -> Optional[Dict[str, Any]]:
    """Return the point entry with the highest quality."""
    if not points:
        return None

    if isinstance(points, dict):
        if "point" in points:
            points = points["point"]
        if isinstance(points, dict):
            return points

    if isinstance(points, list):
        items = [p for p in points if isinstance(p, dict)]
        if not items:
            return None
        return max(items, key=lambda p: int(p.get("quality", 0)))

    return None
