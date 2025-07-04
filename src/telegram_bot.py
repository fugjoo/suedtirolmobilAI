import os
import sys
import argparse
import subprocess
import time

if sys.version_info < (3, 8):
    raise RuntimeError("telegram_bot.py requires Python 3.8 or newer")

import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, filters

from . import chatgpt_helper

API_URL = os.getenv("API_URL", "http://localhost:8000")
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")


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
    return parser.parse_args(args)

async def handle_text(update, context):
    """Handle free text by classifying the request via ChatGPT."""
    text = update.message.text
    try:
        info = chatgpt_helper.classify_query_chatgpt(text)
    except Exception as exc:
        info = {}

    endpoint = (info.get("endpoint") or "search").lower()
    if endpoint == "departures":
        stop = info.get("stop") or text
        url = f"{API_URL}/departures?format=text&chatgpt=true"
        payload = {"stop": stop}
    elif endpoint == "stops":
        query = info.get("query") or text
        url = f"{API_URL}/stops?format=text&chatgpt=true"
        payload = {"query": query}
    else:
        url = f"{API_URL}/search?chatgpt=true"
        payload = {"text": text}

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
        await update.message.reply_text("Please provide a query after /search")
        return
    try:
        resp = requests.post(f"{API_URL}/search?chatgpt=true", json={"text": query})
        if resp.status_code == 200:
            await update.message.reply_text(resp.text)
        else:
            await update.message.reply_text(f"Error: {resp.text}")
    except Exception as exc:
        await update.message.reply_text(f"Request failed: {exc}")


async def cmd_departures(update, context):
    stop = update.message.text.partition(" ")[2].strip()
    if not stop:
        await update.message.reply_text("Please provide a stop name after /departures")
        return
    try:
        url = f"{API_URL}/departures?format=text&chatgpt=true"
        resp = requests.post(url, json={"stop": stop})
        if resp.status_code == 200:
            await update.message.reply_text(resp.text)
        else:
            await update.message.reply_text(f"Error: {resp.text}")
    except Exception as exc:
        await update.message.reply_text(f"Request failed: {exc}")


async def cmd_stops(update, context):
    query = update.message.text.partition(" ")[2].strip()
    if not query:
        await update.message.reply_text("Please provide search text after /stops")
        return
    try:
        url = f"{API_URL}/stops?format=text&chatgpt=true"
        resp = requests.post(url, json={"query": query})
        if resp.status_code == 200:
            await update.message.reply_text(resp.text)
        else:
            await update.message.reply_text(f"Error: {resp.text}")
    except Exception as exc:
        await update.message.reply_text(f"Request failed: {exc}")


def main() -> None:
    global API_URL

    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN environment variable not set")

    args = parse_args()
    API_URL = args.api_url


    server_proc = None
    if args.start_server:
        cmd = ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]
        server_proc = subprocess.Popen(cmd)
        # Give the server a moment to start
        time.sleep(1)

    try:
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
        )
        application.run_polling()
    finally:
        if server_proc:
            server_proc.terminate()

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("search", cmd_search))
    application.add_handler(CommandHandler("departures", cmd_departures))
    application.add_handler(CommandHandler("stops", cmd_stops))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.run_polling()



if __name__ == "__main__":
    main()
