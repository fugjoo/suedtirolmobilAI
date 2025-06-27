"""Natural language interface for Südtirol's transit system."""

from importlib import import_module

__all__ = ["config", "efa_api", "formatter", "nlp_parser"]


def __getattr__(name: str):
    """Lazily import submodules on first access."""
    if name in __all__:
        return import_module(f"{__name__}.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
