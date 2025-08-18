"""Simple stub of the :mod:`pydantic` API used in tests.

It provides a minimal ``BaseModel`` class supporting field definition through
class annotations, a basic ``__init__`` for attribute assignment and a
``model_json_schema`` method returning a trivial schema representation.
This is sufficient for the tests which only instantiate models and request
JSON schemas for tool metadata.
"""

from __future__ import annotations

from typing import Any, Dict


class BaseModel:
    """Very small drop-in replacement for :class:`pydantic.BaseModel`."""

    def __init__(self, **data: Any) -> None:
        for name, _ in self.__annotations__.items():
            if name in data:
                setattr(self, name, data[name])
            else:
                setattr(self, name, getattr(self.__class__, name, None))

    def model_dump(self) -> Dict[str, Any]:  # pragma: no cover - convenience
        return {name: getattr(self, name) for name in self.__annotations__}

    @classmethod
    def model_json_schema(cls) -> Dict[str, Any]:
        props = {name: {"title": name} for name in cls.__annotations__}
        return {"title": cls.__name__, "type": "object", "properties": props}
