"""Telegram bot acting as an MCP client."""

import argparse
import json
import logging
import os
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.websocket import websocket_client
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

MAX_MESSAGE_LENGTH = 4096

API_URL = os.getenv("API_URL", "http://localhost:8000")
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send greeting and show command keyboard."""
    keyboard = [
        [
            KeyboardButton("/search"),
            KeyboardButton("/departures"),
            KeyboardButton("/stops"),
            KeyboardButton("/reset"),
        ]
    ]
    await update.message.reply_text(
        "Send a query or choose a command:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )


async def call_api(
    command: str, session_id: str, text: str, *, json_response: bool = False
) -> Any:
    """Call an MCP tool via WebSocket.

    A user-friendly message is returned if the API server is unreachable.
    """
    payload = {"session_id": session_id, "text": text}
    try:
        async with websocket_client(API_URL) as (read, write):
            session = ClientSession(read, write)
            await session.initialize()
            result = await session.call_tool(command.lstrip("/"), payload)
    except Exception as exc:  # pragma: no cover - network
        logger.error("Request failed: %s", exc)
        return "Service temporarily unavailable. Please try again later."

    texts = [c.text for c in result.content if hasattr(c, "text")]
    combined = "\n".join(texts)
    try:
        data = json.loads(combined)
    except ValueError:
        data = combined
    if json_response:
        return data
    if isinstance(data, dict) and "data" in data:
        content = data["data"]
        return content if isinstance(content, str) else json.dumps(
            content, indent=2, ensure_ascii=False
        )
    return data if isinstance(data, str) else json.dumps(
        data, indent=2, ensure_ascii=False
    )


async def send_reply(update: Update, text: str) -> None:
    """Send text in chunks to avoid Telegram message limits."""
    for i in range(0, len(text), MAX_MESSAGE_LENGTH):
        await update.message.reply_text(text[i : i + MAX_MESSAGE_LENGTH])


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    text = update.message.text.strip()
    session_id = str(update.effective_user.id)
    pending = context.user_data.get("pending")

    if text == "/search":
        context.user_data["pending"] = "search"
        await send_reply(update, "Enter trip query:")
        return
    if text == "/departures":
        context.user_data["pending"] = "departures"
        await send_reply(update, "Enter stop name:")
        return
    if text == "/stops":
        context.user_data["pending"] = "stops"
        await send_reply(update, "Enter search text:")
        return
    if text == "/reset":
        context.user_data.clear()
        await call_api("reset_session", session_id, "")
        await send_reply(update, "Conversation reset")
        return

    if pending == "search":
        context.user_data["pending"] = None
        context.user_data["session_active"] = True
        reply = await call_api("search", session_id, text)
        await send_reply(update, reply)
        return
    if pending == "departures":
        context.user_data["pending"] = None
        reply = await call_api("departures", session_id, text)
        await send_reply(update, reply)
        context.user_data["session_active"] = False
        return
    if pending == "stops":
        context.user_data["pending"] = None
        reply = await call_api("stops", session_id, text)
        await send_reply(update, reply)
        return

    if context.user_data.get("session_active"):
        reply = await call_api("update_query", session_id, text)
    else:
        reply = await call_api("search", session_id, text)
        context.user_data["session_active"] = True
    await send_reply(update, reply)


def run_bot(token: str) -> None:
    """Start the Telegram bot."""
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    application.run_polling()


def main() -> None:
    """Parse arguments and run the bot."""
    global API_URL
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default=API_URL, help="MCP server URL")
    parser.add_argument("--token", default=TOKEN, help="Telegram bot token")
    parser.add_argument("--debug", action="store_true", help="enable debug logging")
    args = parser.parse_args()
    API_URL = args.api_url
    if not args.token:
        parser.error("Telegram token not provided")
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("telegram.ext").setLevel(logging.INFO)
        logger.debug("Debug mode active")
        logger.debug("Args: %s", args)
    run_bot(args.token)


if __name__ == "__main__":
    main()

