import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src import services
from src.services import DeparturesRequest


def test_departures_service_no_results(monkeypatch):
    def fake_stop_finder(stop: str, language: str = "de"):
        return {
            "stopFinder": {
                "points": [
                    {"name": stop, "stateless": "1", "anyType": "stop", "quality": 1}
                ]
            }
        }

    def fake_departure_monitor(stop, limit, stateless=None, language="de"):
        return {"departureList": None}

    monkeypatch.setattr(services.efa_api, "stop_finder", fake_stop_finder)
    monkeypatch.setattr(services.efa_api, "departure_monitor", fake_departure_monitor)
    monkeypatch.setattr(services.request_logger, "log_entry", lambda *a, **k: None)

    result = services.departures_service(DeparturesRequest(stop="Bozen"), format="text")
    assert "Keine Ergebnisse" in result
