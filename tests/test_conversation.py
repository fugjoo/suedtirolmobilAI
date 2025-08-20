import os
import sys
from types import SimpleNamespace

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import openai
from src import conversation


class DummyClient:
    def __init__(self, capture, content="ok"):
        self._capture = capture
        self._response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create)
        )

    def _create(self, **kwargs):
        self._capture["messages"] = kwargs.get("messages")
        return self._response


def test_respond_invokes_mcp(monkeypatch):
    capture = {}

    def fake_call_mcp(text: str) -> str:
        capture["called"] = True
        return "MCP RESULT"

    monkeypatch.setattr(conversation.openai, "OpenAI", lambda api_key=None: DummyClient(capture))
    os.environ["OPENAI_API_KEY"] = "test"
    messages = [{"role": "user", "content": "show departures for Bolzano"}]
    result = conversation.respond(messages, call_mcp_fn=fake_call_mcp)
    assert result == "ok"
    assert capture.get("called") is True
    assert any("MCP RESULT" in m["content"] for m in capture["messages"])


def test_respond_mcp_failure(monkeypatch):
    def failing_call_mcp(text: str) -> str:
        raise ConnectionError("boom")

    def fail_openai(*args, **kwargs):  # pragma: no cover - should not be called
        raise AssertionError("openai should not be called")

    monkeypatch.setattr(conversation.openai, "OpenAI", fail_openai)
    os.environ["OPENAI_API_KEY"] = "test"
    messages = [{"role": "user", "content": "show departures"}]
    result = conversation.respond(messages, call_mcp_fn=failing_call_mcp)
    assert "temporarily unavailable" in result.lower()
