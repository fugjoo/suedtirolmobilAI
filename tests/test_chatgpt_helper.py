import os
import sys
from unittest.mock import patch, MagicMock
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src import chatgpt_helper


@patch('src.chatgpt_helper.requests.post')
def test_parse_query_chatgpt_parses_json(mock_post):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        'choices': [
            {'message': {'content': '{"from_stop": "A", "to_stop": "B"}'}}
        ]
    }
    mock_post.return_value = mock_resp
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-test'}):
        result = chatgpt_helper.parse_query_chatgpt('dummy query')
    assert result == {'from_stop': 'A', 'to_stop': 'B'}
    mock_post.assert_called_once()


@patch('src.chatgpt_helper.requests.post')
def test_parse_query_chatgpt_invalid_json_returns_empty(mock_post):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        'choices': [
            {'message': {'content': 'not json'}}
        ]
    }
    mock_post.return_value = mock_resp
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-test'}):
        result = chatgpt_helper.parse_query_chatgpt('dummy')
    assert result == {}
    mock_post.assert_called_once()


def test_parse_query_chatgpt_requires_key():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError):
            chatgpt_helper.parse_query_chatgpt('hi')


@patch('src.chatgpt_helper.requests.post')
def test_classify_query_chatgpt_parses_json(mock_post):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        'choices': [
            {'message': {'content': '{"endpoint": "departures", "stop": "Bozen"}'}}
        ]
    }
    mock_post.return_value = mock_resp
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-test'}):
        result = chatgpt_helper.classify_query_chatgpt('foo')
    assert result == {'endpoint': 'departures', 'stop': 'Bozen'}
    mock_post.assert_called_once()


@patch('src.chatgpt_helper.requests.post')
def test_classify_query_chatgpt_invalid_json_returns_empty(mock_post):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        'choices': [
            {'message': {'content': 'not json'}}
        ]
    }
    mock_post.return_value = mock_resp
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-test'}):
        result = chatgpt_helper.classify_query_chatgpt('dummy')
    assert result == {}
    mock_post.assert_called_once()


def test_classify_query_chatgpt_requires_key():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError):
            chatgpt_helper.classify_query_chatgpt('hi')

