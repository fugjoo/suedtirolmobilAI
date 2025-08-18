"""Lightweight stand-ins for optional third-party packages.

Importing this package registers minimal modules for ``anyio``, ``fastapi``,
``openai``, ``pydantic`` and ``requests`` so that the project and tests can
import them without the real dependencies being installed.
"""

from importlib import import_module, util
import sys

# Always provide stubs for these modules to avoid pulling in heavy
# dependencies or performing network operations during tests.
for _name in ("fastapi", "openai", "requests"):
    _module = import_module(f".{_name}", __name__)
    sys.modules[_name] = _module

# ``anyio`` and ``pydantic`` are only stubbed when the real packages are
# missing, allowing optional dependencies to use their full implementations
# when available.
for _name in ("anyio", "pydantic"):
    if util.find_spec(_name) is None:
        _module = import_module(f".{_name}", __name__)
        sys.modules[_name] = _module
