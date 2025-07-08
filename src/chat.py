"""Simple console chat loop."""

from . import parser, efa_api


def main() -> None:
    """Run console chat."""
    while True:
        try:
            text = input("> ").strip()
        except EOFError:
            break
        if not text:
            continue
        q = parser.parse(text)
        if q.type == "trip" and q.from_location and q.to_location:
            data = efa_api.trip_request(q.from_location, q.to_location, q.datetime)
            print(data)
        elif q.type == "departure" and q.from_location:
            data = efa_api.departure_monitor(q.from_location)
            print(data)
        else:
            print("Couldn't understand query")


if __name__ == "__main__":
    main()
