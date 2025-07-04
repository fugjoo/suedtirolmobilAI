"""Command line interface for querying the public transport API."""

import argparse
import logging

from . import nlp_parser, efa_api, chatgpt_helper
from .logging_utils import setup_logging
from .summaries import (
    format_search_result,
    format_departures_result,
    format_stops_result,
)

logger = logging.getLogger(__name__)


def run_search(query: str, output_format: str = "legs", debug: bool = False, use_chatgpt: bool = False) -> None:
    """Run a search for the given natural language query.

    Parameters
    ----------
    query: str
        Natural language query describing the trip request.
    output_format: str, optional
        ``"legs"`` prints only the individual trip legs,
        ``"text"`` shows a longer summary,
        ``"json"`` dumps the raw API response.
    use_chatgpt: bool, optional
        If set, the plain-text summary is reformatted via the OpenAI API.
    """
    logger.info("Searching for stops...")
    params = {}
    if use_chatgpt:
        try:
            params = chatgpt_helper.parse_query_chatgpt(query)
        except Exception as exc:
            logger.error("ChatGPT parsing failed: %s", exc)
            params = {}

    if not params:
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
    if output_format == "json" and not debug:
        output_format = "text"
    if output_format == "json":
        import json

        print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        if use_chatgpt:
            text = chatgpt_helper.narrative_trip_summary(response)
        elif output_format == "legs":
            text = format_search_result(response, legs_only=True)
        else:
            text = format_search_result(response)
        print(text)


def run_departures(stop: str, output_format: str = "text", debug: bool = False, use_chatgpt: bool = False) -> None:
    """Query the departure monitor and print the result.

    Parameters
    ----------
    stop: str
        Name of the stop to query.
    output_format: str, optional
        ``"text"`` for a short summary, ``"json"`` for the raw API response.
    use_chatgpt: bool, optional
        If set, the plain-text summary is reformatted via the OpenAI API.
    """
    logger.info("Haltestelle '%s' wird ermittelt...", stop)
    lang = nlp_parser.detect_language(stop)
    try:
        result = efa_api.dm_request(stop, lang=lang)
    except Exception as exc:
        logger.error("Fehler bei der Abfrage: %s", exc)
        return

    logger.info("Suche wird gestartet...")
    logger.info("Ergebnisse gefunden.")
    if output_format == "json" and not debug:
        output_format = "text"
    if output_format == "json":
        import json

        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        text = format_departures_result(result)
        if use_chatgpt:
            text = chatgpt_helper.reformat_summary(text)
        print(text)


def run_stop_finder(query: str, output_format: str = "text", debug: bool = False, use_chatgpt: bool = False) -> None:
    """Query the stop finder and print the result.

    Parameters
    ----------
    query: str
        Text to search for stops.
    output_format: str, optional
        ``"text"`` for a short summary, ``"json"`` for the raw API response.
    use_chatgpt: bool, optional
        If set, the plain-text summary is reformatted via the OpenAI API.
    """
    logger.info("Searching stops...")
    lang = nlp_parser.detect_language(query)
    try:
        result = efa_api.stopfinder_request(query, lang=lang)
    except Exception as exc:
        logger.error("Error during request: %s", exc)
        return
    if output_format == "json" and not debug:
        output_format = "text"
    if output_format == "json":
        import json

        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        text = format_stops_result(result)
        if use_chatgpt:
            text = chatgpt_helper.reformat_summary(text)
        print(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="suedtirolmobilAI CLI")
    parser.add_argument("command", choices=["search", "departures", "stops"], help="Command to execute")
    parser.add_argument("text", nargs="+", help="Query text or stop name")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--format",
        choices=["text", "json", "legs"],
        default="legs",
        help="Output format",
    )
    parser.add_argument(
        "--chatgpt",
        action="store_true",
        help="Generate a short ChatGPT summary",
    )

    args = parser.parse_args()
    setup_logging(args.debug)

    argument = " ".join(args.text)
    if args.command == "search":
        run_search(argument, args.format, debug=args.debug, use_chatgpt=args.chatgpt)
    elif args.command == "departures":
        run_departures(argument, args.format, debug=args.debug, use_chatgpt=args.chatgpt)
    elif args.command == "stops":
        run_stop_finder(argument, args.format, debug=args.debug, use_chatgpt=args.chatgpt)
