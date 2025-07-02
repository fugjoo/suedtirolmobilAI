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
