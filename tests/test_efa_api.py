import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch
from src import efa_api

@patch('src.efa_api.requests.get')
def test_search_efa_calls_requests(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'ok': True}
    params = {'from': 'Bozen', 'to': 'Meran'}
    result = efa_api.search_efa(params)
    mock_get.assert_called_once()
    assert result == {'ok': True}

