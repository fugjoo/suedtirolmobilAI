"""Simple Telegram bot that forwards queries to the API."""

import argparse
import asyncio
import logging
import os
import threading
from typing import Dict, Any

import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

API_URL = os.getenv("API_URL", "http://localhost:8000")
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send greeting and show command keyboard."""
    keyboard = [[KeyboardButton("/search"), KeyboardButton("/departures"), KeyboardButton("/stops")]]
    await update.message.reply_text(
        "Send a query or choose a command:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


def call_api(endpoint: str, payload: Dict[str, Any]) -> str:
    """Send POST request to the API and return response text."""
    try:
        resp = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=10)
    except Exception as exc:  # pragma: no cover - network
        logger.error("Request failed: %s", exc)
        return str(exc)
    if resp.ok:
        try:
            data = resp.json()
            if isinstance(data, dict) and "data" in data:
                return str(data["data"])
            return str(data)
        except ValueError:
            return resp.text
    return f"Error {resp.status_code}: {resp.text}"


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    text = update.message.text.strip()
    state = context.user_data.get("state")
    if text == "/search":
        context.user_data["state"] = "search"
        await update.message.reply_text("Enter trip query:")
        return
    if text == "/departures":
        context.user_data["state"] = "departures"
        await update.message.reply_text("Enter stop name:")
        return
    if text == "/stops":
        context.user_data["state"] = "stops"
        await update.message.reply_text("Enter search text:")
        return

    if state == "search":
        context.user_data.pop("state", None)
        reply = call_api("/search", {"text": text})
        await update.message.reply_text(reply)
        return
    if state == "departures":
        context.user_data.pop("state", None)
        reply = call_api("/departures", {"stop": text})
        await update.message.reply_text(reply)
        return
    if state == "stops":
        context.user_data.pop("state", None)
        reply = call_api("/stops", {"query": text})
        await update.message.reply_text(reply)
        return

    # fallback: try /search
    reply = call_api("/search", {"text": text})
    await update.message.reply_text(reply)


def run_bot(token: str, start_server: bool) -> None:
    """Start the Telegram bot."""
    if start_server:
        import uvicorn

        def serve() -> None:
            uvicorn.run("src.main:app", host="0.0.0.0")

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        logger.info("Started API server")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    application.run_polling()


def main() -> None:
    """Parse arguments and run the bot."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default=API_URL, help="API endpoint")
    parser.add_argument("--start-server", action="store_true", help="start API with uvicorn")
    parser.add_argument("--token", default=TOKEN, help="Telegram bot token")
    args = parser.parse_args()
    global API_URL
    API_URL = args.api_url
    if not args.token:
        parser.error("Telegram token not provided")
    run_bot(args.token, args.start_server)


if __name__ == "__main__":
    main()
