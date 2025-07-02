import os
from typing import Dict, Any, List, Optional
import logging
import requests

from .logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()

BASE_URL = os.environ.get("EFA_BASE_URL", "https://efa.sta.bz.it/apb")


def get_stop_code(query: str) -> str:
    """Resolve a stop name to its stateless identifier using a StopFinder request.

    The returned code can be used directly in subsequent trip or departure
    requests. If the lookup fails, the original query string is returned
    unchanged.
    """
    url = f"{BASE_URL}/XML_STOPFINDER_REQUEST"
    params = {
        "odvSugMacro": "true",
        "name_sf": query,
        "outputFormat": "JSON",
        "locationServerActive": 1,
    }

    logger.debug("Requesting stop code for '%s'", query)
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        logger.debug("StopFinder response status: %s", response.status_code)
        data = response.json()
        stopfinder = data.get("stopFinder")
        if not isinstance(stopfinder, dict):
            stopfinder = {}
        points_data = stopfinder.get("points")
        if isinstance(points_data, dict):
            points = points_data.get("point", [])
        elif isinstance(points_data, list):
            points = points_data
        else:
            points = []
        if isinstance(points, dict):
            points = [points]

        logger.info("StopFinder results for '%s': %s", query, points)

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

        logger.debug("Stop suggestions: %s", points)
        logger.debug("Best match: %s", best)

        if best:
            if best.get("stateless"):
                logger.debug("Using stateless code: %s", best["stateless"])
                return best["stateless"]
            if best.get("name"):
                logger.debug("Using stop name: %s", best["name"])
                return best["name"]
    except Exception as exc:
        logger.warning("Stop code lookup failed for '%s': %s", query, exc)

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

    logger.info("Searching trip: %s", params)

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
        "locationServerActive": 1,
        "odvMacro": "true",
    }

    time = params.get("time")
    if time:
        efa_params["itdTime"] = time
    logger.debug("Trip request params: %s", efa_params)

    response = requests.get(url, params=efa_params, timeout=10)
    response.raise_for_status()
    logger.debug("Trip request status: %s", response.status_code)
    try:
        data = response.json()
        logger.debug("Trip response payload: %s", data)
        return data
    except ValueError:
        return {"text": response.text}


def dm_request(stop_name: str, limit: int = 10) -> Dict[str, Any]:
    """Query the departure monitor (DM) endpoint for a specific stop."""
    url = f"{BASE_URL}/XML_DM_REQUEST"
    logger.info("Requesting departures for '%s'", stop_name)
    stop_name = get_stop_code(stop_name)
    params = {
        "language": "de",
        "type_dm": "stop",
        "name_dm": stop_name,
        "mode": "direct",
        "limit": limit,
        "outputFormat": "JSON",
        "locationServerActive": 1,
        "odvMacro": "true",
    }

    logger.debug("DM request params: %s", params)
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    logger.debug("DM request status: %s", response.status_code)
    try:
        data = response.json()
        logger.debug("DM response payload: %s", data)
        return data
    except ValueError:
        return {"text": response.text}


def stopfinder_request(query: str) -> Dict[str, Any]:
    """Return stop suggestions for the given search string."""
    url = f"{BASE_URL}/XML_STOPFINDER_REQUEST"
    params = {
        "odvSugMacro": "true",
        "name_sf": query,
        "outputFormat": "JSON",
        "locationServerActive": 1,
    }
    logger.info("Stop finder for query '%s'", query)
    logger.debug("StopFinder params: %s", params)
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    logger.debug("StopFinder response: %s", data)
    return data

# Backwards compatibility
stop_finder = stopfinder_request

