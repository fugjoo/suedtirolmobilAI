"""Simple JSON line logger for EFA requests."""

import json
import os
import datetime as dt
import logging
from typing import Any, Dict

LOG_PATH = os.getenv("REQUEST_LOG_FILE", "requests.log")
logger = logging.getLogger(__name__)


def log_entry(entry: Dict[str, Any]) -> None:
    """Append a log entry as JSON line."""
    entry = dict(entry)
    entry.setdefault("timestamp", dt.datetime.utcnow().isoformat())
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")
    except Exception:  # pragma: no cover - file system issues
        logger.exception("Failed to write log entry")
