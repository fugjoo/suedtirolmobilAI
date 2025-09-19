"""Pydantic schemas for normalized responses coming from the EFA backend."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class StopLocation(BaseModel):
    """Normalized representation of a stop finder point."""

    id: str = Field(..., description="Stable identifier for the stop or location")
    gid: Optional[str] = Field(
        default=None, description="Global identifier provided by EFA when available"
    )
    name: str = Field(..., description="Human readable stop name")
    type: Literal["stop", "address", "poi"] = Field(..., description="Location type")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    match_score: int = Field(..., ge=0, le=100, description="0-100 fuzzy match score")
    is_best_match: bool = Field(
        default=False, description="True when the entry is the best match for the query"
    )
    products: List[str] = Field(
        default_factory=list, description="Transit products that serve this stop"
    )

    @field_validator("products", mode="before")
    @classmethod
    def _coerce_products(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return list(value)


class RealtimeInfo(BaseModel):
    """Realtime metadata for a departure/arrival."""

    is_realtime: bool = Field(
        default=False, description="Whether realtime data was present for the journey"
    )
    delay_seconds: int = Field(
        default=0, description="Delay in seconds (negative values indicate an early trip)"
    )
    source: Optional[str] = Field(default=None, description="Realtime provider identifier")
    updated_at: Optional[datetime] = Field(
        default=None, description="Timestamp of the realtime measurement"
    )


class Departure(BaseModel):
    """Normalized departure or arrival entry."""

    id: str = Field(..., description="Journey identifier")
    line: str = Field(..., description="Public short name of the line")
    direction: str = Field(..., description="Destination headsign")
    planned_time: datetime = Field(..., description="Scheduled departure time in ISO-8601")
    estimated_time: Optional[datetime] = Field(
        default=None, description="Realtime updated time when available"
    )
    platform: Optional[str] = Field(default=None, description="Platform or stand information")
    movement_type: Literal["departure", "arrival"] = Field(
        ..., description="Whether the entry represents a departure or arrival"
    )
    realtime: RealtimeInfo = Field(..., description="Realtime metadata for the entry")
    remarks: List[str] = Field(
        default_factory=list, description="Optional textual remarks accompanying the entry"
    )

    @field_validator("planned_time", "estimated_time", mode="before")
    @classmethod
    def _ensure_datetime(cls, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise TypeError("Datetime fields must be provided as ISO strings or datetimes")


class NormalizedError(BaseModel):
    """Normalized error structure derived from EFA error payloads."""

    code: str = Field(..., description="Underlying EFA error code")
    category: Literal["not_found", "unavailable", "invalid_request", "unknown"]
    message: str = Field(..., description="Human readable error message")
    details: Dict[str, Any] = Field(default_factory=dict)
