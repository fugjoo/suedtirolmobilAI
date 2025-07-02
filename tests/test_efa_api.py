import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch
from src import efa_api

@patch('src.efa_api.requests.get')
def test_search_efa_calls_requests(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'ok': True}
    params = {'from_stop': 'Bozen', 'to_stop': 'Meran', 'time': '08:00'}
    result = efa_api.search_efa(params)

    mock_get.assert_called_once()
    url, kwargs = mock_get.call_args
    assert url[0].endswith('/XML_TRIP_REQUEST2')
    efa_params = kwargs['params']
    assert efa_params['name_origin'] == 'Bozen'
    assert efa_params['name_destination'] == 'Meran'
    assert efa_params['itdTime'] == '08:00'
    assert result == {'ok': True}

