import json
from pathlib import Path
from typing import Any, Callable, Dict

import pytest


_FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def load_fixture() -> Callable[[str], Dict[str, Any]]:
    def _load(name: str) -> Dict[str, Any]:
        path = _FIXTURE_DIR / name
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    return _load
