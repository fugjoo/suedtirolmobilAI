import os
import sys
import json
from types import SimpleNamespace

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.llm_parser import parse_llm
import openai


class DummyClient:
    def __init__(self, response):
        self._response = response
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=lambda **kwargs: self._response)
        )


def test_parse_llm_defaults(monkeypatch):
    data = {
        "type": "trip",
        "from": "A",
        "to": "B",
        "datetime": "2025-07-11T10:38",
        "language": "de",
        "bus": None,
        "zug": None,
        "seilbahn": None,
        "long_distance": False,
        "datetime_mode": None,
    }
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(data)))]
    )
    monkeypatch.setattr(openai, "OpenAI", lambda api_key=None: DummyClient(response))
    os.environ["OPENAI_API_KEY"] = "test"
    query = parse_llm("irrelevant")
    assert query.bus is True
    assert query.zug is True
    assert query.seilbahn is True
    assert query.datetime_mode == "dep"
