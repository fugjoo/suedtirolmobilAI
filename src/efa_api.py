import os
from typing import Dict, Any, List, Optional
import requests

BASE_URL = os.environ.get("EFA_BASE_URL", "https://efa.sta.bz.it/apb")


def get_stop_code(query: str) -> str:
    """Resolve a stop name to its stateless identifier using a StopFinder request.

    The returned code can be used directly in subsequent trip or departure
    requests. If the lookup fails, the original query string is returned
    unchanged.
    """
    url = f"{BASE_URL}/XML_STOPFINDER_REQUEST"
    params = {
        "odvSugMacro": 1,
        "name_sf": query,
        "outputFormat": "JSON",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        points: List[Dict[str, Any]] = (
            data.get("stopFinder", {})
            .get("points", {})
            .get("point", [])
        )
        if isinstance(points, dict):
            points = [points]

        best: Optional[Dict[str, Any]] = None
        best_quality = -1
        for p in points:
            try:
                quality = int(p.get("quality", 0))
            except (TypeError, ValueError):
                quality = 0
            if quality > best_quality:
                best_quality = quality
                best = p

        if best:
            if best.get("stateless"):
                return best["stateless"]
            if best.get("name"):
                return best["name"]
    except Exception:
        pass

    return query


def search_efa(params: Dict[str, Any]) -> Dict[str, Any]:
    """Send a GET request to the Mentz-EFA API.

    Parameters
    ----------
    params: dict
        Query parameters for the EFA request.

    Returns
    -------
    dict
        JSON response from the API.
    """
    url = f"{BASE_URL}/XML_TRIP_REQUEST2"

    from_stop = params.get("from_stop")
    if from_stop:
        from_stop = get_stop_code(from_stop)
    to_stop = params.get("to_stop")
    if to_stop:
        to_stop = get_stop_code(to_stop)

    efa_params = {
        "name_origin": from_stop,
        "type_origin": "any",
        "name_destination": to_stop,
        "type_destination": "any",
        "outputFormat": "JSON",
        "calcNumberOfTrips": 1,
    }

    time = params.get("time")
    if time:
        efa_params["itdTime"] = time

    response = requests.get(url, params=efa_params, timeout=10)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


def dm_request(stop_name: str, limit: int = 10) -> Dict[str, Any]:
    """Query the departure monitor (DM) endpoint for a specific stop."""
    url = f"{BASE_URL}/XML_DM_REQUEST"
    stop_name = get_stop_code(stop_name)
    params = {
        "language": "de",
        "type_dm": "stop",
        "name_dm": stop_name,
        "mode": "direct",
        "limit": limit,
        "outputFormat": "JSON",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        return {"text": response.text}


def stop_finder(query: str) -> Dict[str, Any]:
    """Return stop suggestions for the given search string."""
    url = f"{BASE_URL}/XML_STOPFINDER_REQUEST"
    params = {"odvSugMacro": 1, "name_sf": query, "outputFormat": "JSON"}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

