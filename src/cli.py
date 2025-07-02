import argparse
import logging

from . import nlp_parser, efa_api
from .logging_utils import setup_logging

logger = logging.getLogger(__name__)


def _plural(word: str, count: int) -> str:
    """Return pluralized word depending on count."""
    return word if count == 1 else f"{word}s"


def _format_search_result(result: dict) -> str:
    """Return a readable summary of a trip search result."""
    if not isinstance(result, dict):
        return str(result)

    from_stop = (
        result.get("from_stop")
        or result.get("origin", {}).get("name")
        or ""
    )
    to_stop = (
        result.get("to_stop")
        or result.get("destination", {}).get("name")
        or ""
    )

    trips = result.get("trips")
    count = 0
    if isinstance(trips, list):
        count = len(trips)
    elif isinstance(trips, dict):
        trip_data = trips.get("trip")
        if isinstance(trip_data, list):
            count = len(trip_data)
        elif trip_data:
            count = 1
        else:
            count = len(trips)

    if not from_stop and not to_stop:
        return f"{count} {_plural('trip', count)} found."
    if not from_stop:
        return f"{count} {_plural('trip', count)} to {to_stop}."
    if not to_stop:
        return f"{count} {_plural('trip', count)} from {from_stop}."
    return f"{count} {_plural('trip', count)} from {from_stop} to {to_stop}."


def _format_departures_result(result: dict) -> str:
    """Return a readable summary of departures."""
    if not isinstance(result, dict):
        return str(result)

    stop_name = (
        result.get("stop_name")
        or result.get("stopName")
        or result.get("stop", {}).get("name")
        or result.get("name")
        or ""
    )

    departures = (
        result.get("departures")
        or result.get("departureList")
        or result.get("stopEvents")
    )
    count = 0
    if isinstance(departures, list):
        count = len(departures)
    elif departures:
        count = 1

    suffix = f" for '{stop_name}'" if stop_name else ""
    return f"{count} {_plural('departure', count)}{suffix}."


def _format_stops_result(result: dict) -> str:
    """Return a readable summary of stop suggestions."""
    if not isinstance(result, dict):
        return str(result)

    points = (
        result.get("stopFinder", {}).get("points", {}).get("point")
        or result.get("stops")
    )
    names = []
    count = 0
    if isinstance(points, list):
        count = len(points)
        for p in points:
            if isinstance(p, dict) and p.get("name"):
                names.append(p["name"])
    elif isinstance(points, dict):
        count = 1
        if points.get("name"):
            names.append(points["name"])

    if names:
        shown = ", ".join(names[:3])
        if len(names) > 3:
            shown += " ..."
        return f"{count} {_plural('stop', count)} found: {shown}"
    return f"{count} {_plural('stop', count)} found."


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
    print(_format_search_result(response))


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
    print(_format_departures_result(result))


def run_stop_finder(query: str) -> None:
    logger.info("Searching stops...")
    try:
        result = efa_api.stopfinder_request(query)
    except Exception as exc:
        logger.error("Error during request: %s", exc)
        return
    print(_format_stops_result(result))


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
