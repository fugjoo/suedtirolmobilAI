"""Command line interface entry point."""

from __future__ import annotations

import logging
from datetime import datetime

from . import efa_api, formatter, nlp_parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Simple command line interaction."""
    query = input("Frage: ")
    parsed = nlp_parser.parse_user_input(query)
    logger.debug("Parsed input: %s", parsed)
    start = parsed.get("start")
    ziel = parsed.get("ziel")
    date = parsed.get("datum", datetime.now().strftime("%d.%m.%Y"))
    time = parsed.get("uhrzeit", datetime.now().strftime("%H:%M"))

    start_data = efa_api.stopfinder(start)
    ziel_data = efa_api.stopfinder(ziel)

    try:
        start_id = start_data["stopFinder"]["points"][0]["ref"]
        ziel_id = ziel_data["stopFinder"]["points"][0]["ref"]
    except (KeyError, IndexError):
        print("Konnte Haltestellen nicht finden.")
        return

    trip_data = efa_api.trip_request(start_id, ziel_id, date, time)
    print(formatter.format_trip_results(trip_data))


if __name__ == "__main__":
    main()
