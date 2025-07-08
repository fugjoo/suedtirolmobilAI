"""Interactive console chatbot for public transport queries."""

import json
from typing import Dict, Any

from . import nlp_parser, efa_api, summaries, chatgpt_helper
from .logging_utils import setup_logging


def _build_trip_params(info: Dict[str, Any]) -> Dict[str, Any]:
    """Convert parsed info to EFA search parameters."""
    params: Dict[str, Any] = {}
    if info.get("from"):
        params["from_stop"] = info["from"]
    if info.get("to"):
        params["to_stop"] = info["to"]
    if info.get("datetime"):
        time_part = info["datetime"].split("T")[-1][:5]
        params["time"] = time_part
    if info.get("language"):
        params["lang"] = info["language"]
    return params


def chat_loop() -> None:
    """Start a simple chat loop on the console."""
    setup_logging()
    print("Enter text (empty line to quit):")
    while True:
        try:
            text = input(" > ").strip()
        except EOFError:
            break
        if not text:
            break
        try:
            info = chatgpt_helper.parse_request_llm(text)
        except Exception as exc:
            print(f"Parse failed: {exc}")
            continue
        req_type = info.get("type")
        language = info.get("language") or nlp_parser.detect_language(text)
        if req_type == "trip":
            params = _build_trip_params(info)
            result = efa_api.search_efa(params)
            try:
                reply = chatgpt_helper.format_trip_response_llm(result, lang=language)
            except Exception:
                reply = summaries.format_search_result(result, lang=language)
            print(reply)
        elif req_type == "departure":
            stop = info.get("from") or info.get("to") or text
            result = efa_api.dm_request(stop, lang=language)
            print(summaries.format_departures_result(result, lang=language))
        elif req_type == "stop":
            query = info.get("from") or info.get("to") or text
            result = efa_api.stopfinder_request(query, lang=language)
            print(summaries.format_stops_result(result, lang=language))
        else:
            print("Sorry, I could not understand your request.")


if __name__ == "__main__":
    chat_loop()
