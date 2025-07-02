import logging


def setup_logging(debug: bool = False, log_file: str = "app.log") -> None:
    """Configure basic logging for the application."""
    level = logging.DEBUG if debug else logging.INFO
    # Only configure root logger if it hasn't been configured yet
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[logging.StreamHandler(), logging.FileHandler(log_file)],
        )
    else:
        logging.getLogger().setLevel(level)
