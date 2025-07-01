import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src import nlp_parser

def test_parse_query_basic():
    text = "Wie komme ich von Bozen nach Meran um 14:30?"
    result = nlp_parser.parse_query(text)
    assert result.get("from_stop") == "Bozen"
    assert result.get("to_stop") == "Meran"
    assert result.get("time") == "14:30"

