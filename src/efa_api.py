import os
from typing import Dict, Any, List, Optional
import requests

BASE_URL = os.environ.get("EFA_BASE_URL", "https://efa.sta.bz.it/apb")


def _get_best_stop_stateless(query: str) -> str:
    """Look up a stop via ``XML_STOPFINDER_REQUEST`` and return the stateless ID
    of the best matching result.

    The ``stateless`` value uniquely identifies the location within the Mentz
    backend and ensures that the subsequent trip request does not need to
    disambiguate the stop name again. If no suitable result can be determined,
    the original query string is returned as fall-back.
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

        if best and best.get("stateless"):
            return best["stateless"]
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
        from_stop = _get_best_stop_stateless(from_stop)
    to_stop = params.get("to_stop")
    if to_stop:
        to_stop = _get_best_stop_stateless(to_stop)

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

