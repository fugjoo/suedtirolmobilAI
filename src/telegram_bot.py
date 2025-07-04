import os
import sys
import argparse

if sys.version_info < (3, 8):
    raise RuntimeError("telegram_bot.py requires Python 3.8 or newer")

import requests
from telegram.ext import Application, MessageHandler, filters

API_URL = os.getenv("API_URL", "http://localhost:8000")
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
USE_CHATGPT = False


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Telegram interface for suedtirolmobilAI")
    parser.add_argument(
        "--api-url",
        default=API_URL,
        help="Base URL of the API server",
    )
    parser.add_argument(
        "--chatgpt",
        action="store_true",
        help="Use ChatGPT summaries via the API",
    )
    return parser.parse_args(args)

async def handle_text(update, context):
    text = update.message.text
    try:
        url = f"{API_URL}/search?format=text"
        if USE_CHATGPT:
            url += "&chatgpt=true"
        resp = requests.post(url, json={"text": text})
        if resp.status_code == 200:
            await update.message.reply_text(resp.text)
        else:
            await update.message.reply_text(f"Error: {resp.text}")
    except Exception as exc:
        await update.message.reply_text(f"Request failed: {exc}")


def main() -> None:
    global API_URL, USE_CHATGPT

    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN environment variable not set")

    args = parse_args()
    API_URL = args.api_url
    USE_CHATGPT = args.chatgpt

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.run_polling()


if __name__ == "__main__":
    main()
