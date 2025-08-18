"""Project package setup."""

from pathlib import Path
import logging
import os

# Register lightweight stubs for optional third-party libraries.
# Importing this package adds ``anyio``, ``fastapi`` and others to
# ``sys.modules`` so modules can ``import`` them without the real
# dependencies.
from . import stubs  # noqa: F401  # pylint: disable=unused-import

# Configure basic logging.  The log level can be controlled via the
# ``LOG_LEVEL`` environment variable, defaulting to ``WARNING``.
logging.basicConfig(level=os.getenv("LOG_LEVEL", "WARNING").upper())

# ``python-dotenv`` is an optional dependency used during development to
# populate environment variables from a ``.env`` file.  The tests run in a
# minimal environment where the package might not be installed.  Importing it
# unconditionally would therefore raise a ``ModuleNotFoundError`` during test
# collection.  To keep the package optional we attempt to import it and fall
# back to a no-op function if the import fails.
try:  # pragma: no cover - behaviour is trivial
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover
    def load_dotenv(*_args, **_kwargs):  # type: ignore
        """Fallback ``load_dotenv`` when ``python-dotenv`` is missing."""
        return False

_dotenv_path = Path(__file__).resolve().parent.parent / ".env"
if _dotenv_path.exists():
    load_dotenv(_dotenv_path)

