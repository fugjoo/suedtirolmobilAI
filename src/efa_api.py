"""Simple wrapper for the Mentz EFA API."""

from typing import Optional, Dict, Any
import os
import requests

BASE_URL = os.getenv("EFA_BASE_URL", "https://efa.sta.bz.it/apb")


def trip_request(origin: str, destination: str, datetime: Optional[str] = None) -> Dict[str, Any]:
    """Request a trip from origin to destination."""
    params = {
        "name_origin": origin,
        "type_origin": "any",
        "name_destination": destination,
        "type_destination": "any",
        "outputFormat": "JSON",
    }
    if datetime:
        date, time = datetime.split("T")
        params["itdDate"] = date
        params["itdTime"] = time
    response = requests.get(f"{BASE_URL}/XML_TRIP_REQUEST2", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def departure_monitor(stop: str, limit: int = 5) -> Dict[str, Any]:
    """Return upcoming departures for a stop."""
    params = {
        "name_dm": stop,
        "type_dm": "stop",
        "mode": "direct",
        "limit": limit,
        "outputFormat": "JSON",
    }
    response = requests.get(f"{BASE_URL}/XML_DM_REQUEST", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def stop_finder(query: str) -> Dict[str, Any]:
    """Find stop name suggestions for a query."""
    params = {
        "name_sf": query,
        "odvSugMacro": "true",
        "outputFormat": "JSON",
    }
    response = requests.get(f"{BASE_URL}/XML_STOPFINDER_REQUEST", params=params, timeout=10)
    response.raise_for_status()
    return response.json()
