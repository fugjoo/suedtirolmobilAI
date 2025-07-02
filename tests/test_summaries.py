import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.summaries import format_stops_result


def test_format_stops_result_handles_null_stopfinder():
    result = {"stopFinder": None}
    assert format_stops_result(result) == "0 stops found."


def test_format_stops_result_handles_null_points():
    result = {"stopFinder": {"points": None}}
    assert format_stops_result(result) == "0 stops found."
