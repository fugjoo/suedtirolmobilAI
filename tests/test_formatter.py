import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src import llm_formatter


def test_format_trip_no_results():
    data = {"trips": None}
    msg = llm_formatter.format_trip(data, language="en")
    assert "No results found" in msg


def test_format_departures_no_results():
    data = {"departureList": None}
    msg = llm_formatter.format_departures(data, language="de")
    assert "Keine Ergebnisse" in msg
