"""Simplified type definitions used by :mod:`src.mcp_server`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Tool:
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class TextContent:
    type: str
    text: str
