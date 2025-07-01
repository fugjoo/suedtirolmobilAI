# suedtirolmobilAI

This project provides a small FastAPI service that parses natural language
queries for public transport connections and forwards them to a Mentz-EFA
backend.

## Installation

```bash
pip install -r requirements.txt
# optionally download the German spaCy model
python -m spacy download de_core_news_sm
```

## Running the server

Start the API using `uvicorn`:

```bash
uvicorn src.main:app --reload
```

## Testing

Run the unit tests with `pytest`:

```bash
pytest
```
