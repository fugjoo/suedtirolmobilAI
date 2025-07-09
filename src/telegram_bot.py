"""Simple Telegram bot that forwards queries to the API."""

import argparse
import asyncio
import json
import logging
import os
import threading
from typing import Dict, Any, List

from . import parser, efa_api, llm_parser

import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

MAX_MESSAGE_LENGTH = 4096

API_URL = os.getenv("API_URL", "http://localhost:8000")
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEBUG = False
DEBUG_INFO: List[Dict[str, Any]] = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send greeting and show command keyboard."""
    keyboard = [[KeyboardButton("/search"), KeyboardButton("/departures"), KeyboardButton("/stops"), KeyboardButton("/debug")]]
    await update.message.reply_text(
        "Send a query or choose a command:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


def call_api(endpoint: str, payload: Dict[str, Any], *, params: Dict[str, Any] = None, json_response: bool = False) -> Any:
    """Send POST request to the API and return response."""
    if DEBUG:
        logger.debug("Request %s %s %s", endpoint, params, payload)
    try:
        resp = requests.post(f"{API_URL}{endpoint}", json=payload, params=params, timeout=10)
    except Exception as exc:  # pragma: no cover - network
        logger.error("Request failed: %s", exc)
        DEBUG_INFO.append({"endpoint": endpoint, "payload": payload, "error": str(exc)})
        return str(exc)
    if resp.ok:
        try:
            data = resp.json()
        except ValueError:
            data = resp.text
        DEBUG_INFO.append({"endpoint": endpoint, "payload": payload, "response": data})
        if json_response:
            return data
        if isinstance(data, dict) and "data" in data:
            content = data["data"]
            return content if isinstance(content, str) else json.dumps(content, indent=2, ensure_ascii=False)
        return data if isinstance(data, str) else json.dumps(data, indent=2, ensure_ascii=False)
    DEBUG_INFO.append({"endpoint": endpoint, "payload": payload, "status": resp.status_code})
    return f"Error {resp.status_code}: {resp.text}"


async def send_reply(update: Update, text: str) -> None:
    """Send text in chunks to avoid Telegram message limits."""
    for i in range(0, len(text), MAX_MESSAGE_LENGTH):
        await update.message.reply_text(text[i : i + MAX_MESSAGE_LENGTH])


def gather_debug_entries(text: str, state: str = None) -> List[Dict[str, Any]]:
    """Return debug information for a query."""
    if state == "departures":
        query = parser.Query("departure", from_location=text, language="de")
    else:
        query = parser.parse(text)
        if query.type != "trip" or not query.from_location or not query.to_location:
            try:
                query = llm_parser.parse_llm(text)
            except Exception as exc:  # pragma: no cover - network
                logger.error("LLM parse failed: %s", exc)
    entries: List[Dict[str, Any]] = [query.__dict__]
    if query.type == "trip" and query.from_location and query.to_location:
        from_sf = efa_api.stop_finder(query.from_location, language=query.language or "de")
        from_pts = from_sf.get("stopFinder", {}).get("points", [])
        to_sf = efa_api.stop_finder(query.to_location, language=query.language or "de")
        to_pts = to_sf.get("stopFinder", {}).get("points", [])
        if from_pts and to_pts:
            from_p = efa_api.best_point(from_pts)
            to_p = efa_api.best_point(to_pts)
            params = efa_api.build_trip_params(
                from_p.get("name", query.from_location),
                to_p.get("name", query.to_location),
                query.datetime,
                origin_stateless=from_p.get("stateless"),
                destination_stateless=to_p.get("stateless"),
                origin_type=from_p.get("anyType"),
                destination_type=to_p.get("anyType"),
                include=query.include,
                exclude=query.exclude,
                long_distance=query.long_distance,
                language=query.language or "de",
            )
            entries.append(
                {
                    "fromStateless": from_p.get("stateless"),
                    "toStateless": to_p.get("stateless"),
                    "request": {
                        "url": f"{efa_api.BASE_URL}/XML_TRIP_REQUEST2",
                        "params": params,
                    },
                }
            )
    elif query.type == "departure" and query.from_location:
        sf_data = efa_api.stop_finder(query.from_location, language=query.language or "de")
        points = sf_data.get("stopFinder", {}).get("points", [])
        if points:
            point = efa_api.best_point(points)
            params = efa_api.build_departure_params(
                point.get("name", query.from_location),
                stateless=point.get("stateless"),
                language=query.language or "de",
            )
            entries.append(
                {
                    "stateless": point.get("stateless"),
                    "request": {
                        "url": f"{efa_api.BASE_URL}/XML_DM_REQUEST",
                        "params": params,
                    },
                }
            )
    return entries


async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send collected debug information."""
    if not DEBUG_INFO:
        await send_reply(update, "No debug info available")
        return
    await send_reply(update, json.dumps(DEBUG_INFO, indent=2, ensure_ascii=False))
    DEBUG_INFO.clear()


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    text = update.message.text.strip()
    state = context.user_data.get("state")
    if text == "/debug":
        await debug_command(update, context)
        return
    if text == "/search":
        context.user_data["state"] = "search"
        await send_reply(update, "Enter trip query:")
        return
    if text == "/departures":
        context.user_data["state"] = "departures"
        await send_reply(update, "Enter stop name:")
        return
    if text == "/stops":
        context.user_data["state"] = "stops"
        await send_reply(update, "Enter search text:")
        return

    if state == "search":
        context.user_data.pop("state", None)
        if DEBUG:
            entries = gather_debug_entries(text)
            DEBUG_INFO.extend(entries)
            for ent in entries:
                await send_reply(update, json.dumps(ent, indent=2, ensure_ascii=False))
        reply = call_api("/search", {"text": text})
        await send_reply(update, reply)
        return
    if state == "departures":
        context.user_data.pop("state", None)
        if DEBUG:
            entries = gather_debug_entries(text, state="departures")
            DEBUG_INFO.extend(entries)
            for ent in entries:
                await send_reply(update, json.dumps(ent, indent=2, ensure_ascii=False))
        reply = call_api("/departures", {"stop": text})
        await send_reply(update, reply)
        return
    if state == "stops":
        context.user_data.pop("state", None)
        reply = call_api("/stops", {"query": text})
        await send_reply(update, reply)
        return

    # fallback: try /search
    if DEBUG:
        entries = gather_debug_entries(text)
        DEBUG_INFO.extend(entries)
        for ent in entries:
            await send_reply(update, json.dumps(ent, indent=2, ensure_ascii=False))
    reply = call_api("/search", {"text": text})
    await send_reply(update, reply)


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
    application.add_handler(CommandHandler("debug", debug_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    application.run_polling()


def main() -> None:
    """Parse arguments and run the bot."""
    global API_URL
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default=API_URL, help="API endpoint")
    parser.add_argument("--start-server", action="store_true", help="start API with uvicorn")
    parser.add_argument("--token", default=TOKEN, help="Telegram bot token")
    parser.add_argument("--debug", action="store_true", help="enable debug logging")
    args = parser.parse_args()
    API_URL = args.api_url
    if not args.token:
        parser.error("Telegram token not provided")
    if args.debug:
        global DEBUG
        DEBUG = True
        logger.setLevel(logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("telegram.ext").setLevel(logging.INFO)
        logger.debug("Debug mode active")
        logger.debug("Args: %s", args)
    run_bot(args.token, args.start_server)


if __name__ == "__main__":
    main()
