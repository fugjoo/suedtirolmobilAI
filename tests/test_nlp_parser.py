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


def test_parse_query_german_short():
    text = "Meran nach Bozen"
    result = nlp_parser.parse_query(text)
    assert result.get("from_stop") == "Meran"
    assert result.get("to_stop") == "Bozen"


def test_parse_query_two_tokens():
    text = "Meran Bozen"
    result = nlp_parser.parse_query(text)
    assert result.get("from_stop") == "Meran"
    assert result.get("to_stop") == "Bozen"


def test_classify_request_departures():
    text = "Abfahrten Brixen"
    result = nlp_parser.classify_request(text)
    assert result["endpoint"] == "departures"
    assert result["stop"] == text


def test_classify_request_stops():
    text = "Haltestelle Brixen"
    result = nlp_parser.classify_request(text)
    assert result["endpoint"] == "stops"
    assert result["query"] == text


def test_classify_request_search():
    text = "Wie komme ich von Bozen nach Meran?"
    result = nlp_parser.classify_request(text)
    assert result["endpoint"] == "search"
    assert result.get("from_stop") == "Bozen"
    assert result.get("to_stop") == "Meran"


def test_classify_request_single_stop_departures():
    text = "Bozen"
    result = nlp_parser.classify_request(text)
    assert result["endpoint"] == "departures"
    assert result.get("stop") == "Bozen"


def test_classify_request_two_stops_search():
    text = "Bozen Meran"
    result = nlp_parser.classify_request(text)
    assert result["endpoint"] == "search"
    assert result.get("from_stop") == "Bozen"
    assert result.get("to_stop") == "Meran"


def test_classify_request_suffix_departures():
    text = "Neumarkt Busbahnhof"
    result = nlp_parser.classify_request(text)
    assert result["endpoint"] == "departures"
    assert result.get("stop") == text


def test_classify_request_hyphen_search():
    text = "Bozen-Meran"
    result = nlp_parser.classify_request(text)
    assert result["endpoint"] == "search"
    assert result.get("from_stop") == "Bozen"
    assert result.get("to_stop") == "Meran"

