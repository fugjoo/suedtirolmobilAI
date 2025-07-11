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


def test_parse_trip_default_modes():
    q = parser.parse("von A nach B")
    assert q.bus is True
    assert q.zug is True
    assert q.seilbahn is True


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
    assert "inclMOT_ZUG" not in params
    assert "inclMOT_8" not in params
    assert params["lineRestriction"] == "401"
    assert params["itdTripDateTimeDepArr"] == "arr"
    assert params["language"] == "it"


def test_build_trip_params_defaults():
    params = efa_api.build_trip_params("A", "B")
    assert params["inclMOT_BUS"] == "true"
    assert params["inclMOT_ZUG"] == "true"
    assert params["inclMOT_8"] == "true"
    assert params["itdTripDateTimeDepArr"] == "dep"


def test_build_trip_params_only_train():
    params = efa_api.build_trip_params(
        "A",
        "B",
        "2025-02-03T12:00",
        bus=False,
        zug=True,
        seilbahn=False,
    )
    assert "inclMOT_BUS" not in params
    assert params["inclMOT_ZUG"] == "true"
    assert "inclMOT_8" not in params


def test_build_trip_params_no_bus():
    params = efa_api.build_trip_params(
        "A",
        "B",
        "2025-02-03T12:00",
        bus=False,
        zug=True,
        seilbahn=True,
    )
    assert "inclMOT_BUS" not in params
    assert params["inclMOT_ZUG"] == "true"
    assert params["inclMOT_8"] == "true"


def test_parse_without_train():
    q = parser.parse("von Bozen nach Brixen heute um 17:00 ohne zug")
    assert q.bus is True
    assert q.zug is False
    assert q.seilbahn is True


def test_language_detection_italian():
    q = parser.parse("un collegamento da Malles a Merano")
    assert q.language == "it"


def test_language_detection_english():
    q = parser.parse("a trip from Merano to Bolzano")
    assert q.language == "en"
