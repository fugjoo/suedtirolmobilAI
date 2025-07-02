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
    cli.run_search('foo', output_format='json')
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {'foo': 'bar'}
