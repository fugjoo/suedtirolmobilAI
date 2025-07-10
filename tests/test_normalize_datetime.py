import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime, timedelta

from src.llm_parser import _normalize_datetime


def test_normalize_today():
    iso = _normalize_datetime("heute", "")
    assert iso.startswith(datetime.now().strftime("%Y-%m-%d"))


def test_normalize_morgen_time():
    iso = _normalize_datetime("morgen um 09:15", "")
    tomorrow = datetime.now() + timedelta(days=1)
    expected = tomorrow.strftime("%Y-%m-%dT09:15")
    assert iso == expected


def test_normalize_iso():
    iso = _normalize_datetime("2025-03-05T10:30", "")
    year = datetime.now().year
    expected = datetime(year, 3, 5, 10, 30).strftime("%Y-%m-%dT%H:%M")
    assert iso == expected
