import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.summaries import (
    format_stops_result,
    format_search_result,
    format_departures_result,
    format_search_result_legs_only,
)


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
    assert "[TOP]" in summary


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
        "Citybus 320.1 Richtung Milland KG Arcobaleno Steig A um 13:20 Uhr" in summary
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


def test_format_search_result_legs_only():
    result = {
        "trips": {
            "trip": {
                "legs": [
                    {
                        "origin": {
                            "name": "Bolzano, Stazione di Bolzano",
                            "platformName": "1",
                            "time": "16:36",
                        },
                        "destination": {
                            "name": "Termeno sulla Strada del Vino, Stazione di Egna - Termeno",
                            "platformName": "1",
                            "time": "17:00",
                        },
                        "mode": {
                            "name": "Treno regionale R 16697",
                            "destination": "Verona Porta Nuova",
                        },
                    },
                    {
                        "origin": {
                            "name": "Termeno sulla Strada del Vino, Stazione di Egna - Termeno",
                            "time": "17:11",
                        },
                        "destination": {
                            "name": "Villa, Villa di Sopra",
                            "time": "17:18",
                        },
                        "mode": {
                            "name": "Bus 142",
                            "destination": "Aldino - Pietralba",
                        },
                    },
                ]
            }
        }
    }

    summary = format_search_result_legs_only(result)
    assert "Treno regionale R 16697 Richtung Verona Porta Nuova" in summary
    assert "16:36: Bolzano, Stazione di Bolzano von Steig 1" in summary
    assert "17:00: Termeno sulla Strada del Vino, Stazione di Egna - Termeno auf Steig 1" in summary
    assert "Bus 142 Richtung Aldino - Pietralba" in summary
    assert "17:11: Termeno sulla Strada del Vino, Stazione di Egna - Termeno" in summary
    assert "17:18: Villa, Villa di Sopra" in summary

