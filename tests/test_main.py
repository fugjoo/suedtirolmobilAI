from unittest.mock import patch
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@patch('src.main.efa_api.search_efa')
@patch('src.main.nlp_parser.parse_query')
def test_search_endpoint(mock_parse, mock_search):
    mock_parse.return_value = {'from_stop': 'Bozen', 'to_stop': 'Meran', 'time': '12:00'}
    mock_search.return_value = {'trips': []}
    response = client.post('/search', json={'text': 'Bozen nach Meran um 12:00'})
    assert response.status_code == 200
    assert response.json() == {'trips': []}
    mock_parse.assert_called_once_with('Bozen nach Meran um 12:00')
    mock_search.assert_called_once()

