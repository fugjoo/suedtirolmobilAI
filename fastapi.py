"""Minimal subset of :mod:`fastapi` for tests.

Only :class:`HTTPException` is provided to mimic the real behaviour used in the
service layer.
"""

from __future__ import annotations


class HTTPException(Exception):
    """Exception carrying an HTTP status code and detail message."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
