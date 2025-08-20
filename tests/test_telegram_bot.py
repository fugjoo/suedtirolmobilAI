"""Tests for the Telegram bot message flow."""

import os
import sys
import types
from unittest.mock import AsyncMock, Mock

import anyio


def _import_bot(monkeypatch):
    """Import telegram_bot with a mocked agent."""
    fake_agent = types.SimpleNamespace(
        respond=AsyncMock(return_value="agent reply"),
        reset=Mock(),
    )
    monkeypatch.setitem(sys.modules, "ai_agent", types.SimpleNamespace(agent=fake_agent))
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from importlib import reload
    from src import telegram_bot as tb

    return reload(tb), fake_agent


async def _run_handle(tb, text):
    update = types.SimpleNamespace(
        message=types.SimpleNamespace(text=text, reply_text=AsyncMock()),
        effective_user=types.SimpleNamespace(id=1),
    )
    context = types.SimpleNamespace(user_data={})
    await tb.handle(update, context)
    return update.message.reply_text


def test_handle_forwards_to_agent(monkeypatch):
    tb, fake_agent = _import_bot(monkeypatch)
    reply_mock = anyio.run(lambda: _run_handle(tb, "hello"))
    fake_agent.respond.assert_awaited_once_with("hello", "1")
    reply_mock.assert_awaited_once_with("agent reply")


def test_reset_uses_agent(monkeypatch):
    tb, fake_agent = _import_bot(monkeypatch)
    reply_mock = anyio.run(lambda: _run_handle(tb, "/reset"))
    fake_agent.reset.assert_called_once_with("1")
    reply_mock.assert_awaited_once_with("Conversation reset")

