"""Utility functions for configuring application logging."""

import logging

def setup_logging(debug: bool = False, log_file: str = "app.log") -> None:
    """Configure basic logging for the application."""
    level = logging.DEBUG if debug else logging.INFO
    root_logger = logging.getLogger()
    # Only configure root logger if it hasn't been configured yet
    if not root_logger.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[logging.StreamHandler(), logging.FileHandler(log_file)],
        )
    else:
        root_logger.setLevel(level)

    # Reduce verbosity of third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
