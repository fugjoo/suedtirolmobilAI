"""Tests for the AIAgent conversation manager."""

from __future__ import annotations

import inspect
import json
import os
import sys
import types

import anyio
import openai
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src import ai_agent, mcp_server


class DummyClient:
    """Minimal stand-in for the OpenAI client used by the agent."""

    def __init__(self, messages):
        self._messages = iter(messages)

    @property
    def chat(self):  # pragma: no cover - trivial property
        return types.SimpleNamespace(
            completions=types.SimpleNamespace(create=self._create)
        )

    def _create(self, *args, **kwargs):  # pragma: no cover - parameters unused
        message = next(self._messages)
        choice = types.SimpleNamespace(message=message)
        return types.SimpleNamespace(choices=[choice])


def _run(func, *args, **kwargs):
    """Execute ``func`` whether it is sync or async."""
    if inspect.iscoroutinefunction(func):
        return anyio.run(lambda: func(*args, **kwargs))
    return func(*args, **kwargs)


def _memory(agent):
    """Return the internal memory list from ``agent``."""
    return getattr(agent, "memory", getattr(agent, "_memory"))


def _user_messages(memory):
    """Extract user message texts from ``memory`` entries."""
    texts = []
    for item in memory:
        if isinstance(item, dict):
            role = item.get("role")
            if role == "user" or role is None:
                texts.append(item.get("content"))
        elif isinstance(item, types.SimpleNamespace):
            role = getattr(item, "role", None)
            if role == "user" or role is None:
                texts.append(getattr(item, "content", None))
        else:
            texts.append(str(item))
    return [t for t in texts if t is not None]


def test_memory_limit(monkeypatch):
    """The agent keeps only the last N messages in memory."""
    responses = [types.SimpleNamespace(content="ok") for _ in range(5)]
    monkeypatch.setattr(openai, "OpenAI", lambda api_key=None: DummyClient(responses))
    agent = ai_agent.AIAgent(memory_limit=3)
    for i in range(5):
        _run(agent.ask, f"msg{i}")
    memory = _memory(agent)
    user_texts = _user_messages(memory)
    assert user_texts == ["msg2", "msg3", "msg4"]


def test_reset_clears_memory(monkeypatch):
    """Calling ``reset`` removes all stored messages."""
    responses = [types.SimpleNamespace(content="ok")]
    monkeypatch.setattr(openai, "OpenAI", lambda api_key=None: DummyClient(responses))
    agent = ai_agent.AIAgent(memory_limit=3)
    _run(agent.ask, "hello")
    agent.reset()
    assert _memory(agent) == []


def test_mcp_request(monkeypatch):
    """Tool calls returned by OpenAI trigger MCP requests."""
    calls = []

    async def fake_call_tool(name, payload):
        calls.append((name, payload))
        return [types.SimpleNamespace(text="data")]

    monkeypatch.setattr(mcp_server, "call_tool", fake_call_tool)
    message = types.SimpleNamespace(
        content="done",
        tool_calls=[
            types.SimpleNamespace(
                function=types.SimpleNamespace(
                    name="search", arguments=json.dumps({"text": "foo"})
                )
            )
        ],
    )
    monkeypatch.setattr(openai, "OpenAI", lambda api_key=None: DummyClient([message]))
    agent = ai_agent.AIAgent(memory_limit=3)
    _run(agent.ask, "foo")
    assert calls and calls[0][0] == "search"
