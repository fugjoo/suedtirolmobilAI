"""Format EFA responses using OpenAI."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import openai

NO_RESULTS = {
    "de": (
        "Keine Ergebnisse gefunden. Vielleicht gab es ein Problem bei der Eingabe. "
        "Bitte versuche es mit einer anderen Formulierung."
    ),
    "it": (
        "Nessun risultato trovato. Potrebbe esserci stato un problema nell'inserimento. "
        "Prova con una nuova formulazione."
    ),
    "en": (
        "No results found. Something may have gone wrong with the input. "
        "Please try again with a different wording."
    ),
}

from .config import get_openai_model, get_openai_max_tokens

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "formatter_prompt.txt"


def load_prompt() -> str:
    """Return formatter prompt template."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def _extract_time(point: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Return planned and real time strings from a point."""

    if not isinstance(point, dict):
        return {"time": None, "rtTime": None}

    dt = point.get("dateTime", {})
    time = None
    rt_time = None
    if isinstance(dt, dict):
        hour = dt.get("time")
        if hour:
            time = hour
        rt_hour = dt.get("rtTime")
        if rt_hour:
            rt_time = rt_hour
    return {"time": time, "rtTime": rt_time}


def extract_trip_info(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return minimal information about a trip."""

    trips = data.get("trips")
    if isinstance(trips, dict):
        trip = trips.get("trip")
    elif isinstance(trips, list):
        trip = trips[0] if trips else None
    else:
        trip = None

    if not isinstance(trip, dict):
        return {}
    result: Dict[str, Any] = {
        "duration": trip.get("duration"),
        "interchange": trip.get("interchange"),
        "legs": [],
    }

    legs = trip.get("legs")
    if isinstance(legs, dict):
        legs = legs.get("leg", [])  # type: ignore[assignment]
    if not isinstance(legs, list):
        legs = []
    for leg in legs:
        points = leg.get("points", [])
        if isinstance(points, dict):
            points = points.get("point", [])  # type: ignore[assignment]

        if len(points) < 2:
            continue
        start = points[0]
        end = points[-1]
        mode = leg.get("mode", {})
        leg_info = {
            "line": mode.get("name"),
            "number": mode.get("number"),
            "direction": mode.get("destination"),
            "origin": start.get("name"),
            "destination": end.get("name"),
        }
        leg_info.update(_extract_time(start))
        arrival_times = _extract_time(end)
        leg_info["arrival"] = arrival_times.get("time")
        leg_info["rtArrival"] = arrival_times.get("rtTime")
        result["legs"].append(leg_info)
    return result


def extract_departure_info(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return minimal information about upcoming departures."""
    departures: List[Dict[str, Any]] = []

    dep_list = data.get("departureList")
    if isinstance(dep_list, dict):
        dep_list = dep_list.get("departure", [])
    if not isinstance(dep_list, list):
        dep_list = []
    for dep in dep_list:

        line = dep.get("servingLine", {})
        dt = dep.get("dateTime", {})
        rt = dep.get("realDateTime", {})
        time = None
        rt_time = None
        if dt:
            hour = dt.get("hour")
            minute = dt.get("minute")
            if hour is not None and minute is not None:
                time = f"{hour}:{minute.zfill(2)}" if isinstance(minute, str) else f"{hour}:{minute:02d}"
        if rt:
            hour = rt.get("hour")
            minute = rt.get("minute")
            if hour is not None and minute is not None:
                rt_time = f"{hour}:{minute.zfill(2)}" if isinstance(minute, str) else f"{hour}:{minute:02d}"
        departures.append(
            {
                "stop": dep.get("stopName"),
                "line": line.get("name"),
                "number": line.get("number"),
                "direction": line.get("direction"),
                "time": time,
                "rtTime": rt_time,
            }
        )
    return {"departures": departures}


def format_trip(
    data: Dict[str, Any],
    language: str = "de",
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """Return ChatGPT-formatted trip description.

    The ``OPENAI_MODEL`` environment variable is used when ``model`` is not
    provided.
    """
    if model is None:
        model = get_openai_model()
    if max_tokens is None:
        max_tokens = get_openai_max_tokens()

    short_data = extract_trip_info(data)
    if not short_data:
        return NO_RESULTS.get(language, NO_RESULTS["de"])

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    prompt = load_prompt().format(data=json.dumps(short_data, ensure_ascii=False), language=language)

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def format_departures(
    data: Dict[str, Any],
    language: str = "de",
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """Return ChatGPT-formatted departure list.

    The ``OPENAI_MODEL`` environment variable is used when ``model`` is not
    provided.
    """
    if model is None:
        model = get_openai_model()
    if max_tokens is None:
        max_tokens = get_openai_max_tokens()

    short_data = extract_departure_info(data)
    if not short_data.get("departures"):
        return NO_RESULTS.get(language, NO_RESULTS["de"])

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    prompt = load_prompt().format(data=json.dumps(short_data, ensure_ascii=False), language=language)


    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()
