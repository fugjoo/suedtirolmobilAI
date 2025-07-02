import argparse
import logging

from . import nlp_parser, efa_api
from .logging_utils import setup_logging
from .summaries import (
    format_search_result,
    format_departures_result,
    format_stops_result,
)

logger = logging.getLogger(__name__)


def run_search(query: str) -> None:
    """Run a search for the given natural language query with progress output."""
    logger.info("Searching for stops...")
    params = nlp_parser.parse_query(query)

    if not params:
        logger.warning("No parameters extracted from the query.")
        return

    logger.info("Determining results...")
    try:
        response = efa_api.search_efa(params)
    except Exception as exc:
        logger.error("Error during search: %s", exc)
        return

    logger.info("Interpreting results...")
    if isinstance(response, dict) and "trips" in response:
        trips = response.get("trips") or []
        logger.info("Found %d trips.", len(trips))
    else:
        logger.info("No trip data found.")

    logger.info("Returning search results...")
    print(format_search_result(response))


def run_departures(stop: str) -> None:
    """Query the departure monitor and show progress messages."""
    logger.info("Haltestelle '%s' wird ermittelt...", stop)
    try:
        result = efa_api.dm_request(stop)
    except Exception as exc:
        logger.error("Fehler bei der Abfrage: %s", exc)
        return

    logger.info("Suche wird gestartet...")
    logger.info("Ergebnisse gefunden.")
    print(format_departures_result(result))


def run_stop_finder(query: str) -> None:
    logger.info("Searching stops...")
    try:
        result = efa_api.stopfinder_request(query)
    except Exception as exc:
        logger.error("Error during request: %s", exc)
        return
    print(format_stops_result(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="suedtirolmobilAI CLI")
    parser.add_argument("command", choices=["search", "departures", "stops"], help="Command to execute")
    parser.add_argument("text", nargs="+", help="Query text or stop name")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()
    setup_logging(args.debug)

    argument = " ".join(args.text)
    if args.command == "search":
        run_search(argument)
    elif args.command == "departures":
        run_departures(argument)
    elif args.command == "stops":
        run_stop_finder(argument)
