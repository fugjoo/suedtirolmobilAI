"""CLI entry point for the suedtirolmobilAI demo."""

import argparse
from pprint import pprint

try:  # Support running as a script or as part of the package
    from fahrplan_api import (
        get_departures,
        search_connection,
        search_stop_or_address,
    )
    from nlp_parser import parse_user_input
except ImportError:  # When imported via ``src`` package
    from .fahrplan_api import (
        get_departures,
        search_connection,
        search_stop_or_address,
    )
    from .nlp_parser import parse_user_input


def handle_request(text: str):
    """Parse the text and route the request to the correct API wrapper."""
    parsed = parse_user_input(text)
    if parsed.intent == "departures" and parsed.stop_query:
        result = get_departures(parsed.stop_query, parsed.time)
    elif parsed.intent == "connection" and parsed.from_location and parsed.to_location:
        result = search_connection(parsed.from_location, parsed.to_location, parsed.time)
    else:
        result = search_stop_or_address(parsed.stop_query or text)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the Fahrplan API via natural language")
    parser.add_argument("text", help="Text to parse and send to the API")
    args = parser.parse_args()

    response = handle_request(args.text)
    pprint(response)


if __name__ == "__main__":
    main()
