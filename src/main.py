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
            "Extract the origin and destination from the user's travel "
            "request. Respond with a JSON object using the keys "
            "'origin', 'destination' and optional 'time' (HH:MM)."
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


def fetch_connections(
    origin: str, destination: str, time: Optional[str] = None
) -> Optional[dict]:
    """Fetch connection information from the EFA API."""
    try:
        params = {
            "outputFormat": "JSON",
            "type_origin": "any",
            "name_origin": origin,
            "type_destination": "any",
            "name_destination": destination,
        }
        if time:
            params["itdTime"] = time
        url = "https://efa.sta.bz.it/bin/query.exe/dn"
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logging.error("Failed to fetch connections: %s", exc)
        return None


def format_connections(data: dict) -> str:
    """Create a simple text representation of the returned connections."""
    if not data:
        return "No connections found."

    connections = (
        data.get("connections")
        or data.get("journeys")
        or data.get("trips")
        or []
    )

    lines = []
    for conn in connections:
        dep_stop = (
            conn.get("origin")
            if isinstance(conn.get("origin"), str)
            else conn.get("origin", {}).get("name")
        )
        dest_stop = (
            conn.get("destination")
            if isinstance(conn.get("destination"), str)
            else conn.get("destination", {}).get("name")
        )
        dep_time = (
            conn.get("departure", {}).get("time")
            if isinstance(conn.get("departure"), dict)
            else conn.get("departure")
        )
        arr_time = (
            conn.get("arrival", {}).get("time")
            if isinstance(conn.get("arrival"), dict)
            else conn.get("arrival")
        )
        line = f"{dep_time} {dep_stop} -> {dest_stop} {arr_time}".strip()
        lines.append(line)

    return "\n".join(lines) if lines else "No connections found."


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Query Suedtirolmobil via natural language"
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

    data = fetch_connections(origin, destination, time)
    if not data:
        print("Failed to retrieve connections.")
        sys.exit(1)

    print(format_connections(data))


if __name__ == "__main__":
    main()
