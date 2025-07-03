import os
import sys
import json
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src import cli

@patch('src.cli.format_search_result', return_value='summary')
@patch('src.cli.efa_api.search_efa', return_value={'ok': True})
@patch('src.cli.nlp_parser.parse_query', return_value={'from_stop': 'A', 'to_stop': 'B'})
def test_run_search_text(mock_parse, mock_search, mock_format, capsys):
    cli.run_search('foo', output_format='text')
    captured = capsys.readouterr()
    assert captured.out.strip() == 'summary'
    mock_format.assert_called_once_with({'ok': True})

@patch('src.cli.efa_api.search_efa', return_value={'foo': 'bar'})
@patch('src.cli.nlp_parser.parse_query', return_value={'from_stop': 'A'})
def test_run_search_json(mock_parse, mock_search, capsys):
    cli.run_search('foo', output_format='json', debug=True)
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {'foo': 'bar'}


@patch('src.cli.format_search_result', return_value='legs')
@patch('src.cli.efa_api.search_efa', return_value={'ok': True})
@patch('src.cli.nlp_parser.parse_query', return_value={'from_stop': 'A', 'to_stop': 'B'})
def test_run_search_legs(mock_parse, mock_search, mock_format, capsys):
    cli.run_search('foo', output_format='legs')
    captured = capsys.readouterr()
    assert captured.out.strip() == 'legs'
    mock_format.assert_called_once_with({'ok': True}, legs_only=True)


@patch('src.cli.chatgpt_helper.narrative_trip_summary', return_value='better')
@patch('src.cli.efa_api.search_efa', return_value={'ok': True})
@patch('src.cli.nlp_parser.parse_query')
@patch('src.cli.chatgpt_helper.parse_query_chatgpt', return_value={'from_stop': 'A', 'to_stop': 'B'})
def test_run_search_chatgpt(mock_parse_gpt, mock_parse, mock_search, mock_narrative, capsys):
    cli.run_search('foo', output_format='legs', use_chatgpt=True)
    captured = capsys.readouterr()
    assert captured.out.strip() == 'better'
    mock_parse_gpt.assert_called_once_with('foo')
    mock_parse.assert_not_called()
    mock_narrative.assert_called_once_with({'ok': True})


@patch('src.cli.chatgpt_helper.narrative_trip_summary', return_value='better')
@patch('src.cli.efa_api.search_efa', return_value={'ok': True})
@patch('src.cli.nlp_parser.parse_query', return_value={'from_stop': 'A', 'to_stop': 'B'})
@patch('src.cli.chatgpt_helper.parse_query_chatgpt', return_value={})
def test_run_search_chatgpt_fallback(mock_parse_gpt, mock_parse, mock_search, mock_narrative, capsys):
    cli.run_search('foo', output_format='legs', use_chatgpt=True)
    captured = capsys.readouterr()
    assert captured.out.strip() == 'better'
    mock_parse_gpt.assert_called_once_with('foo')
    mock_parse.assert_called_once_with('foo')
    mock_narrative.assert_called_once_with({'ok': True})
