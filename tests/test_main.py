import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app

@patch('src.main.efa_api.search_efa')
@patch('src.main.nlp_parser.parse_query')
def test_search_endpoint(mock_parse_query, mock_search_efa):
    mock_parse_query.return_value = {'from_stop': 'Bozen', 'to_stop': 'Meran'}
    expected_result = {'result': 'ok'}
    mock_search_efa.return_value = expected_result
    client = TestClient(app)
    response = client.post('/search', json={'text': 'Wie komme ich von Bozen nach Meran?'})
    assert response.status_code == 200
    assert response.json() == expected_result
    mock_parse_query.assert_called_once_with('Wie komme ich von Bozen nach Meran?')
    mock_search_efa.assert_called_once_with({'from_stop': 'Bozen', 'to_stop': 'Meran'})


@patch('src.main.efa_api.dm_request')
def test_departures_endpoint(mock_dm_request):
    expected = {'dm': 'ok'}
    mock_dm_request.return_value = expected
    client = TestClient(app)
    response = client.post('/departures', json={'stop': 'Bozen', 'limit': 5})
    assert response.status_code == 200
    assert response.json() == expected
    mock_dm_request.assert_called_once_with('Bozen', 5)


@patch('src.main.efa_api.stop_finder')
def test_stops_endpoint(mock_stop_finder):
    expected = {'stops': []}
    mock_stop_finder.return_value = expected
    client = TestClient(app)
    response = client.post('/stops', json={'query': 'Brixen'})
    assert response.status_code == 200
    assert response.json() == expected
    mock_stop_finder.assert_called_once_with('Brixen')
