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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.cli 'your query'")
    else:
        run_search(" ".join(sys.argv[1:]))
