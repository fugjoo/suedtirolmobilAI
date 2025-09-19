import pytest

from suedtirolmobilai.handlers import map_error_response
from suedtirolmobilai.schemas import NormalizedError


def test_error_mapping_unavailable(load_fixture):
    payload = load_fixture("error_response_unavailable.json")
    normalized = map_error_response(payload)
    validated = NormalizedError.model_validate(normalized.model_dump())
    assert validated == normalized
    assert normalized.category == "unavailable"
    assert normalized.message == "Backend temporarily unavailable"
    assert normalized.details == {"httpStatus": 503}


def test_error_mapping_unknown_code(load_fixture):
    payload = load_fixture("error_response_unknown.json")
    normalized = map_error_response(payload)
    assert normalized.category == "unknown"
    assert normalized.message == "An undocumented error occurred"
    assert normalized.details == {"requestId": "abc-123"}


def test_error_mapping_missing_section_raises():
    with pytest.raises(ValueError):
        map_error_response({})
