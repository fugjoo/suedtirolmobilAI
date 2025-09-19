from suedtirolmobilai.handlers import normalize_stop_finder
from suedtirolmobilai.schemas import StopLocation


def test_stop_finder_results_validate_against_schema(load_fixture):
    payload = load_fixture("stop_finder_success.json")
    results = normalize_stop_finder(payload)

    assert len(results) == 2
    for item in results:
        validated = StopLocation.model_validate(item.model_dump())
        assert validated == item

    assert results[0].is_best_match is True
    assert results[0].match_score == 100
    assert results[1].is_best_match is False


def test_stop_finder_contract_snapshot(load_fixture):
    payload = load_fixture("stop_finder_success.json")
    results = normalize_stop_finder(payload)

    snapshot = [item.model_dump() for item in results]
    assert snapshot == [
        {
            "id": "1001",
            "gid": "de:altoadige:1001",
            "name": "Bolzano, Bahnhof",
            "type": "stop",
            "latitude": 46.498295,
            "longitude": 11.354758,
            "match_score": 100,
            "is_best_match": True,
            "products": ["train", "bus"],
        },
        {
            "id": "1002",
            "gid": "de:altoadige:1002",
            "name": "Bolzano, Waltherplatz",
            "type": "stop",
            "latitude": 46.49892,
            "longitude": 11.35796,
            "match_score": 92,
            "is_best_match": False,
            "products": ["bus"],
        },
    ]
