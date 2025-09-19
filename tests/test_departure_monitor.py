from datetime import timedelta

from suedtirolmobilai.handlers import normalize_departure_monitor
from suedtirolmobilai.schemas import Departure


def test_departure_monitor_realtime_flags(load_fixture):
    payload = load_fixture("departure_monitor_departures.json")
    departures = normalize_departure_monitor(payload)

    assert len(departures) == 2
    for item in departures:
        validated = Departure.model_validate(item.model_dump())
        assert validated == item

    realtime_departure = departures[0]
    assert realtime_departure.movement_type == "departure"
    assert realtime_departure.realtime.is_realtime is True
    assert realtime_departure.realtime.delay_seconds == 120
    assert realtime_departure.estimated_time == realtime_departure.planned_time + timedelta(
        minutes=2
    )
    assert realtime_departure.realtime.source == "efa-realtime"

    scheduled_only = departures[1]
    assert scheduled_only.realtime.is_realtime is False
    assert scheduled_only.estimated_time is None
    assert scheduled_only.realtime.delay_seconds == 0


def test_arrival_monitor_behaviour(load_fixture):
    payload = load_fixture("departure_monitor_arrivals.json")
    arrivals = normalize_departure_monitor(payload)

    assert len(arrivals) == 1
    arrival = arrivals[0]
    assert arrival.movement_type == "arrival"
    assert arrival.realtime.is_realtime is True
    assert arrival.realtime.delay_seconds == -60
    assert arrival.estimated_time == arrival.planned_time + timedelta(minutes=-1)
