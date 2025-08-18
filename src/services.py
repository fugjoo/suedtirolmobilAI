"""Service layer for transit queries."""
from typing import Any, Dict

import logging
import requests
from fastapi import HTTPException
from pydantic import BaseModel

from . import efa_api, parser, llm_parser, llm_formatter, request_logger


logger = logging.getLogger(__name__)


class SearchRequest(BaseModel):
    """Request body for search queries."""

    text: str


class DeparturesRequest(BaseModel):
    """Request body for departures queries."""

    stop: str
    limit: int = 10
    language: str = "de"


class StopsRequest(BaseModel):
    """Request body for stop suggestions."""

    query: str
    language: str = "de"


def search_service(body: SearchRequest, format: str = "json") -> Any:
    """Parse a text query and return EFA results.

    A departure monitor request is executed when no destination is provided.
    """
    logger.debug("search_service called with body=%s format=%s", body, format)
    q = parser.parse(body.text)
    if q.type != "trip" or not q.from_location or not q.to_location:
        try:
            q = llm_parser.parse_llm(body.text)
        except Exception as exc:  # pragma: no cover - no tests
            raise HTTPException(status_code=400, detail=str(exc))

    if not q.from_location:
        raise HTTPException(status_code=400, detail="origin not specified")

    if not q.to_location:
        sf_data = efa_api.stop_finder(q.from_location, language=q.language or "de")
        points = sf_data.get("stopFinder", {}).get("points", [])
        if not points:
            raise HTTPException(status_code=404, detail="stop not found")
        point = efa_api.best_point(points)
        if not point:
            raise HTTPException(status_code=404, detail="stop not found")
        verified = point.get("name", q.from_location)
        stateless = point.get("stateless")
        params = efa_api.build_departure_params(
            verified, 10, stateless=stateless, language=q.language or "de"
        )
        full_url = requests.Request(
            "GET",
            f"{efa_api.BASE_URL}/XML_DM_REQUEST",
            params=params,
        ).prepare().url
        request_logger.log_entry(
            {
                "input": body.text,
                "stop": point,
                "url": full_url,
            }
        )
        data = efa_api.departure_monitor(
            verified, 10, stateless=stateless, language=q.language or "de"
        )
        short_data = llm_formatter.extract_departure_info(data)
        try:
            text = llm_formatter.format_departures(data, language=q.language or "de")
            if format == "text":
                return text
            return {
                "input": body.text,
                "stop": point,
                "llmData": short_data,
                "data": text,
            }
        except Exception as exc:  # pragma: no cover - no tests
            raise HTTPException(status_code=500, detail=str(exc))

    from_data = efa_api.stop_finder(q.from_location, language=q.language or "de")
    points = from_data.get("stopFinder", {}).get("points", [])
    if not points:
        raise HTTPException(status_code=404, detail="origin not found")
    from_point = efa_api.best_point(points)
    if not from_point:
        raise HTTPException(status_code=404, detail="origin not found")
    q.from_location = from_point.get("name", q.from_location)
    from_stateless = from_point.get("stateless")
    from_type = from_point.get("anyType")

    to_data = efa_api.stop_finder(q.to_location, language=q.language or "de")
    points = to_data.get("stopFinder", {}).get("points", [])
    if not points:
        raise HTTPException(status_code=404, detail="destination not found")
    to_point = efa_api.best_point(points)
    if not to_point:
        raise HTTPException(status_code=404, detail="destination not found")
    q.to_location = to_point.get("name", q.to_location)
    to_stateless = to_point.get("stateless")
    to_type = to_point.get("anyType")

    params = efa_api.build_trip_params(
        q.from_location,
        q.to_location,
        q.datetime,
        origin_stateless=from_stateless,
        destination_stateless=to_stateless,
        origin_type=from_type,
        destination_type=to_type,
        bus=q.bus,
        zug=q.zug,
        seilbahn=q.seilbahn,
        long_distance=q.long_distance,
        datetime_mode=q.datetime_mode,
        last_connection=q.last_connection,
        language=q.language or "de",
    )
    full_url = requests.Request(
        "GET",
        f"{efa_api.BASE_URL}/XML_TRIP_REQUEST2",
        params=params,
    ).prepare().url
    request_logger.log_entry(
        {
            "input": body.text,
            "from": from_point,
            "to": to_point,
            "url": full_url,
        }
    )
    data: Dict[str, Any] = efa_api.trip_request(
        q.from_location,
        q.to_location,
        q.datetime,
        origin_stateless=from_stateless,
        destination_stateless=to_stateless,
        origin_type=from_type,
        destination_type=to_type,
        bus=q.bus,
        zug=q.zug,
        seilbahn=q.seilbahn,
        long_distance=q.long_distance,
        datetime_mode=q.datetime_mode,
        last_connection=q.last_connection,
        language=q.language or "de",
    )
    short_data = llm_formatter.extract_trip_info(data)
    try:
        text = llm_formatter.format_trip(data, language=q.language or "de")
        if format == "text":
            return text
        return {
            "input": body.text,
            "from": from_point,
            "to": to_point,
            "llmData": short_data,
            "data": text,
        }
    except Exception as exc:  # pragma: no cover - no tests
        raise HTTPException(status_code=500, detail=str(exc))


def departures_service(body: DeparturesRequest, format: str = "json") -> Any:
    """Return upcoming departures for a stop."""
    logger.debug(
        "departures_service called with body=%s format=%s", body, format
    )
    sf_data = efa_api.stop_finder(body.stop, language=body.language)
    points = sf_data.get("stopFinder", {}).get("points", [])
    if not points:
        raise HTTPException(status_code=404, detail="stop not found")
    point = efa_api.best_point(points)
    if not point:
        raise HTTPException(status_code=404, detail="stop not found")
    verified = point.get("name", body.stop)
    stateless = point.get("stateless")
    params = efa_api.build_departure_params(
        verified, body.limit, stateless=stateless, language=body.language
    )
    full_url = requests.Request(
        "GET",
        f"{efa_api.BASE_URL}/XML_DM_REQUEST",
        params=params,
    ).prepare().url
    request_logger.log_entry(
        {
            "input": body.stop,
            "stop": point,
            "url": full_url,
        }
    )
    data = efa_api.departure_monitor(
        verified, body.limit, stateless=stateless, language=body.language
    )
    short_data = llm_formatter.extract_departure_info(data)
    try:
        text = llm_formatter.format_departures(data, language=body.language)
        if format == "text":
            return text
        return {
            "input": body.stop,
            "stop": point,
            "llmData": short_data,
            "data": text,
        }
    except Exception as exc:  # pragma: no cover - no tests
        raise HTTPException(status_code=500, detail=str(exc))


def stops_service(body: StopsRequest, format: str = "json") -> Any:
    """Return stop name suggestions."""
    logger.debug("stops_service called with body=%s format=%s", body, format)
    params = {
        "name_sf": body.query,
        "odvSugMacro": "true",
        "outputFormat": "JSON",
        "language": body.language,
    }
    full_url = requests.Request(
        "GET",
        f"{efa_api.BASE_URL}/XML_STOPFINDER_REQUEST",
        params=params,
    ).prepare().url
    request_logger.log_entry(
        {
            "input": body.query,
            "url": full_url,
        }
    )
    data = efa_api.stop_finder(body.query, language=body.language)
    return data if format == "text" else {"data": data}

