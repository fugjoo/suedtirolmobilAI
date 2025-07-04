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
    assert "A (stop)" in summary
    assert "B (location)" in summary
    lines = summary.splitlines()
    top_line = [l for l in lines if l.startswith("[TOP]")][0]
    assert top_line.startswith("[TOP] ")


def test_format_stops_result_english():
    result = {
        "stopFinder": {
            "points": [
                {"name": "A", "anyType": "stop", "quality": "10"}
            ]
        }
    }
    summary = format_stops_result(result, lang="en")
    assert "Stops found:" in summary


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


def test_format_departures_result_formats_line():
    result = {
        "stop_name": "Brixen",
        "departures": {
            "departure": [
                {
                    "time": "13:20",
                    "servingLine": {
                        "name": "Citybus 320.1",
                        "direction": "Milland KG Arcobaleno",
                    },
                    "platformName": "A",
                }
            ]
        },
    }

    summary = format_departures_result(result)
    assert "Abfahrten f" in summary
    assert (
        "13:20 Citybus 320.1 Richtung Milland KG Arcobaleno Steig A" in summary
    )


def test_format_departures_result_includes_number():
    result = {
        "departures": {
            "departure": [
                {
                    "time": "08:00",
                    "servingLine": {
                        "name": "Bus sostitutivo",
                        "number": "B200",
                        "direction": "Merano Express",
                    },
                    "platformName": "F",
                }
            ]
        }
    }

    summary = format_departures_result(result)
    assert "Bus sostitutivo B200" in summary
    assert "Steig F" in summary


def test_format_search_result_structured_time():
    result = {
        "trips": {
            "trip": {
                "legs": [
                    {
                        "points": [
                            {
                                "name": "Start",
                                "platformName": "B",
                                "dateTime": {"hour": "10", "minute": "05"},
                            },
                            {
                                "name": "End",
                                "platformName": "C",
                                "dateTime": {"hour": "10", "minute": "35"},
                            },
                        ],
                        "mode": {"name": "Bus B1", "destination": "End"},
                    }
                ]
            }
        }
    }

    summary = format_search_result(result)
    assert "um 10:05 Uhr" in summary
    assert "um 10:35 Uhr" in summary


def test_format_search_result_legs_only():
    result = {
        "trips": {
            "trip": {
                "legs": [
                    {
                        "origin": {"name": "A", "platformName": "1", "time": "08:00"},
                        "destination": {"name": "B", "platformName": "2", "time": "08:30"},
                        "mode": {"name": "Bus 10", "destination": "B"},
                    }
                ]
            }
        }
    }

    summary = format_search_result(result, legs_only=True)
    assert summary.startswith("Bus 10 Richtung B")
    assert "08:00: A von Steig 1" in summary
    assert "08:30: B auf Steig 2" in summary


def test_format_departures_result_structured_time():
    result = {
        "departures": {
            "departure": [
                {
                    "dateTime": {"hour": "09", "minute": "15"},
                    "servingLine": {"name": "Bus", "direction": "Town"},
                    "platformName": "1",
                }
            ]
        }
    }

    summary = format_departures_result(result)
    assert "09:15 Bus Richtung Town Steig 1" in summary


def test_format_departures_result_english():
    result = {
        "departures": {
            "departure": [
                {
                    "time": "08:00",
                    "servingLine": {"name": "Bus", "direction": "Town"},
                    "platformName": "1",
                }
            ]
        }
    }

    summary = format_departures_result(result, lang="en")
    assert "Departures" in summary
    assert "Platform" in summary

