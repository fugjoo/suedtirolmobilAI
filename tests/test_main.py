import os
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.main import app

@patch('src.main.efa_api.search_efa')
@patch('src.main.nlp_parser.parse_query')
def test_search_endpoint(mock_parse_query, mock_search_efa):
    mock_parse_query.return_value = {'from_stop': 'Bozen', 'to_stop': 'Meran'}
    expected_result = {'result': 'ok'}
    mock_search_efa.return_value = expected_result
    client = TestClient(app)
    response = client.post('/search?format=json', json={'text': 'Wie komme ich von Bozen nach Meran?'})
    assert response.status_code == 200
    assert response.json() == expected_result
    mock_parse_query.assert_called_once_with('Wie komme ich von Bozen nach Meran?')
    mock_search_efa.assert_called_once_with({'from_stop': 'Bozen', 'to_stop': 'Meran'})


@patch('src.main.format_search_result', return_value='summary')
@patch('src.main.nlp_parser.detect_language', return_value='de')
@patch('src.main.efa_api.search_efa')
@patch('src.main.nlp_parser.parse_query')
def test_search_endpoint_text(mock_parse_query, mock_search_efa, mock_detect, mock_format):
    mock_parse_query.return_value = {'from_stop': 'A', 'to_stop': 'B'}
    mock_search_efa.return_value = {'dummy': True}
    client = TestClient(app)
    response = client.post('/search?format=text', json={'text': 'foo'})
    assert response.status_code == 200
    assert response.text == 'summary'
    mock_format.assert_called_once_with({'dummy': True}, legs_only=False, lang='de')


@patch('src.main.format_search_result', return_value='legs')
@patch('src.main.nlp_parser.detect_language', return_value='de')
@patch('src.main.efa_api.search_efa')
@patch('src.main.nlp_parser.parse_query')
def test_search_endpoint_default(mock_parse_query, mock_search_efa, mock_detect, mock_format):
    mock_parse_query.return_value = {'from_stop': 'A', 'to_stop': 'B'}
    mock_search_efa.return_value = {'dummy': True}
    client = TestClient(app)
    response = client.post('/search', json={'text': 'foo'})
    assert response.status_code == 200
    assert response.text == 'legs'
    mock_format.assert_called_once_with({'dummy': True}, legs_only=True, lang='de')


@patch('src.main.chatgpt_helper.narrative_trip_summary', return_value='better')
@patch('src.main.nlp_parser.detect_language', return_value='de')
@patch('src.main.efa_api.search_efa')
@patch('src.main.nlp_parser.parse_query')
@patch('src.main.chatgpt_helper.parse_query_chatgpt', return_value={'from_stop': 'A', 'to_stop': 'B'})
def test_search_endpoint_chatgpt(mock_parse_gpt, mock_parse_query, mock_search_efa, mock_detect, mock_narrative):
    mock_search_efa.return_value = {'dummy': True}
    client = TestClient(app)
    response = client.post('/search?chatgpt=true', json={'text': 'foo'})
    assert response.status_code == 200
    assert response.text == 'better'
    mock_parse_gpt.assert_called_once_with('foo')
    mock_parse_query.assert_not_called()
    mock_narrative.assert_called_once_with({'dummy': True}, lang='de')


@patch('src.main.efa_api.search_efa')
@patch('src.main.nlp_parser.parse_query')
@patch('src.main.chatgpt_helper.parse_query_chatgpt', return_value={})
def test_search_endpoint_chatgpt_bad_parse(mock_parse_gpt, mock_parse_query, mock_search_efa):
    client = TestClient(app)
    response = client.post('/search?chatgpt=true', json={'text': 'foo'})
    assert response.status_code == 400
    mock_parse_gpt.assert_called_once_with('foo')
    mock_parse_query.assert_not_called()
    mock_search_efa.assert_not_called()


@patch('src.main.nlp_parser.detect_language', return_value='de')
@patch('src.main.efa_api.dm_request')
def test_departures_endpoint(mock_dm_request, mock_detect):
    expected = {'dm': 'ok'}
    mock_dm_request.return_value = expected
    client = TestClient(app)
    response = client.post('/departures', json={'stop': 'Bozen', 'limit': 5})
    assert response.status_code == 200
    assert response.json() == expected
    mock_dm_request.assert_called_once_with('Bozen', 5, 'de')


@patch('src.main.format_departures_result', return_value='dep')
@patch('src.main.efa_api.dm_request')
def test_departures_endpoint_text(mock_dm_request, mock_format):
    mock_dm_request.return_value = {'ok': True}
    client = TestClient(app)
    response = client.post('/departures?format=text', json={'stop': 'B', 'limit': 1})
    assert response.status_code == 200
    assert response.text == 'dep'
    mock_format.assert_called_once_with({'ok': True}, lang='de')


@patch('src.main.chatgpt_helper.reformat_summary', return_value='better dep')
@patch('src.main.format_departures_result', return_value='dep')
@patch('src.main.efa_api.dm_request')
def test_departures_endpoint_chatgpt(mock_dm_request, mock_format, mock_reformat):
    mock_dm_request.return_value = {'ok': True}
    client = TestClient(app)
    response = client.post('/departures?format=text&chatgpt=true', json={'stop': 'B', 'limit': 1})
    assert response.status_code == 200
    assert response.text == 'better dep'
    mock_format.assert_called_once_with({'ok': True}, lang='de')
    mock_reformat.assert_called_once_with('dep')


@patch('src.main.nlp_parser.detect_language', return_value='de')
@patch('src.main.efa_api.stopfinder_request')
def test_stops_endpoint(mock_stopfinder_request, mock_detect):
    expected = {'stops': []}
    mock_stopfinder_request.return_value = expected
    client = TestClient(app)
    response = client.post('/stops', json={'query': 'Brixen'})
    assert response.status_code == 200
    assert response.json() == expected
    mock_stopfinder_request.assert_called_once_with('Brixen', 'de')


@patch('src.main.nlp_parser.detect_language', return_value='de')
@patch('src.main.format_stops_result', return_value='stops')
@patch('src.main.efa_api.stopfinder_request')
def test_stops_endpoint_text(mock_stopfinder_request, mock_format, mock_detect):
    mock_stopfinder_request.return_value = {'foo': 'bar'}
    client = TestClient(app)
    response = client.post('/stops?format=text', json={'query': 'xyz'})
    assert response.status_code == 200
    assert response.text == 'stops'
    mock_format.assert_called_once_with({'foo': 'bar'}, lang='de')


@patch('src.main.chatgpt_helper.reformat_summary', return_value='better stops')
@patch('src.main.nlp_parser.detect_language', return_value='de')
@patch('src.main.format_stops_result', return_value='stops')
@patch('src.main.efa_api.stopfinder_request')
def test_stops_endpoint_chatgpt(mock_stopfinder_request, mock_format, mock_detect, mock_reformat):
    mock_stopfinder_request.return_value = {'foo': 'bar'}
    client = TestClient(app)
    response = client.post('/stops?format=text&chatgpt=true', json={'query': 'xyz'})
    assert response.status_code == 200
    assert response.text == 'better stops'
    mock_format.assert_called_once_with({'foo': 'bar'}, lang='de')
    mock_reformat.assert_called_once_with('stops')
