"""Wrapper functions for interacting with the EFA XML API."""

from __future__ import annotations

import logging
from typing import Any, Dict

import requests

from . import config

logger = logging.getLogger(__name__)


def stopfinder(query: str) -> Dict[str, Any]:
    """Call the StopFinder API to resolve a location name to a stop ID."""
    params = {
        "odvSugMacro": 1,
        "name_sf": query,
        "outputFormat": "json",
    }
    logger.debug("StopFinder params: %s", params)
    response = requests.get(config.STOPFINDER_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def trip_request(origin_id: str, destination_id: str, date: str, time: str) -> Dict[str, Any]:
    """Call the TripRequest API to search for a connection."""
    params = {
        "name_origin": origin_id,
        "name_destination": destination_id,
        "itdDate": date,
        "itdTime": time,
        "outputFormat": "json",
    }
    logger.debug("TripRequest params: %s", params)
    response = requests.get(config.TRIP_REQUEST_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
