import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.summaries import format_stops_result
from src.summaries import format_search_result, format_departures_result


def test_format_stops_result_handles_null_stopfinder():
    result = {"stopFinder": None}
    assert format_stops_result(result) == "0 stops found."


def test_format_stops_result_handles_null_points():
    result = {"stopFinder": {"points": None}}
    assert format_stops_result(result) == "0 stops found."


def test_format_stops_result_handles_points_list():
    result = {
        "stopFinder": {
            "points": [
                {"name": "A", "anyType": "stop", "quality": "10"},
                {"name": "B", "anyType": "location", "quality": "20"},
            ]
        }
    }
    summary = format_stops_result(result)
    assert "Gefundene Haltestellen:" in summary
    lines = summary.splitlines()
    # first entry should be the stop type
    assert lines[1].startswith("A (stop)")
    # best result flagged on line with highest quality
    assert any("B (location) [beste]" in l for l in lines)


def test_format_search_result_handles_points_leg():
    result = {
        "trips": {
            "trip": {
                "legs": [
                    {
                        "points": [
                            {
                                "name": "Start",
                                "platformName": "B",
                                "dateTime": {"time": "10:00"},
                            },
                            {
                                "name": "End",
                                "platformName": "F",
                                "dateTime": {"time": "10:30"},
                            },
                        ],
                        "mode": {"name": "Bus B123", "destination": "End"},
                    }
                ]
            }
        }
    }

    summary = format_search_result(result)
    assert "Ab: Start" in summary
    assert "um 10:00 Uhr" in summary
    assert "von Steig B" in summary
    assert "An: End" in summary
    assert "um 10:30 Uhr" in summary
    assert "auf Steig F" in summary


def test_format_search_result_multiple_legs_separated():
    result = {
        "trips": {
            "trip": {
                "legs": [
                    {
                        "origin": {"name": "A", "platformName": "F", "time": "10:00"},
                        "destination": {"name": "B", "platformName": "1", "time": "10:30"},
                        "mode": {"name": "Bus B200", "destination": "B"},
                    },
                    {
                        "origin": {"name": "B", "platformName": "2", "time": "10:40"},
                        "destination": {"name": "C", "platformName": "3", "time": "11:00"},
                        "mode": {"name": "Bus B300", "destination": "C"},
                    },
                ]
            }
        }
    }

    summary = format_search_result(result)
    lines = summary.splitlines()
    # ensure there is an empty line separating the two legs
    assert "" in lines
    assert lines[0].startswith("Ab: A")
    assert lines[2] == ""
    assert lines[3].startswith("Ab: B")


def test_format_departures_result_formats_line():
    result = {
        "stop_name": "Brixen",
        "departures": {
            "departure": [
                {
                    "time": "13:20",
                    "servingLine": {
                        "name": "Bus",
                        "number": "401",
                        "direction": "Brixen Bahnhof",
                    },
                    "platformName": "A",
                }
            ]
        },
    }

    summary = format_departures_result(result)
    assert "Abfahrten f" in summary
    assert "Bus 401 Richtung Brixen Bahnhof Steig A um 13:20 Uhr" in summary

