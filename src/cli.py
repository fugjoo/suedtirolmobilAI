import sys
from . import nlp_parser, efa_api


def run_search(query: str) -> None:
    """Run a search for the given natural language query with progress output."""
    print("Searching for stops...")
    params = nlp_parser.parse_query(query)

    if not params:
        print("No parameters extracted from the query.")
        return

    print("Determining results...")
    try:
        response = efa_api.search_efa(params)
    except Exception as exc:
        print(f"Error during search: {exc}")
        return

    print("Interpreting results...")
    if isinstance(response, dict) and "trips" in response:
        trips = response.get("trips") or []
        print(f"Found {len(trips)} trips.")
    else:
        print("No trip data found.")

    print("Returning search results...")
    print(response)


def run_departures(stop: str) -> None:
    """Query the departure monitor and show progress messages."""
    print(f"Haltestelle '{stop}' wird ermittelt...")
    try:
        result = efa_api.dm_request(stop)
    except Exception as exc:
        print(f"Fehler bei der Abfrage: {exc}")
        return

    print("Suche wird gestartet...")
    print("Ergebnisse gefunden.")
    print(result)


def run_stop_finder(query: str) -> None:
    print("Searching stops...")
    try:
        result = efa_api.stop_finder(query)
    except Exception as exc:
        print(f"Error during request: {exc}")
        return
    print(result)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m src.cli [search|departures|stops] 'query'")
        sys.exit(1)

    command = sys.argv[1]
    argument = " ".join(sys.argv[2:])
    if command == "search":
        run_search(argument)
    elif command == "departures":
        run_departures(argument)
    elif command == "stops":
        run_stop_finder(argument)
    else:
        print(f"Unknown command: {command}")
