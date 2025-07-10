import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src import parser, efa_api  # noqa:E402


def test_relative_weekend():
    iso = parser.relative_iso("am Wochenende")
    assert iso is not None
    now = datetime.now()
    days = (5 - now.weekday()) % 7
    if days <= 0:
        days += 7
    expected = (now + timedelta(days=days)).strftime("%Y-%m-%d")
    assert iso.startswith(expected)


def test_parse_trip_simple():
    q = parser.parse("von A nach B um 12:30")
    assert q.type == "trip"
    assert q.from_location == "A"
    assert q.to_location == "B"
    assert q.datetime == "2025-01-01T12:30"


def test_parse_departure():
    q = parser.parse("Abfahrten Bozen")
    assert q.type == "departure"
    assert q.from_location == "Bozen"


def test_best_point_prefers_stop():
    points = [
        {"anyType": "platform", "quality": 10},
        {"anyType": "stop", "quality": 3},
        {"anyType": "stop", "quality": 2},
    ]
    best = efa_api.best_point(points)
    assert best == {"anyType": "stop", "quality": 3}


def test_build_trip_params_long_distance():
    params = efa_api.build_trip_params(
        "A",
        "B",
        "2025-02-03T12:00",
        bus=True,
        zug=False,
        seilbahn=False,
        long_distance=False,
        datetime_mode="arr",
        language="it",
    )
    assert params["inclMOT_BUS"] == "true"
    assert params["inclMOT_ZUG"] == "false"
    assert params["inclMOT_8"] == "false"
    assert params["lineRestriction"] == "401"
    assert params["itdTripDateTimeDepArr"] == "arr"
    assert params["language"] == "it"
