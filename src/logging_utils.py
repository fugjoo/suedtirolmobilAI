import logging
import os
from typing import Optional


def setup_logging(debug: Optional[bool] = None) -> None:
    """Configure basic logging for the application."""
    if debug is None:
        debug = os.environ.get("SM_DEBUG") in {"1", "true", "True"}
    level = logging.DEBUG if debug else logging.INFO
    # Only configure root logger if it hasn't been configured yet
    if not logging.getLogger().handlers:
        logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    else:
        logging.getLogger().setLevel(level)
