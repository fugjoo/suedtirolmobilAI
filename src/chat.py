"""Simple console chat loop."""

import argparse
import json

from . import efa_api, parser
from . import llm_formatter, llm_parser


def main() -> None:
    """Run console chat."""
    argp = argparse.ArgumentParser()
    argp.add_argument("--llm-parser", action="store_true", help="use OpenAI parser")
    argp.add_argument("--llm-format", action="store_true", help="format results with OpenAI")
    argp.add_argument("--debug", action="store_true", help="show parsed input JSON")
    args = argp.parse_args()

    while True:
        try:
            text = input("> ").strip()
        except EOFError:
            break
        if not text:
            continue
        if args.llm_parser:
            try:
                q = llm_parser.parse_llm(text)
            except Exception as exc:
                print(f"Parser error: {exc}")
                continue
        else:
            q = parser.parse(text)

        if args.debug:
            print(json.dumps(q.__dict__, indent=2, ensure_ascii=False))

        if q.type == "trip" and q.from_location and q.to_location:
            data = efa_api.trip_request(q.from_location, q.to_location, q.datetime)
            if args.llm_format:
                try:
                    print(llm_formatter.format_trip(data, language=q.language or "de"))
                except Exception as exc:
                    print(f"Format error: {exc}")
            else:
                print(data)
        elif q.type == "departure" and q.from_location:
            data = efa_api.departure_monitor(q.from_location)
            print(data)
        else:
            print("Couldn't understand query")


if __name__ == "__main__":
    main()
