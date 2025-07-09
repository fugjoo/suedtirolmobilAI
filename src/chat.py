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
            from_sf = efa_api.stop_finder(q.from_location)
            from_points = from_sf.get("stopFinder", {}).get("points", [])
            to_sf = efa_api.stop_finder(q.to_location)
            to_points = to_sf.get("stopFinder", {}).get("points", [])
            if not from_points or not to_points:
                print("Stop not found")
                continue
            from_point = from_points[0]
            to_point = to_points[0]
            if args.debug:
                debug_info = {
                    "fromStateless": from_point.get("stateless"),
                    "toStateless": to_point.get("stateless"),
                }
                params = efa_api.build_trip_params(
                    from_point.get("name", q.from_location),
                    to_point.get("name", q.to_location),
                    q.datetime,
                    origin_stateless=from_point.get("stateless"),
                    destination_stateless=to_point.get("stateless"),
                )
                debug_info["request"] = {
                    "url": f"{efa_api.BASE_URL}/XML_TRIP_REQUEST2",
                    "params": params,
                }
                print(json.dumps(debug_info, indent=2, ensure_ascii=False))
            data = efa_api.trip_request(
                from_point.get("name", q.from_location),
                to_point.get("name", q.to_location),
                q.datetime,
                origin_stateless=from_point.get("stateless"),
                destination_stateless=to_point.get("stateless"),
            )
            if args.llm_format:
                try:
                    print(llm_formatter.format_trip(data, language=q.language or "de"))
                except Exception as exc:
                    print(f"Format error: {exc}")
            else:
                print(data)
        elif q.type == "departure" and q.from_location:
            sf_data = efa_api.stop_finder(q.from_location)
            points = sf_data.get("stopFinder", {}).get("points", [])
            if not points:
                print("Stop not found")
                continue
            point = points[0]
            if args.debug:
                params = efa_api.build_departure_params(
                    point.get("name", q.from_location),
                    stateless=point.get("stateless"),
                )
                debug_info = {
                    "stateless": point.get("stateless"),
                    "request": {
                        "url": f"{efa_api.BASE_URL}/XML_DM_REQUEST",
                        "params": params,
                    },
                }
                print(json.dumps(debug_info, indent=2, ensure_ascii=False))
            data = efa_api.departure_monitor(
                point.get("name", q.from_location),
                stateless=point.get("stateless"),
            )
            if args.llm_format:
                try:
                    print(llm_formatter.format_departures(data, language=q.language or "de"))
                except Exception as exc:
                    print(f"Format error: {exc}")
            else:
                print(data)
        else:
            print("Couldn't understand query")


if __name__ == "__main__":
    main()
