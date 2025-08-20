"""Telegram bot acting as an MCP client."""

import argparse
import logging
import os

from ai_agent import agent
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.error import Conflict

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


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    text = update.message.text.strip()
    if text == "/start":
        return

    session_id = str(update.effective_user.id)
    if text == "/reset":
        agent.reset(session_id)
        await update.message.reply_text("Conversation reset")
        return

    reply = await agent.respond(text, session_id)
    await update.message.reply_text(reply)


def run_bot(token: str) -> None:
    """Start the Telegram bot."""
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, handle))
    try:
        application.run_polling()
    except Conflict as exc:  # pragma: no cover - network
        logger.error("Bot stopped: %s", exc)


def main() -> None:
    """Parse arguments and run the bot."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=TOKEN, help="Telegram bot token")
    parser.add_argument("--debug", action="store_true", help="enable debug logging")
    args = parser.parse_args()
    if not args.token:
        parser.error("Telegram token not provided")
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("telegram.ext").setLevel(logging.INFO)
        logger.debug("Debug mode active")
        logger.debug("Args: %s", args)
    run_bot(args.token)


if __name__ == "__main__":
    main()

