"""Very simple text parser to detect Fahrplan intents."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedRequest:
    intent: str
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    stop_query: Optional[str] = None
    time: Optional[str] = None


def parse_user_input(text: str) -> ParsedRequest:
    """Parse a short text and return the recognized intent and parameters."""
    text = text.lower()
    if "abfahr" in text:
        # Example: "Abfahrten am Bahnhof Bruneck"
        match = re.search(r"abfahr.*?\b([\w\s]+)", text)
        stop_query = match.group(1).strip() if match else None
        return ParsedRequest(intent="departures", stop_query=stop_query)
    if "nach" in text and "von" in text:
        # Example: "Wann fährt der nächste Bus von Bozen nach Meran?"
        from_match = re.search(r"von\s+([\w\s]+?)\s+nach", text)
        to_match = re.search(r"nach\s+([\w\s]+)", text)
        return ParsedRequest(
            intent="connection",
            from_location=from_match.group(1).strip() if from_match else None,
            to_location=to_match.group(1).strip() if to_match else None,
        )
    # Default to stop search
    return ParsedRequest(intent="stop_search", stop_query=text.strip())
