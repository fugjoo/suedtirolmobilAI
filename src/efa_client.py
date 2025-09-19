"""Client utilities for interacting with the Südtirolmobil EFA backend."""
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "EfaClient",
    "EfaError",
    "EfaHttpError",
    "EfaApiError",
    "StopFinderCandidate",
    "StopFinderResponse",
    "DepartureBoard",
    "DepartureQuery",
    "DepartureEvent",
    "TransportInfo",
    "TripPlan",
    "TripJourney",
    "TripLeg",
    "TripLegStop",
    "TripStep",
    "TripEndpoint",
]

logger = logging.getLogger(__name__)

SERVICE_URL = "https://efa.sta.bz.it/apb"
DEFAULT_LANGUAGE = "en"
COORD_FORMAT = "WGS84[DD.DDDDD]"
SERVICE_TIMEZONE = ZoneInfo("Europe/Rome")


class EfaError(RuntimeError):
    """Base class for EFA related failures."""


class EfaHttpError(EfaError):
    """Raised when the HTTP transport fails."""


class EfaApiError(EfaError):
    """Raised when the backend signals an error."""

    def __init__(self, message: str, *, messages: Sequence[SystemMessage] | None = None) -> None:
        super().__init__(message)
        self.messages = tuple(messages or ())


class BaseSchema(BaseModel):
    """Common configuration for response models."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class SystemMessage(BaseSchema):
    """Represents a system message emitted by the backend."""

    type: str | None = None
    module: str | None = None
    code: int | None = None
    text: str | None = None
    sub_type: str | None = Field(default=None, alias="subType")


class LocationSummary(BaseSchema):
    """Compact representation of a location returned by the API."""

    id: str | None = None
    name: str | None = None
    type: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    locality: str | None = None
    stop_id: str | None = None
    platform: str | None = None
    properties: dict[str, Any] | None = None


class StopFinderCandidate(LocationSummary):
    """Stop finder result entry."""

    match_quality: int | None = Field(default=None, alias="matchQuality")
    is_best: bool | None = Field(default=None, alias="isBest")
    product_classes: list[int] | None = Field(default=None, alias="productClasses")


class TransportProduct(BaseSchema):
    id: int | None = None
    class_id: int | None = Field(default=None, alias="class")
    name: str | None = None
    icon_id: int | None = Field(default=None, alias="iconId")


class TransportOperator(BaseSchema):
    id: str | None = None
    code: str | None = None
    name: str | None = None


class TransportReference(BaseSchema):
    id: str | None = None
    name: str | None = None
    type: str | None = None


class TransportInfo(BaseSchema):
    id: str | None = None
    name: str | None = None
    short_name: str | None = Field(default=None, alias="shortName")
    number: str | None = None
    description: str | None = None
    product: TransportProduct | None = None
    operator: TransportOperator | None = None
    origin: TransportReference | None = None
    destination: TransportReference | None = None
    properties: dict[str, Any] | None = None


class StopEventNotice(BaseSchema):
    id: str | None = None
    type: str | None = None
    priority: str | None = None
    text: str | None = None
    url: str | None = None


class DepartureEvent(BaseSchema):
    """Normalized departure monitor event."""

    stop: LocationSummary
    planned_time: datetime
    estimated_time: datetime | None = None
    delay_minutes: float | None = None
    realtime_status: str | None = None
    is_realtime_controlled: bool | None = None
    transportation: TransportInfo
    notices: list[StopEventNotice] | None = None
    properties: dict[str, Any] | None = None


class DepartureQuery(BaseSchema):
    stop_id: str
    date: str
    time: str
    limit: int | None = None
    include_realtime: bool = True


class DepartureBoard(BaseSchema):
    stop: LocationSummary
    query: DepartureQuery
    events: list[DepartureEvent]
    messages: list[SystemMessage]


class StopFinderResponse(BaseSchema):
    query: str
    results: list[StopFinderCandidate]
    messages: list[SystemMessage]


class TripLegStop(LocationSummary):
    arrival_planned: datetime | None = None
    arrival_estimated: datetime | None = None
    departure_planned: datetime | None = None
    departure_estimated: datetime | None = None
    sequence_index: int | None = None


class TripStep(BaseSchema):
    description: str | None = None
    turn_direction: str | None = Field(default=None, alias="turnDirection")
    maneuver: str | None = None
    distance_meters: float | None = Field(default=None, alias="distance")
    cumulative_distance_meters: float | None = Field(default=None, alias="cumDistance")
    duration_seconds: int | None = Field(default=None, alias="duration")
    cumulative_duration_seconds: int | None = Field(default=None, alias="cumDuration")


class TripLeg(BaseSchema):
    mode: str | None = None
    duration_seconds: int | None = Field(default=None, alias="duration")
    transportation: TransportInfo | None = None
    origin: LocationSummary | None = None
    destination: LocationSummary | None = None
    stops: list[TripLegStop] | None = None
    steps: list[TripStep] | None = None
    infos: list[StopEventNotice] | None = None
    path: list[tuple[float, float]] | None = None
    properties: dict[str, Any] | None = None


class FareOption(BaseSchema):
    id: str | None = None
    name: str | None = None
    price: float | None = Field(default=None, alias="priceBrutto")
    currency: str | None = None
    person: str | None = None
    traveller_class: str | None = Field(default=None, alias="travellerClass")
    time_validity: str | None = Field(default=None, alias="timeValidity")
    valid_minutes: int | None = Field(default=None, alias="validMinutes")
    from_leg: int | None = Field(default=None, alias="fromLeg")
    to_leg: int | None = Field(default=None, alias="toLeg")
    properties: dict[str, Any] | None = None


class TripJourney(BaseSchema):
    rating: int | None = None
    is_additional: bool | None = Field(default=None, alias="isAdditional")
    interchanges: int | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration_seconds: float | None = None
    legs: list[TripLeg]
    fares: list[FareOption] | None = None
    days_of_service: list[str] | dict[str, Any] | None = Field(default=None, alias="daysOfService")


class TripPlan(BaseSchema):
    query_time: datetime
    arrive_by: bool
    query_origin: TripEndpoint
    query_destination: TripEndpoint
    query_via: TripEndpoint | None = None
    journeys: list[TripJourney]
    messages: list[SystemMessage]


class TripEndpoint(BaseSchema):
    """Endpoint specification for trip planning requests."""

    stop_id: str = Field(..., description="Stop identifier as returned by stop.find.")
    type: str = Field(default="stopID", description="EFA type for the endpoint.")
    label: str | None = Field(default=None, description="Optional human readable label.")


@dataclass(slots=True)
class CacheEntry:
    value: Any
    expires_at: float

    def is_valid(self) -> bool:
        return time.monotonic() < self.expires_at


class EfaClient:
    """Async client with caching, throttling and response normalization."""

    def __init__(
        self,
        *,
        base_url: str = SERVICE_URL,
        language: str = DEFAULT_LANGUAGE,
        coord_format: str = COORD_FORMAT,
        request_timeout: float = 15.0,
        min_interval: float = 0.2,
        max_connections: int = 4,
        stop_cache_ttl: float = 30.0,
        dm_cache_ttl: float = 10.0,
        trip_cache_ttl: float = 15.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.language = language
        self.coord_format = coord_format
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=request_timeout)
        self._cache: dict[tuple[str, tuple[tuple[str, str], ...]], CacheEntry] = {}
        self._cache_lock = asyncio.Lock()
        self._rate_lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(max_connections)
        self._min_interval = min_interval
        self._last_request = 0.0
        self._stop_cache_ttl = stop_cache_ttl
        self._dm_cache_ttl = dm_cache_ttl
        self._trip_cache_ttl = trip_cache_ttl

    async def __aenter__(self) -> "EfaClient":
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def stop_finder(
        self,
        query: str,
        *,
        limit: int | None = None,
        location_types: Sequence[str] | None = None,
        best_only: bool = False,
    ) -> StopFinderResponse:
        params = {
            "language": self.language,
            "outputFormat": "rapidJSON",
            "coordOutputFormat": self.coord_format,
            "SpEncId": "0",
            "odvSugMacro": "true",
            "name_sf": query,
        }
        payload = await self._request(
            "XML_STOPFINDER_REQUEST",
            params,
            cache_ttl=self._stop_cache_ttl,
        )
        messages = self._extract_messages(payload)
        candidates = [self._build_stop_candidate(entry) for entry in payload.get("locations", [])]
        if location_types:
            allowed = {value.lower() for value in location_types}
            candidates = [c for c in candidates if c.type and c.type.lower() in allowed]
        if best_only:
            candidates = [c for c in candidates if c.is_best]
        if limit is not None:
            candidates = candidates[:limit]
        if not candidates and any(msg.type == "error" for msg in messages):
            raise EfaApiError("No stop finder results", messages=messages)
        return StopFinderResponse(query=query, results=candidates, messages=messages)

    async def departures(
        self,
        stop_id: str,
        *,
        when: datetime | None = None,
        limit: int | None = 10,
        include_realtime: bool = True,
    ) -> DepartureBoard:
        service_time = self._to_service_time(when)
        params = {
            "language": self.language,
            "outputFormat": "rapidJSON",
            "coordOutputFormat": self.coord_format,
            "SpEncId": "0",
            "locationServerActive": "1",
            "stateless": "1",
            "mode": "direct",
            "type_dm": "stopID",
            "name_dm": stop_id,
            "useAllStops": "1",
            "useRealtime": include_realtime,
            "itdDate": service_time.strftime("%Y%m%d"),
            "itdTime": service_time.strftime("%H:%M"),
            "limit": limit,
            "itdLPxx_depOnly": "1",
        }
        payload = await self._request("XML_DM_REQUEST", params, cache_ttl=self._dm_cache_ttl)
        messages = self._extract_messages(payload)
        events = [self._build_departure_event(event) for event in payload.get("stopEvents", [])]
        if limit is not None:
            events = events[:limit]
        locations = payload.get("locations", [])
        stop_summary = self._build_location(locations[0]) if locations else LocationSummary(stop_id=stop_id)
        if not events and any(msg.type == "error" for msg in messages):
            raise EfaApiError("No departures returned", messages=messages)
        query = DepartureQuery(
            stop_id=stop_id,
            date=service_time.strftime("%Y-%m-%d"),
            time=service_time.strftime("%H:%M"),
            limit=limit,
            include_realtime=include_realtime,
        )
        return DepartureBoard(stop=stop_summary, query=query, events=events, messages=messages)

    async def plan_trip(
        self,
        origin: TripEndpoint,
        destination: TripEndpoint,
        *,
        via: TripEndpoint | None = None,
        departure_time: datetime | None = None,
        arrive_by: bool = False,
        max_trips: int = 5,
        include_realtime: bool = True,
    ) -> TripPlan:
        service_time = self._to_service_time(departure_time)
        params = {
            "language": self.language,
            "outputFormat": "rapidJSON",
            "coordOutputFormat": self.coord_format,
            "SpEncId": "0",
            "locationServerActive": "1",
            "stateless": "1",
            "type_origin": origin.type,
            "name_origin": origin.stop_id,
            "type_destination": destination.type,
            "name_destination": destination.stop_id,
            "itdDate": service_time.strftime("%Y%m%d"),
            "itdTime": service_time.strftime("%H:%M"),
            "itdTripDateTimeDepArr": "arr" if arrive_by else "dep",
            "calcNumberOfTrips": max_trips,
            "useRealtime": include_realtime,
            "itOptionsActive": "1",
            "ptOptionsActive": "1",
        }
        if via is not None:
            params.update({
                "type_via": via.type,
                "name_via": via.stop_id,
            })
        payload = await self._request("XML_TRIP_REQUEST2", params, cache_ttl=self._trip_cache_ttl)
        messages = self._extract_messages(payload)
        journeys = [self._build_journey(entry) for entry in payload.get("journeys", [])]
        if not journeys and any(msg.type == "error" for msg in messages):
            raise EfaApiError("Trip planning failed", messages=messages)
        return TripPlan(
            query_time=datetime.now(timezone.utc),
            arrive_by=arrive_by,
            query_origin=origin,
            query_destination=destination,
            query_via=via,
            journeys=journeys,
            messages=messages,
        )

    async def _request(
        self,
        endpoint: str,
        params: dict[str, Any],
        *,
        cache_ttl: float | None = None,
    ) -> dict[str, Any]:
        cleaned = self._prepare_params(params)
        cache_key = (endpoint, tuple(sorted(cleaned.items())))
        if cache_ttl:
            async with self._cache_lock:
                entry = self._cache.get(cache_key)
                if entry and entry.is_valid():
                    return entry.value
                if entry and not entry.is_valid():
                    self._cache.pop(cache_key, None)
        async with self._semaphore:
            await self._throttle()
            try:
                response = await self._client.get(endpoint, params=cleaned)
            except httpx.RequestError as exc:
                raise EfaHttpError(f"Failed to reach EFA backend: {exc}") from exc
        if response.status_code >= 500:
            raise EfaHttpError(f"EFA backend returned {response.status_code}")
        if response.status_code >= 400:
            raise EfaApiError(f"EFA request rejected with HTTP {response.status_code}")
        try:
            payload = response.json()
        except ValueError as exc:  # pragma: no cover - defensive
            raise EfaApiError("Failed to decode EFA response") from exc
        if cache_ttl:
            async with self._cache_lock:
                self._cache[cache_key] = CacheEntry(payload, time.monotonic() + cache_ttl)
        return payload

    async def _throttle(self) -> None:
        async with self._rate_lock:
            if self._min_interval <= 0:
                self._last_request = time.monotonic()
                return
            now = time.monotonic()
            elapsed = now - self._last_request
            if elapsed < self._min_interval:
                await asyncio.sleep(self._min_interval - elapsed)
            self._last_request = time.monotonic()

    def _prepare_params(self, params: dict[str, Any]) -> dict[str, str]:
        prepared: dict[str, str] = {}
        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, bool):
                prepared[key] = "1" if value else "0"
            elif isinstance(value, (list, tuple, set)):
                prepared[key] = ",".join(str(item) for item in value if item is not None)
            else:
                prepared[key] = str(value)
        return prepared

    def _extract_messages(self, payload: dict[str, Any]) -> list[SystemMessage]:
        messages = []
        for entry in payload.get("systemMessages", []) or []:
            messages.append(SystemMessage(**entry))
        return messages

    def _build_stop_candidate(self, entry: dict[str, Any]) -> StopFinderCandidate:
        location = self._build_location(entry)
        base = StopFinderCandidate(**entry)
        return base.model_copy(update=location.model_dump(exclude_none=True))

    def _build_location(self, entry: dict[str, Any]) -> LocationSummary:
        coord = entry.get("coord") or []
        latitude = coord[0] if len(coord) > 0 else None
        longitude = coord[1] if len(coord) > 1 else None
        parent = entry.get("parent") or {}
        locality = parent.get("name") if parent.get("type") == "locality" else parent.get("name") if parent.get("type") == "municipality" else None
        properties = entry.get("properties") or {}
        stop_id = properties.get("stopId") if isinstance(properties, dict) else None
        platform = properties.get("platform") if isinstance(properties, dict) else None
        return LocationSummary(
            id=entry.get("id"),
            name=entry.get("name"),
            type=entry.get("type"),
            latitude=latitude,
            longitude=longitude,
            locality=locality,
            stop_id=stop_id,
            platform=platform,
            properties=properties if isinstance(properties, dict) else None,
        )

    def _build_departure_event(self, entry: dict[str, Any]) -> DepartureEvent:
        location = self._build_location(entry.get("location", {}))
        transport = self._build_transport(entry.get("transportation", {}))
        planned = self._parse_time(entry.get("departureTimePlanned"))
        estimated = self._parse_time(entry.get("departureTimeEstimated"))
        delay_minutes: float | None = None
        if planned and estimated:
            delay_minutes = (estimated - planned).total_seconds() / 60.0
        notices = [self._build_notice(info) for info in entry.get("infos", [])] if entry.get("infos") else None
        status = entry.get("realtimeStatus")
        if isinstance(status, (list, tuple, set)):
            status = ", ".join(str(item) for item in status if item is not None)
        is_controlled = entry.get("isRealtimeControlled")
        if isinstance(is_controlled, str):
            is_controlled = is_controlled.lower() == "true"
        return DepartureEvent(
            stop=location,
            planned_time=planned or datetime.now(timezone.utc),
            estimated_time=estimated,
            delay_minutes=delay_minutes,
            realtime_status=status,
            is_realtime_controlled=is_controlled,
            transportation=transport,
            notices=notices,
            properties=entry.get("properties"),
        )

    def _build_transport(self, entry: dict[str, Any]) -> TransportInfo:
        product = TransportProduct(**entry.get("product", {})) if entry.get("product") else None
        operator = TransportOperator(**entry.get("operator", {})) if entry.get("operator") else None
        origin = TransportReference(**entry.get("origin", {})) if entry.get("origin") else None
        destination = TransportReference(**entry.get("destination", {})) if entry.get("destination") else None
        return TransportInfo(
            id=entry.get("id"),
            name=entry.get("name"),
            short_name=entry.get("disassembledName"),
            number=entry.get("number"),
            description=entry.get("description"),
            product=product,
            operator=operator,
            origin=origin,
            destination=destination,
            properties=entry.get("properties"),
        )

    def _build_notice(self, entry: dict[str, Any]) -> StopEventNotice:
        url = None
        if entry.get("infoLinks"):
            first = entry["infoLinks"][0]
            url = first.get("url")
        return StopEventNotice(
            id=entry.get("id"),
            type=entry.get("type"),
            priority=entry.get("priority"),
            text=entry.get("text") or entry.get("name"),
            url=url,
        )

    def _build_journey(self, entry: dict[str, Any]) -> TripJourney:
        legs_data = entry.get("legs", [])
        legs = [self._build_leg(leg) for leg in legs_data]
        start_time = self._extract_leg_start(legs_data[0]) if legs_data else None
        end_time = self._extract_leg_end(legs_data[-1]) if legs_data else None
        duration_seconds = None
        if start_time and end_time:
            duration_seconds = (end_time - start_time).total_seconds()
        fares = [FareOption(**ticket) for ticket in entry.get("fare", {}).get("tickets", [])] if entry.get("fare") else None
        return TripJourney(
            rating=entry.get("rating"),
            is_additional=entry.get("isAdditional"),
            interchanges=entry.get("interchanges"),
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            legs=legs,
            fares=fares,
            days_of_service=entry.get("daysOfService"),
        )

    def _build_leg(self, entry: dict[str, Any]) -> TripLeg:
        transport = self._build_transport(entry.get("transportation", {})) if entry.get("transportation") else None
        stops = [
            TripLegStop(
                **self._build_location(stop).model_dump(),
                arrival_planned=self._parse_time(stop.get("arrivalTimePlanned")),
                arrival_estimated=self._parse_time(stop.get("arrivalTimeEstimated")),
                departure_planned=self._parse_time(stop.get("departureTimePlanned")),
                departure_estimated=self._parse_time(stop.get("departureTimeEstimated")),
                sequence_index=index,
            )
            for index, stop in enumerate(entry.get("stopSequence", []))
        ]
        steps = [TripStep(**step) for step in entry.get("pathDescriptions", [])] if entry.get("pathDescriptions") else None
        notices = [self._build_notice(info) for info in entry.get("infos", [])] if entry.get("infos") else None
        path_coords = None
        if entry.get("coords"):
            path_coords = [tuple(coord) for coord in entry["coords"] if isinstance(coord, (list, tuple)) and len(coord) >= 2]
        origin = self._build_location(entry.get("origin", {})) if entry.get("origin") else None
        destination = self._build_location(entry.get("destination", {})) if entry.get("destination") else None
        mode = None
        if transport and transport.product:
            mode = transport.product.name
        return TripLeg(
            mode=mode,
            duration_seconds=entry.get("duration"),
            transportation=transport,
            origin=origin,
            destination=destination,
            stops=stops or None,
            steps=steps,
            infos=notices,
            path=path_coords,
            properties=entry.get("properties") or entry.get("footPathInfo"),
        )

    def _extract_leg_start(self, leg: dict[str, Any]) -> datetime | None:
        origin = leg.get("origin", {})
        return (
            self._parse_time(origin.get("departureTimeEstimated"))
            or self._parse_time(origin.get("departureTimePlanned"))
        )

    def _extract_leg_end(self, leg: dict[str, Any]) -> datetime | None:
        destination = leg.get("destination", {})
        return (
            self._parse_time(destination.get("arrivalTimeEstimated"))
            or self._parse_time(destination.get("arrivalTimePlanned"))
        )

    def _parse_time(self, value: Any) -> datetime | None:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                logger.debug("Unable to parse datetime value: %s", value)
                return None
        return None

    def _to_service_time(self, when: datetime | None) -> datetime:
        if when is None:
            return datetime.now(SERVICE_TIMEZONE)
        if when.tzinfo is None:
            return when.replace(tzinfo=SERVICE_TIMEZONE)
        return when.astimezone(SERVICE_TIMEZONE)
