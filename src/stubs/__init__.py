"""Lightweight stand-ins for optional third-party packages.

Importing this package registers minimal modules for ``anyio``, ``fastapi``,
``openai``, ``pydantic`` and ``requests`` so that the project and tests can
import them without the real dependencies being installed.
"""

from importlib import import_module, util
import os
import sys

# ``fastapi`` is only stubbed when the real package is not explicitly
# requested.  This allows the development server to use the actual
# implementation by setting ``USE_REAL_FASTAPI=1``.
_base_stubs = ["openai", "requests"]
if not os.getenv("USE_REAL_FASTAPI"):
    _base_stubs.insert(0, "fastapi")

for _name in _base_stubs:
    _module = import_module(f".{_name}", __name__)
    sys.modules[_name] = _module

# ``anyio`` and ``pydantic`` are only stubbed when the real packages are
# missing, allowing optional dependencies to use their full implementations
# when available.
for _name in ("anyio", "pydantic"):
    if util.find_spec(_name) is None:
        _module = import_module(f".{_name}", __name__)
        sys.modules[_name] = _module
