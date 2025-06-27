from src import formatter


def test_empty_results():
    assert formatter.format_trip_results({}) == "Keine Verbindungen gefunden."
