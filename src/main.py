import argparse
import json
import logging
import os
import sys
from typing import Optional

import openai
import requests

logging.basicConfig(level=logging.INFO)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


def extract_intent(text: str) -> Optional[dict]:
    """Use ChatGPT to extract origin, destination and optional time."""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.error("OPENAI_API_KEY not set")
            return None
        openai.api_key = api_key

        prompt = (
            "Extract origin and destination from the user's travel request. "
            "Return a JSON object with keys 'origin', 'destination' and "
            "optional 'time'."
        )
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ]
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0,
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as exc:
        logging.error("Failed to extract intent: %s", exc)
        return None


def fetch_schedule(
    origin: str, destination: str, time: Optional[str] = None
) -> Optional[dict]:
    """Fetch schedule information from the EFA API."""
    try:
        params = {
            "format": "json",
            "orig": origin,
            "dest": destination,
        }
        if time:
            params["time"] = time
        url = "https://efa.sta.bz.it/bin/query.exe/"
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logging.error("Failed to fetch schedule: %s", exc)
        return None


def format_schedule(data: dict) -> str:
    """Create a simple text representation of the schedule."""
    if not data:
        return "No schedule data available."

    lines = []
    for trip in data.get("trips", []):
        dep = trip.get("departure", "unknown")
        arr = trip.get("arrival", "unknown")
        lines.append(f"{dep} -> {arr}")

    return "\n".join(lines) if lines else "No trips found."


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query Suedtirolmobil schedule via natural language"
    )
    parser.add_argument(
        "query",
        nargs="+",
        help="Travel request in natural language",
    )
    args = parser.parse_args()

    text = " ".join(args.query)
    intent = extract_intent(text)
    if not intent:
        print("Could not understand the request.")
        sys.exit(1)

    origin = intent.get("origin")
    destination = intent.get("destination")
    time = intent.get("time")

    if not origin or not destination:
        print("Incomplete request. Need origin and destination.")
        sys.exit(1)

    data = fetch_schedule(origin, destination, time)
    if not data:
        print("Failed to retrieve schedule.")
        sys.exit(1)

    print(format_schedule(data))


if __name__ == "__main__":
    main()
