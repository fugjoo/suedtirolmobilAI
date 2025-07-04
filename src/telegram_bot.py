"""Telegram bot interface for interacting with the API service."""

import sys
import argparse
import subprocess
import time
import logging

if sys.version_info < (3, 8):
    raise RuntimeError("telegram_bot.py requires Python 3.8 or newer")

import requests

from .config import API_URL as CONFIG_API_URL, TELEGRAM_TOKEN
from telegram import ReplyKeyboardMarkup, ForceReply
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    filters,
)

from . import chatgpt_helper, nlp_parser
from .logging_utils import setup_logging

logger = logging.getLogger(__name__)

API_URL = CONFIG_API_URL
BOT_TOKEN = TELEGRAM_TOKEN
USE_CHATGPT = False

# Conversation states for interactive commands
SEARCH, DEPARTURES = range(2)


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Telegram interface for suedtirolmobilAI")
    parser.add_argument(
        "--api-url",
        default=API_URL,
        help="Base URL of the API server",
    )
    parser.add_argument(
        "--start-server",
        action="store_true",
        help="Start the API server before launching the bot",
    )
    parser.add_argument(
        "--chatgpt",
        action="store_true",
        help="Enable ChatGPT-based request handling",
    )
    return parser.parse_args(args)

async def handle_text(update, context):
    """Handle free text by classifying the request via ChatGPT."""
    text = update.message.text
    logger.info("Received message: %s", text)
    try:
        if USE_CHATGPT:
            info = chatgpt_helper.classify_query_chatgpt(text)
        else:
            info = nlp_parser.classify_request(text)
    except Exception as exc:
        logger.error("ChatGPT classification failed: %s", exc)
        info = {}

    endpoint = (info.get("endpoint") or "search").lower()
    if endpoint == "departures":
        stop = info.get("stop") or text
        url = f"{API_URL}/departures?format=text"
        if USE_CHATGPT:
            url += "&chatgpt=true"
        payload = {"stop": stop}
    elif endpoint == "stops":
        query = info.get("query") or text
        url = f"{API_URL}/stops?format=text"
        if USE_CHATGPT:
            url += "&chatgpt=true"
        payload = {"query": query}
    else:
        url = f"{API_URL}/search"
        if USE_CHATGPT:
            url += "?chatgpt=true"
        payload = {"text": text}

    logger.info("Sending request to %s with payload %s", url, payload)
    try:
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            await update.message.reply_text(resp.text)
        else:
            await update.message.reply_text(f"Error: {resp.text}")
    except Exception as exc:
        await update.message.reply_text(f"Request failed: {exc}")


async def cmd_start(update, context):
    """Send a welcome message and show the command keyboard."""
    keyboard = [["/search", "/departures", "/stops"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome! Send me a request or choose a command.", reply_markup=markup
    )


async def cmd_search(update, context):
    query = update.message.text.partition(" ")[2].strip()
    if not query:
        await update.message.reply_text(
            "Please provide a query for /search:", reply_markup=ForceReply()
        )
        return SEARCH
    return await handle_search_query(update, context, query)


async def handle_search_query(update, context, query=None):
    if query is None:
        query = update.message.text.strip()
    logger.info("/search %s", query)
    try:
        url = f"{API_URL}/search"
        if USE_CHATGPT:
            url += "?chatgpt=true"
        payload = {"text": query}
        logger.info("Sending request to %s with payload %s", url, payload)
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            await update.message.reply_text(resp.text)
        else:
            await update.message.reply_text(f"Error: {resp.text}")
    except Exception as exc:
        await update.message.reply_text(f"Request failed: {exc}")
    return ConversationHandler.END


async def cmd_departures(update, context):
    stop = update.message.text.partition(" ")[2].strip()
    if not stop:
        await update.message.reply_text(
            "Please provide a stop name for /departures:", reply_markup=ForceReply()
        )
        return DEPARTURES
    return await handle_departures_query(update, context, stop)


async def handle_departures_query(update, context, stop=None):
    if stop is None:
        stop = update.message.text.strip()
    logger.info("/departures %s", stop)
    try:
        url = f"{API_URL}/departures?format=text"
        if USE_CHATGPT:
            url += "&chatgpt=true"
        payload = {"stop": stop}
        logger.info("Sending request to %s with payload %s", url, payload)
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            await update.message.reply_text(resp.text)
        else:
            await update.message.reply_text(f"Error: {resp.text}")
    except Exception as exc:
        await update.message.reply_text(f"Request failed: {exc}")
    return ConversationHandler.END


async def cmd_stops(update, context):
    query = update.message.text.partition(" ")[2].strip()
    if not query:
        await update.message.reply_text("Please provide search text after /stops")
        return
    logger.info("/stops %s", query)
    try:
        url = f"{API_URL}/stops?format=text"
        if USE_CHATGPT:
            url += "&chatgpt=true"
        payload = {"query": query}
        logger.info("Sending request to %s with payload %s", url, payload)
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            await update.message.reply_text(resp.text)
        else:
            await update.message.reply_text(f"Error: {resp.text}")
    except Exception as exc:
        await update.message.reply_text(f"Request failed: {exc}")


def main() -> None:
    global API_URL, USE_CHATGPT

    setup_logging()

    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN environment variable not set")

    args = parse_args()
    API_URL = args.api_url
    USE_CHATGPT = args.chatgpt


    server_proc = None
    if args.start_server:
        cmd = ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]
        try:
            server_proc = subprocess.Popen(cmd)
            # Give the server a moment to start
            time.sleep(1)
        except OSError as exc:
            logger.error("Failed to start server: %s", exc)
            server_proc = None

    try:
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", cmd_start))

        search_conv = ConversationHandler(
            entry_points=[CommandHandler("search", cmd_search)],
            states={
                SEARCH: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_search_query
                    )
                ]
            },
            fallbacks=[],
        )
        depart_conv = ConversationHandler(
            entry_points=[CommandHandler("departures", cmd_departures)],
            states={
                DEPARTURES: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_departures_query
                    )
                ]
            },
            fallbacks=[],
        )
        application.add_handler(search_conv)
        application.add_handler(depart_conv)
        application.add_handler(CommandHandler("stops", cmd_stops))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
        )
        application.run_polling()
    finally:
        if server_proc:
            server_proc.terminate()



if __name__ == "__main__":
    main()
