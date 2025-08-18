"""Lightweight subset of the :mod:`requests` API used in the tests.

Only the parts exercised by the service layer are implemented: a ``Request``
class capable of generating a ``prepared`` URL and an ``HTTPError`` exception
class.  This avoids pulling the external dependency while keeping the public
interface required by the code.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from urllib.parse import urlencode


class HTTPError(Exception):
    """Minimal stand-in for :class:`requests.HTTPError`."""


@dataclass
class Request:
    method: str
    url: str
    params: dict | None = None

    def prepare(self) -> SimpleNamespace:
        query = urlencode(self.params or {})
        full_url = f"{self.url}?{query}" if query else self.url
        return SimpleNamespace(url=full_url)
