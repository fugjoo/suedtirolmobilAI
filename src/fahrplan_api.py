"""Wrappers around the existing Fahrplan API endpoints."""

from typing import Any, Dict

import requests


BASE_URL = "http://efa.sta.bz.it/apb"


def _get(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Perform a GET request against the specified endpoint and return JSON."""
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def search_stop_or_address(query: str) -> Dict[str, Any]:
    """Search for stops or addresses that match the query string."""
    params = {"odvSugMacro": 1, "name_sf": query, "outputFormat": "JSON"}
    return _get("XML_STOPFINDER_REQUEST", params)


def search_connection(from_location: str, to_location: str, time: str | None = None) -> Dict[str, Any]:
    """Search for a connection between two locations.

    Args:
        from_location: Departure stop or address.
        to_location: Destination stop or address.
        time: Optional departure time.
    """
    params = {
        "name_origin": from_location,
        "type_origin": "any",
        "name_destination": to_location,
        "type_destination": "any",
        "odvMacro": "true",
        "calcNumberOfTrips": 1,
        "outputFormat": "JSON",
    }
    if time:
        params["itdTime"] = time
        params["itdTripDateTimeDepArr"] = "dep"
    return _get("XML_TRIP_REQUEST2", params)


def get_departures(stop_id: str, time: str | None = None) -> Dict[str, Any]:
    """Return departures for a specific stop ID at the given time."""
    params = {
        "language": "de",
        "type_dm": "stop",
        "name_dm": stop_id,
        "mode": "direct",
        "limit": 100,
        "outputFormat": "JSON",
    }
    if time:
        params["itdTime"] = time
    return _get("XML_DM_REQUEST", params)
