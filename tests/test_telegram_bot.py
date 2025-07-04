import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src import telegram_bot


def test_parse_args_default():
    args = telegram_bot.parse_args([])
    assert args.api_url == "http://localhost:8000"
    assert args.chatgpt is False


def test_parse_args_override():
    args = telegram_bot.parse_args(["--api-url", "http://1.2.3.4:8000"])
    assert args.api_url == "http://1.2.3.4:8000"

def test_parse_args_chatgpt():
    args = telegram_bot.parse_args(["--chatgpt"])
    assert args.chatgpt is True
