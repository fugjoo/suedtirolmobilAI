import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src import nlp_parser

def test_parse_query_basic():
    text = "Wie komme ich von Bozen nach Meran um 14:30?"
    result = nlp_parser.parse_query(text)
    assert result.get("from_stop") == "Bozen"
    assert result.get("to_stop") == "Meran"
    assert result.get("time") == "14:30"

def test_parse_query_english():
    text = "How do I get from Bolzano to Merano at 14:30?"
    result = nlp_parser.parse_query(text)
    assert result.get("from_stop") == "Bolzano"
    assert result.get("to_stop") == "Merano"
    assert result.get("time") == "14:30"

def test_parse_query_italian():
    text = "Come arrivo da Bolzano a Merano alle 14:30?"
    result = nlp_parser.parse_query(text)
    assert result.get("from_stop") == "Bolzano"
    assert result.get("to_stop") == "Merano"
    assert result.get("time") == "14:30"


def test_parse_query_multiple_tokens():
    text = "from Bozen to Sterzing, Busbahnhof"
    result = nlp_parser.parse_query(text)
    assert result.get("from_stop") == "Bozen"
    assert result.get("to_stop") == "Sterzing, Busbahnhof"

