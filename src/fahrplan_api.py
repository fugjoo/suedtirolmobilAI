"""Wrappers around the existing Fahrplan API endpoints."""

from typing import Any, Dict


def search_stop_or_address(query: str) -> Dict[str, Any]:
    """Search for stops or addresses that match the query string.

    This function should call your real API and return the parsed JSON
    response. Here it returns a placeholder structure.
    """
    # TODO: Replace with real API call
    return {"type": "stop_search", "query": query}


def search_connection(from_location: str, to_location: str, time: str | None = None) -> Dict[str, Any]:
    """Search for a connection between two locations.

    Args:
        from_location: Departure stop or address.
        to_location: Destination stop or address.
        time: Optional departure time.
    """
    # TODO: Replace with real API call
    return {
        "type": "connection_search",
        "from": from_location,
        "to": to_location,
        "time": time,
    }


def get_departures(stop_id: str, time: str | None = None) -> Dict[str, Any]:
    """Return departures for a specific stop ID at the given time."""
    # TODO: Replace with real API call
    return {"type": "departure_board", "stop_id": stop_id, "time": time}
