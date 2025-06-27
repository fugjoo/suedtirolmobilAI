"""Utilities for formatting API results for human consumption."""

from __future__ import annotations

from typing import Dict, List


def format_trip_results(data: Dict) -> str:
    """Convert raw trip data into a human-friendly string."""
    trips: List[str] = []
    for trip in data.get("trips", []):
        dep = trip.get("departure", "")
        arr = trip.get("arrival", "")
        line = trip.get("line", "")
        trips.append(f"{dep} -> {arr} via {line}")
    return "\n".join(trips) if trips else "Keine Verbindungen gefunden."
