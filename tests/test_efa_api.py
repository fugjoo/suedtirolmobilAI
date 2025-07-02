import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import patch, MagicMock
from src import efa_api

@patch('src.efa_api.requests.get')
def test_get_stop_code(mock_get):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        'stopFinder': {
            'points': {
                'point': [
                    {'name': 'Bozen Hbf', 'quality': '800', 'stateless': 's1'},
                    {
                        'name': 'Bozen, Stazione',
                        'quality': '990',
                        'stateless': 's2',
                    },
                ]
            }
        }
    }
    mock_get.return_value = resp

    code = efa_api.get_stop_code('Bozen')
    assert code == 's2'
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert kwargs['params']['locationServerActive'] == 1


@patch('src.efa_api.requests.get')
def test_search_efa_calls_requests(mock_get):
    def side_effect(url, params=None, timeout=10):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        if url.endswith('XML_STOPFINDER_REQUEST'):
            mock_resp.json.return_value = {
                'stopFinder': {
                    'points': {
                        'point': {
                            'name': params['name_sf'],
                            'quality': '999',
                            'stateless': params['name_sf'] + '_SL',
                        }
                    }
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
    assert efa_params['name_origin'] == 'Bozen_SL'
    assert efa_params['name_destination'] == 'Meran_SL'
    assert efa_params['itdTime'] == '08:00'
    assert efa_params['locationServerActive'] == 1
    assert efa_params['odvMacro'] == 'true'
    assert result == {'ok': True}


@patch('src.efa_api.get_stop_code', return_value='Bozen')
@patch('src.efa_api.requests.get')
def test_dm_request_calls_requests(mock_get, mock_best):
    mock_get.return_value = MagicMock(status_code=200, json=lambda: {'ok': True})

    result = efa_api.dm_request('Bozen', limit=5)

    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0].endswith('/XML_DM_REQUEST')
    assert kwargs['params']['name_dm'] == 'Bozen'
    assert kwargs['params']['limit'] == 5
    assert kwargs['params']['locationServerActive'] == 1
    assert kwargs['params']['odvMacro'] == 'true'
    assert result == {'ok': True}


@patch('src.efa_api.requests.get')
def test_stopfinder_request_returns_json(mock_get):
    mock_get.return_value = MagicMock(status_code=200, json=lambda: {'stops': []})

    result = efa_api.stopfinder_request('Bruneck')

    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0].endswith('/XML_STOPFINDER_REQUEST')
    assert kwargs['params']['name_sf'] == 'Bruneck'
    assert result == {'stops': []}

