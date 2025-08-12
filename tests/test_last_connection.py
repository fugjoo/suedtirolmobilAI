import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src import parser, efa_api


@pytest.mark.parametrize("text", [
    "Letzte Verbindung von A nach B",
    "Last connection from A to B",
    "Ultima corsa da A a B",
])
def test_parser_last_connection(text):
    q = parser.parse(text)
    assert q.last_connection is True


def test_build_trip_params_last_connection():
    params = efa_api.build_trip_params("A", "B", last_connection=True)
    assert params.get("calcMode") == "last"
    assert params.get("itdTime") == "23:59"
