"""Simple wrapper for the Mentz EFA API."""

from typing import Optional, Dict, Any
import os
import logging
import datetime as dt
import requests
from . import request_logger

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("EFA_BASE_URL", "https://efa.sta.bz.it/apb")


def build_trip_params(
    origin: str,
    destination: str,
    datetime: Optional[str] = None,
    origin_stateless: Optional[str] = None,
    destination_stateless: Optional[str] = None,
    *,
    origin_type: Optional[str] = None,
    destination_type: Optional[str] = None,
    bus: bool = True,
    zug: bool = True,
    seilbahn: bool = True,
    long_distance: Optional[bool] = None,
    datetime_mode: str = "dep",
    last_connection: bool = False,
    language: str = "de",
) -> Dict[str, Any]:
    """Return parameters for a trip request.

    If ``last_connection`` is ``True``, the API is asked for the latest
    possible connection of the day by setting ``calcMode`` to ``"last"`` and
    defaulting the time to ``23:59`` when no explicit datetime is supplied.
    """
    params: Dict[str, Any] = {
        "outputFormat": "JSON",
        "language": language,
        "odvMacro": "true",
        "includedMeans": "checkbox",
    }

    if bus:
        params["inclMOT_BUS"] = "true"
    if zug:
        params["inclMOT_ZUG"] = "true"
    if seilbahn:
        params["inclMOT_8"] = "true"
    if origin_stateless:
        params["name_origin"] = origin_stateless
        params["type_origin"] = "stop"
    else:
        params["name_origin"] = origin
        params["type_origin"] = origin_type or "any"

    if destination_stateless:
        params["name_destination"] = destination_stateless
        params["type_destination"] = "stop"
    else:
        params["name_destination"] = destination
        params["type_destination"] = destination_type or "any"

    params["itdTripDateTimeDepArr"] = datetime_mode
    if datetime:
        try:
            dt_value = dt.datetime.fromisoformat(datetime)
            params["itdDate"] = dt_value.strftime("%Y%m%d")
            params["itdTime"] = dt_value.strftime("%H:%M")
        except ValueError:
            logger.warning("Invalid datetime string: %s", datetime)
    elif last_connection:
        now = dt.datetime.now()
        params["itdDate"] = now.strftime("%Y%m%d")
        params["itdTime"] = "23:59"

    if last_connection:
        params["calcMode"] = "last"

    if long_distance is False:
        params["lineRestriction"] = "401"
    else:
        params["lineRestriction"] = "400"
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
    origin_type: Optional[str] = None,
    destination_type: Optional[str] = None,
    bus: bool = True,
    zug: bool = True,
    seilbahn: bool = True,
    long_distance: Optional[bool] = None,
    datetime_mode: str = "dep",
    last_connection: bool = False,
    language: str = "de",
) -> Dict[str, Any]:
    """Request a trip from origin to destination."""
    params = build_trip_params(
        origin,
        destination,
        datetime,
        origin_stateless=origin_stateless,
        destination_stateless=destination_stateless,
        origin_type=origin_type,
        destination_type=destination_type,
        bus=bus,
        zug=zug,
        seilbahn=seilbahn,
        long_distance=long_distance,
        datetime_mode=datetime_mode,
        last_connection=last_connection,
        language=language,
    )
    url = f"{BASE_URL}/XML_TRIP_REQUEST2"
    logger.debug("EFA request %s %s", url, params)
    full_url = requests.Request("GET", url, params=params).prepare().url
    request_logger.log_entry({"url": full_url})
    response = requests.get(url, params=params, timeout=10)
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
    url = f"{BASE_URL}/XML_DM_REQUEST"
    logger.debug("EFA request %s %s", url, params)
    full_url = requests.Request("GET", url, params=params).prepare().url
    request_logger.log_entry({"url": full_url})
    response = requests.get(url, params=params, timeout=10)
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
    url = f"{BASE_URL}/XML_STOPFINDER_REQUEST"
    logger.debug("EFA request %s %s", url, params)
    full_url = requests.Request("GET", url, params=params).prepare().url
    request_logger.log_entry({"url": full_url})
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def best_point(points: Any) -> Optional[Dict[str, Any]]:
    """Return the stop entry with the highest quality.

    Entries of type ``stop`` are preferred. If no such entry exists, the
    highest quality item from the provided list is returned.
    """
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
        stop_items = [p for p in items if p.get("anyType") == "stop"]
        ranked = stop_items or items
        return max(ranked, key=lambda p: int(p.get("quality", 0)))

    return None
