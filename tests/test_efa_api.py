import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch, MagicMock
from src import efa_api

@patch('src.efa_api.requests.get')
def test_get_best_stop_name(mock_get):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        'stopFinder': {
            'points': {
                'point': [
                    {'name': 'Bozen Hbf', 'quality': '800'},
                    {'name': 'Bozen, Stazione', 'quality': '990'},
                ]
            }
        }
    }
    mock_get.return_value = resp

    name = efa_api._get_best_stop_name('Bozen')
    assert name == 'Bozen, Stazione'


@patch('src.efa_api.requests.get')
def test_search_efa_calls_requests(mock_get):
    def side_effect(url, params=None, timeout=10):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        if url.endswith('XML_STOPFINDER_REQUEST'):
            mock_resp.json.return_value = {
                'stopFinder': {
                    'points': {'point': {'name': params['name_sf'], 'quality': '999'}}
                }
            }
        else:
            mock_resp.json.return_value = {'ok': True}
        return mock_resp

    mock_get.side_effect = side_effect

    params = {'from_stop': 'Bozen', 'to_stop': 'Meran', 'time': '08:00'}
    result = efa_api.search_efa(params)

    assert mock_get.call_count == 3
    trip_call = mock_get.call_args_list[-1]
    assert trip_call[0][0].endswith('/XML_TRIP_REQUEST2')
    efa_params = trip_call[1]['params']
    assert efa_params['name_origin'] == 'Bozen'
    assert efa_params['name_destination'] == 'Meran'
    assert efa_params['itdTime'] == '08:00'
    assert result == {'ok': True}

